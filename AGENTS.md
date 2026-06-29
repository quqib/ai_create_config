# AGENTS.md

## Project purpose

Generate `configure` (dict) + `entrance_url` (str) as a `.py` file importable by `main.py` — a DSL config for crawling Chinese government procurement sites. NOT JSON, NOT scraper code. Configs go under `result/{site}/{category}.py`; analysis reports under `analysis/{site}.md`.

## Execution model

`main.py` line 5 does `from result.{site}.{category} import *` to get `configure` + `entrance_url`, then passes both to `NewCommonSpider` (`base.py`). Edit the import line to switch configs. No CLI args. The engine runs list → detail → sub_info pagination.

Spider output: `new_spider.log`, `spider_temp/{config_name}/`, `attachments_temp/` in CWD.

Request modes:
- `"REQUESTS"` — static HTTP via `requests`.
- `"SELENIUM"` — despite the name, launches **Playwright Chromium** (headless), not Selenium. JS-dependent pages only.
- Per-URL Selenium switching: set `checkselenium` in `list` config (`base.py:543,565-568`) — engine checks if any pattern matches the URL and auto-switches mode, so a single config can mix both modes.

Engine auto-generates a random User-Agent at each request (`base.py:548-551`). The UA in config headers serves as a fallback — don't waste effort crafting exact UA strings.

## Directories

- **`config/`** — reference templates (`tianjinshi/`). DO NOT edit or generate into `config/`. Note: template dirs use deep nesting (`config/tianjinshi/tianjingonggongziyuan/{district}/{category}/`), but results must be flat (`result/{site}/{category}.py`).
- **`result/`** — generated configs. Flat per site: `result/{site}/{category}.py`. Files may disappear between sessions; regenerate as needed.
- **`analysis/`** — site reports (`{site}.md`). Must exist before generating. Never skip analysis.
- **`tasks/`** — YAML task files (`hainan.yaml`) consumed by `run_task.md` workflow.
- **`.opencode/skills/crawler-config-basic/`** — skill docs: `writing_manual.md`, `config_schema.md`, `config_rule.md`, `category_rule.md`, `examples/`.

## `fields` must be a **dict**, not a list

The engine iterates with `for field_name, field_cfg in fields_config.items()` at `base.py:1630`. A list with `"name"` keys **will crash at runtime** even though Python import succeeds.

**List fields** (fixed required names): `title`, `url`, `entrance_url`, `publish_time`. `url` = browser address bar URL. `entrance_url` = actual request URL (often same). Both needed. `prepath: True` prepends `configure["host"]` via `urllib.parse.urljoin`.

**Detail fields** (fixed required names): `content`, `title`, `publish_time`, `project_code`.

**Attachment fields** (under `detail.attachment.fields`): field names `url` + `name`.

## DSL quick reference

- Config root: `name`, `host`, `source_site`, `industry`, `notice_type`, `org_id`, `page_url`, `list`, `detail`, `pagination`.
- `list`/`detail`: `mode`, `method`, `headers`, `fields`. Optionally `captcha` (bool), `attachment`.
- Common field options: `type` (`xpath`/`jsonpath`), `value`, `regex`, `format` (`"date"` → YYYYMMdd), `prepath`, `isnull`, `isbalance`/`isclean` (bracket cleaning), `candidate` (fallback), `request` (separate HTTP for field content), `istimestamp`, `ismulti`.
- Detail content XPath: use `textall()` (custom function at `base.py:1648-1698` and again at `base.py:1742-1748+` — extracts all descendant text with block-level tag handling). Do NOT use plain `text()` for content.
- `pagination.page_param`: `current`, `start`, `step`, `offset`, `per_num`, plus exactly one of `count` (jsonpath → total records; engine computes `ceil(count/per_num)`), `total` (direct page count), or `next` (next-page probe).
- `${page_param}` renders as `str(page*step + offset)`.

## M@$ payload syntax (hard-earned)

