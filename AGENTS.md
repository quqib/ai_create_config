# AGENTS.md

## Project purpose

Generate **crawler DSL configurations** (JSON) for Chinese government procurement websites. The deliverable is a config file, NOT runnable Python code or a scraper framework. Per `project.md` / `.opencode/project.md`:

- Prefer REST/JSON APIs over browser automation.
- Output must conform to the DSL schema (`entranceUrl`, `list`, `detail`, `pagination`, `fields`).
- Do not guess endpoints; mark anything uncertain.
- For captcha-gated sites, set `captcha: true` and flag it — do **not** attempt to bypass. The default workflow assumes `captcha=false`.

Generated configs go under `result/{site}/{category}.json` (e.g. `result/anhui/purchase.json`).

## How the system runs

`base.py` defines `NewCommonSpider`, the engine that interprets a DSL config and crawls. It supports two request modes:

- `mode: "REQUESTS"` — static HTTP via `requests`.
- `mode: "SELENIUM"` — despite the name, this launches **Playwright Chromium** (headless), not Selenium. Used for dynamic/JS pages.

`main.py` is the runner. To test a config, **edit the import line** in `main.py`:

```python
from config.chengjiaogonggao import *
```

then `python main.py`. There is no CLI argument — switching configs means editing the source. `main.py` runs a `list` task, then iterates `url_info` into `detail` tasks, then handles `sub_info` pagination.

The spider writes `new_spider.log`, `spider_temp/{config_name}/` (HTML/screenshots), and `attachments_temp/` in the CWD.

## Config files vs. generated DSL

Configs under `config/*.py` are **Python modules** that expose two top-level names consumed by `main.py`:

- `configure` (dict) — the DSL itself.
- `entrance_url` (str) — list-page entrance URL; may contain `${tplSetId}` style placeholders resolved at runtime by captcha/preflight steps.

See `config/chengjiaogonggao.py` as the reference template. The final AI-generated deliverables in `result/` are plain JSON (no Python).

## DSL quick reference (verified from base.py + chengjiaogonggao.py)

- `list` / `detail`: `mode`, `method`, `headers`, `fields`, optional `captcha`, `attachment`.
- `fields` entry types: `xpath`, `jsonpath`. Common keys: `value`, `regex`, `format` (`"date"`), `prepath` (bool, prepend host), `isnull` (bool, allow missing), `isbalance`/`isclean` (bracket cleaning for project codes).
- `captcha.steps`: sequenced sub-requests; each step supports `name`, `url`, `method`, `headers`, `issave`, `response_type` (`json`/`image`/`file`), `fields`, `encrypt`, `check_success`, `check_fail`. Placeholders `${var}` are rendered from the accumulating `ctx`. Image response_type triggers `ddddocr` via `classfy_ocr` (`abc_num` / `math` / `multi_slide` / `block_puzzle`).
- `pagination.page_param`: `current`, `start`, `step`, `per_num`, and `count` (a jsonpath+regex that extracts total pages from the response).
- `attachment`: `enable`, `mode`, `isverify`, `fields` (`url`/`name`), optional `candidate` fallback selectors, and `encrypt` transforms (`replace` most common; also `aes`/`rsa`/`md5`/`hmac`/`base64`/`url`/`truncate`).
- URL payloads: POST entrance URLs may append `M@$param1=val1&param2=val2`; `_request` parses it via `parse_entrance_url_payload`. Values prefixed `@json:` are JSON-decoded; `@plus:` restores `+` from spaces.
- Headers may contain `$exec(<python>)` — executed server-side, must assign `result` or the header key. Use sparingly and with care.

## Environment / setup

No `requirements.txt` and no tests exist. Heavy dependencies (from `base.py` imports) you must install manually:

- `playwright` (run `playwright install chromium` after pip install)
- `ddddocr`, `opencv-python`, `numpy`
- `pycryptodome` (imported as `Crypto`)
- `jsonpath_ng`, `jsonpath`, `minio`, `requests`

**`base.py` has hardcoded upstream proxy credentials** (`j708.kdltps.com:15818`, user `t14306903178173`) baked into `_request`. Real crawling requires that proxy account to be valid; for local DSL authoring/analysis you generally don't need to run the spider.

## OpenCode workflow in this repo

- `.opencode/project.md` is the long-form spec; `.opencode/prompts/{analyze_site,generate_single,generate_batch}.md` are the task templates.
- Skill `crawler-config-batch` (`.opencode/skills/crawler-config-basic/SKILL.md`) drives multi-category generation. Note the directory is named `crawler-config-basic` but the skill `name:` frontmatter is `crawler-config-batch`; invoke it via the `crawler-config-batch` skill name.
- `a.md` at root is a generic web-scraping note, not project-specific — don't treat it as authoritative for DSL rules.

## Conventions to keep

- Output DSL JSON with `ensure_ascii=False` (Chinese must remain readable, as `main.py` does when printing `configure`).
- Keep `source_site`, `org_id`, `notice_type`, `industry`, `host`, `page_url` populated in each config — the engine checks `config` + `entrance_url` + `source_site` are present or the run aborts (`base.py:154`).
- When unsure whether a page needs JS, set `mode: "REQUESTS"` first and only fall back to `"SELENIUM"` if the static response lacks the data.
