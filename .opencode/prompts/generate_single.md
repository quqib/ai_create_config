# PYTHON DSL GENERATION (SINGLE SITE)

---

## INPUT

website:
{{website}}

category:
{{category}}

analysis:
{{analysis}}

---

## OBJECTIVE

生成可执行 Python DSL 配置文件

---

## OUTPUT FORMAT（必须严格遵守）

必须生成：

result/{{site}}/{{category}}.py

---

## PYTHON DSL STRUCTURE（强制）

必须生成如下结构：

```python
configure = {
    "name": "",
    "site": "",
    "entranceUrl": "",

    "list": {
        "url": "",
        "method": "GET",
        "params": {},
        "headers": {},
        "mode": "REQUESTS"   # or SELENIUM
    },

    "detail": {
        "url_rule": "",
        "fields": {
            "title": "",
            "publish_time": "",
            "content": "",
            "source_url": ""
        }
    },

    "pagination": {
        "type": "page|offset|cursor",
        "page_param": "",
        "size_param": ""
    },

    "captcha": {
        "enabled": false,
        "type": ""
    },

    "unknown": false
}