POST entrance URLs append `M@$param1=val1&param2=val2` to the base URL. Engine splits on `M@$`, runs `parse_qs(unquote(...))` at `base.py:793`:

| Prefix | Behavior |
|--------|----------|
| `@json:` | JSON-decodes the value (e.g. `pn=@json:0` → int `0`). **Required for numeric fields** — plain strings stay strings, many servers reject them. |
| `@plus:` | Restores `+` from spaces |
| none | Value stays string; `true`/`false`/`null` become bool/None |

**Critical**: Numbers are NOT auto-converted. Wrap numeric fields in `@json:` (e.g. `pn=@json:0`, `rn=@json:10`, `cl=@json:200`). Failure causes servers like Hainan to silently return an HTML error page with HTTP 200.

**⚠ Conflict with `writing_manual.md` §4.2**: The manual says "普通参数禁止使用 @json" — this is **incorrect for strict servers**. The `@json:` rule above is verified against Hainan and other real sites. When in doubt, prefer `@json:` for numeric fields.

Keep the DSL raw — `@json:0`, not URL-encoded `%40json%3A0`. The engine URL-decodes at runtime.

The M@$ payload is parsed into a Python dict, then the engine `json.dumps` it for the POST body (`base.py:584`, `isdump` defaults to True at `base.py:535`). Do NOT pre-serialize the body in M@$ format — write it as query-style key=value pairs.

## Header `$exec()` syntax

Headers can use `$exec(python_code)` where code assigns `result`. For computed headers (e.g. dynamic signatures). See `config_schema.md` appendix C.

## API gotchas (verified against real sites)

- **Missing headers → silent HTML error**. Hainan API returns HTML error (HTTP 200, ~2915 bytes) instead of JSON when `Referer` + `Origin` + `User-Agent` + `X-Requested-With` are absent. Always mirror real browser headers.
- **Charset misdirection**. Hainan declares `charset=UTF-8` but sends GB18030 bytes. Engine handles via `apparent_encoding` (`base.py:611`). Manual verification must decode as GB18030.
- **Province is a parameter, not a directory**. `xiaquncode` (e.g. `460200` for 三亚) is an optional POST filter. Do not create per-region configs.

## Verification

Test import + structural soundness (single Windows PowerShell line):

```python
python -c "import sys; sys.path.insert(0, '.'); from result.hainan.caigougonggao import configure, entrance_url; assert 'M@$' in entrance_url and configure['pagination']['enable'] and configure['list']['method'] == 'POST'; print('OK')"
```

Result subdirs use Python 3.3+ namespace packages — no `__init__.py` needed. For batch operations, write a `.py` script file — PowerShell inline Python chokes on nested quote/brace escaping.

## Environment

No `requirements.txt`. Dependencies (from `base.py` imports): `playwright` (+ `playwright install chromium`), `ddddocr`, `opencv-python`, `numpy`, `pycryptodome`, `jsonpath_ng`, `jsonpath`, `minio`, `requests`.

`base.py:575` hardcodes proxy credentials (`j708.kdltps.com:15818`). Only needed for real crawling, not DSL authoring.

## OpenCode workflow

- `.opencode/project.md` — authoritative spec (analyze → generate, no JSON, no skip analysis).
- `run_task.md` — 4-step executor: read YAML → verify analysis → generate → verify completeness.
- Skill `crawler-config-batch` (skill dir: `crawler-config-basic`).
- File reading priority (conflicts resolved by order): `writing_manual.md` > `config_rule.md` > `config_schema.md` > `category_rule.md` > examples.
- `.opencode/prompts/{analyze_site,generate_single,generate_batch}.md` — task templates.

## Naming

- Filename/dir: pinyin or English, lowercase, word segments concatenated (e.g. `caigougonggao.py`, `zhaobiaogonggao.py`).
- Dict values: Chinese readable (kept as-is; `main.py` prints via `json.dumps(ensure_ascii=False)`).
- `result/` structure: flat per site (`result/{site}/{category}.py`), NOT nested by province/city.
