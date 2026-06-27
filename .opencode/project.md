# AI CRAWLER CONFIG GENERATION SYSTEM

---

## SYSTEM GOAL

将政府采购网站自动转换为：

👉 Python DSL crawler configuration

---

## PIPELINE

必须严格执行：

1. analyze_site
2. generate_single
3. generate_batch (optional)

---

## OUTPUT RULE（核心）

所有结果必须写入：

result/

格式必须是：

.py 文件（Python DSL）

---

## STRICT RULES

### ❌ 禁止

- 输出 JSON DSL
- 输出解释性文本
- 输出HTML解析代码
- 推测API接口
- 跳过分析步骤

---

### ✔ 必须

- 优先 API
- 不存在 API 才 HTML
- 必须生成 pagination
- 必须生成 fields
- 必须检测 captcha

---

## FILE SYSTEM RULE

所有 skill 必须写入文件：

result/{{site}}/{{category}}.py

---

## MODE RULE

list mode：

- REQUESTS 优先
- SELENIUM 仅 fallback

---

## CAPTURE RULE

captcha = true 时：

必须停止 DSL 生成