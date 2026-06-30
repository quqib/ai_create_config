# AI 爬虫配置生成规范（v2.0）

本规范用于指导 AI 基于真实网站请求生成可被 Python 爬虫框架直接 import 的配置文件（.py）。

最终输出必须为 .py 文件，不得输出解释内容。

----------------------------------------

# 0. 核心原则（最高优先级）

0.1 只允许真实还原，禁止推断

AI 只能基于真实数据源：
- 浏览器 Network 请求（优先）
- 页面源码
- API 返回
- examples 配置

禁止：
- 猜测接口功能
- 推断参数含义
- 修改 URL 结构
- 添加不存在参数
- 根据经验补全接口

----------------------------------------

# 1. URL DSL 规则

- M@$：POST 参数分隔符
- @json:：JSON 类型标识或者列表类型标识

# 1.1 DSL不可解析规则（必须新增）

M@$ 与 @json: 必须作为“不可解析字符串处理”

禁止：

- decode
- encode
- URL重写
- 拆分参数结构

必须保持原始字符串结构

----------------------------------------

# 2. M@$ 规则

2.1 定义

URLM@$key=value&key2=value2

表示：
- URL + POST body

2.2 强规则

✔ 必须保留 M@$

❌ 禁止：
- 删除 M@$
- 改接口名
- 修改 URL

2.3 示例

正确：
/api/listM@$page=0&size=10

错误：
/api/list

----------------------------------------

# 3. @json 规则

仅 JSON 才能用：

condition=@json:[{"field":"name"}]

禁止：
page=@json:1
size=@json:10

----------------------------------------

# 4. entrance_url

必须是：

- 第一页真实请求
- 完整参数
- 完整 DSL
**示例（海南政府采购 采购公告）**：

```python
entrance_url = "https://ggzy.hainan.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNewM@$pn=0&rn=10&cnum=001&fields=title&sort=@json:{\"webdate\":\"0\"}&condition=@json:[{\"fieldName\":\"categorynum\",\"equal\":\"003002002\",\"isLike\":true,\"likeType\":2}]&time=@json:[{\"fieldName\":\"webdate\",\"startTime\":\"1970-01-01 00:00:00\",\"endTime\":\"2999-12-31 23:59:59\"}]"
```

禁止任何修改

**注意**：对数组或对象等复杂参数，如 `condition`、`time`、`sort`，使用 `@json:` 前缀，并保持原始 JSON，不进行 URL 编码。数值字段（如 `pn`、`rn`）不需要 `@json:`。

----------------------------------------

# 5. pagination 规则

# 5.1 URL结构锁定规则（关键补充）

pagination.url 必须满足：

- URL path 完全一致
- 参数 key 完全一致
- 参数数量完全一致
- 仅 value 允许变化

---

❌ 错误：

/list?page=1
/listPage?page=2

✔ 正确：

https://ggzy.hainan.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNewM@$pn=${page_param}&rn=10&cnum=001&fields=title&sort=@json:{\"webdate\":\"0\"}&condition=@json:[{\"fieldName\":\"categorynum\",\"equal\":\"003002002\",\"isLike\":true,\"likeType\":2}]&time=@json:[{\"fieldName\":\"webdate\",\"startTime\":\"1970-01-01 00:00:00\",\"endTime\":\"2999-12-31 23:59:59\"}]

必须满足：

- 同接口
- 同 pagination.url必须与entrance_url保持一致,只有value差异，没有key差异
- 同参数结构
- 同参数数量

只允许改分页字段：

page / pn / offset / cursor

----------------------------------------

# 6. page_param

# 6.1 分页字段识别规则（必须新增）

分页字段必须通过“请求差异”判断，而不是字段名判断

判断标准：

1. 在 page=1 vs page=2 请求中发生变化
2. 其他参数完全一致
3. 仅 value 变化

---

❌ 禁止：

- 根据字段名判断 page / pn / offset
- 根据经验推断分页逻辑

✔ 唯一标准：

diff 变化字段 = 分页字段

必须从真实请求差异得出

禁止推测 step / start

----------------------------------------

# 7. list 规则

优先级：

API > XHR > HTML > Selenium

只负责数据获取

----------------------------------------

# 8. detail 规则

优先级：

JSON > API字段 > HTML > XPath

禁止：

- /html/body
- //div[1]

推荐：

//div[@class="xxx"]

确保其唯一性。

----------------------------------------

# 9. examples

只能学习结构

禁止复制任何真实数据

----------------------------------------

# 10. 输出规则

最终只能输出：

Python .py 文件

禁止：
- Markdown
- JSON
- 解释