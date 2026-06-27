# SITE ANALYSIS (STRUCTURE EXTRACTION)

---

## INPUT

website:
{{website}}

---

## OUTPUT MODE

仅输出结构信息（禁止 DSL / Python / JSON）

输出必须用于 generate_single.md

---

## ANALYSIS TARGET

必须提取：

### 1. 页面结构
- list page
- detail page
- category page

---

### 2. 数据来源
判断：
- REST API
- JSON API
- HTML
- JS rendering (only detect, not execute)

---

### 3. 列表规则
- URL
- method
- params
- headers
- pagination mode

---

### 4. 详情规则
- detail URL pattern
- content selector (xpath / css)
- fields mapping clues

---

### 5. 分类信息
- name
- code
- url

---

### 6. CAPTCHA检测
- 是否存在验证码
- 类型（image / slider / login）

---

## OUTPUT FORMAT（关键）

输出必须是**结构化文本（非JSON）**，例如：

LIST_URL:
DETAIL_URL:
PAGINATION:
FIELDS_HINT:
API_HINT:
CAPTCHA:

---

## OUTPUT RULE

禁止：

- JSON
- Python
- DSL
- 解释性段落

---

## SAVE RULE

保存到：

analysis/{{site}}.txt