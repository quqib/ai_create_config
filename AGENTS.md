# AGENTS.md

## Purpose
Generate a Python `configure` dict + `entrance_url` string as `result/{site}/{category}.py`. Configs are imported by `main.py`. No JSON, no scraper code.

## Output layout
- `result` is a Python namespace package (PEP 420); no `__init__.py` needed.
- Flat: `result/{site}/{category}.py`. Do NOT create nested province/city directories (prompt examples are misleading).
- `config/` contains reference templates; never edit or generate into it.
- `analysis/` must contain a `{site}.md` analysis report before generation.
- `tasks/` holds task YAML files (e.g. `hainan.yaml`).

## Execution model
- `main.py` imports `from result.{site}.{category} import *`. Edit that line to switch which generated config is used.
- Before generation, an `analysis/{site}.md` report must exist (produced by the analyze step).
- The `run_task.md` prompt orchestrates the full workflow; invoke it via the OpenCode interface.
`main.py` imports `from result.{site}.{category} import *`. Edit that import line to switch configs.

## Skill priority
- Primary DSL and generation rules are defined under `.opencode/skills/crawler-config-basic/` (writing_manual.md, config_rule.md, config_schema.md, category_rule.md, examples/). The prompts in `.opencode/prompts/` orchestrate the workflow.
- Follow the order: `writing_manual.md` → `config_rule.md` → `config_schema.md` → `category_rule.md` → `examples/`.
When generating, consult docs in order: `writing_manual.md` → `config_rule.md` → `config_schema.md` → `category_rule.md` → `examples/`.

## DSL essentials
- `fields` must be a **dict**; a list crashes (`base.py:1630`).
- List fields required: `title`, `url`, `entrance_url`, `publish_time`. Use `prepath:true` to join host.
- Detail fields required: `content`, `title`, `publish_time`, `project_code`.
- Attachment fields: `url`, `name`.
- `@json:` is only for complex structured parameters (arrays/objects) such as `condition`, `time`, etc. Numeric values like `pn`, `rn` should be plain numbers or use `${page_param}` for pagination.
- Keep DSL raw; do **not** URL‑encode `@json:`.
- Header values may use `$exec(python_code)` for dynamic computation.

## API gotchas
- Required request headers: `Referer`, `Origin`, `User-Agent`, `X-Requested-With`. Missing any yields silent HTML error pages.
- Some sites lie about charset (declare UTF‑8 but send GB18030). `base.py` corrects via `resp.apparent_encoding`.
- `xiaquncode` is an optional POST filter, **not** a directory; do not create per‑region configs.

## Engine defaults
- `isdump=True` → POST bodies are JSON‑serialized automatically.
- Random UA generated per request (`base.py:548‑549`); custom UA in config is only a fallback.
- `checkselenium` can be set in `list` or `detail` to auto‑switch to Playwright for matching URLs.
- Proxy is hard‑coded (`base.py:575`); needed only for real crawling.

## Request modes
- `"REQUESTS"` → static `requests` calls.
- `"SELENIUM"` → actually uses Playwright Chromium (headless). Use only when JS is required.
- Set `checkselenium` patterns to trigger Playwright per‑URL.

## Pagination DSL
`pagination.page_param` includes `current`, `start`, `step`, `offset`, `per_num` plus **one** of:
- `count` (jsonpath → total records),
- `total` (direct page count),
- `next` (probe next page).
Use `${page_param}` to insert the calculated page number.

## Content extraction
Use `textall()` for detail `content` fields (custom extractor handling block‑level tags). Avoid plain `text()`.

## Naming & conventions
- Filenames/directories: lowercase pinyin or English concatenated (`caigougonggao.py`).
- Dict values are human‑readable Chinese; `main.py` prints with `json.dumps(..., ensure_ascii=False)`.

## Dependencies (implicit)
`playwright`, `ddddocr`, `opencv-python`, `numpy`, `pycryptodome`, `jsonpath_ng`, `jsonpath`, `minio`, `requests`.

## Verification command
```bash
python -c "import sys; sys.path.insert(0, '.'); from result.yoursite.yourcategory import configure, entrance_url; print('OK')"
```
Ignore `result/__pycache__/` (namespace‑package side‑effect).

## Task YAML required keys
`site.name`, `site.url`, `site.province`, `site.org_id`, `task.mode`, `task.discover_category`, `task.generate_all`, `output.dir`, `rules.captcha`, `rules.api_first`.

## Workflow
1. `run_task.md` reads task YAML, validates analysis, runs generation, checks completeness.
2. `analyze_site.md` extracts navigation, categories, API endpoints.
3. `generate_single.md` / `generate_batch.md` produce config files (flat layout).
4. Config files must be importable Python modules.

## Common pitfalls

- **Running a task**: Use the OpenCode prompt `run_task.md`. It reads a `tasks/*.yaml`, ensures an `analysis/{site}.md` exists, then generates flat Python modules under `result/{site}/` via the `crawler-config-basic` skill.
- **Switching configs**: `main.py` imports the generated module via `from result.{site}.{category} import *`. Edit that single import line to test a different configuration.
- **Verification**: After generation, run:
  ```bash
  python -c "import sys; sys.path.insert(0, '.'); from result.<site>.<category> import configure, entrance_url; print('OK')"
  ```
  to confirm the module imports without errors.
- Using `@json:` on numeric parameters where not needed (e.g., `pn`, `rn`) can produce malformed URLs; use plain numbers or `${page_param}` for pagination.
- Using a list for `fields` → runtime crash.
- Generating nested directories under `result/` → import fails.
- Omitting required headers → silent HTML error.
- Using `text()` instead of `textall()` for content → incomplete extraction.
