# 网站采集配置规范（机器可读版）

## 1. 根节点（Root）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 网站栏目标识，格式：`网站名-导航栏路径`，与配置记录表 `review_name` 一致 |
| `host` | string | ✅ | 网站域名，如 `XXX.XX.cn` |
| `source_site` | string | ✅ | 来源网站名称，与组织配置表 `org_name` 一致 |
| `industry` | string | ✅ | 业务类型，直接取自网站（如 `政府采购`、`工程建设`） |
| `notice_type` | string | ✅ | 公告类型，直接取自网站（如 `招标计划`、`招标公告`） |
| `is_proxy` | integer | 可选 | 是否使用代理：`1` 使用，`0` 不使用，默认 `1` |
| `list` | object | ✅ | 列表页提取配置（见第2节） |
| `detail` | object | ✅ | 详情页提取配置（见第3节） |
| `pagination` | object | ✅ | 翻页配置（见第4节） |

---

## 2. 列表配置（`list`）

### 2.1 基础请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | ✅ | 请求模式：`REQUESTS`（静态）或 `SELENIUM`（模拟浏览器） |
| `method` | string | ✅ | HTTP方法：`GET` / `POST` |
| `isdump` | boolean | 可选 | POST负载是否转为JSON字符串，默认 `True`（不配置即为True） |
| `isverify` | boolean | 可选 | 是否关闭SSL证书验证，默认 `False`（不关闭） |
| `isredirect` | boolean | 可选 | 是否自动跟随重定向，默认 `True`（可重定向） |
| `formdata` | list | 可选 | 存在 `xxxx` 字段时需使用 `files` 参数请求 |
| `page` | object | 可选 | 若列表请求方法改变且不返回页码，增加此请求获取页码（结构同本表） |
| `decrypt` | list | 可选 | 按顺序对请求结果进行解密处理（见附录A） |
| `encrypt` | list | 可选 | 按顺序对请求结果进行加密处理（见附录B） |
| `headers` | object | 可选 | 请求头键值对，支持 `$exec(...)` 自定义加密（见附录C） |

### 2.2 字段提取（`fields`）

每个字段为对象，键名固定（可增删，需同步）。通用属性：

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | ✅ | 提取方式：`xpath` / `jsonpath` / `regex` |
| `value` | string | ✅ | 提取表达式 |
| `regex` | string | 可选 | 提取结果后进一步正则匹配，匹配不到则返回原值 |
| `jsonpath` | string | 可选 | 提取结果后进一步jsonpath提取 |
| `decrypt` | list | 可选 | 同2.1中的解密 |
| `encrypt` | list | 可选 | 同2.1中的加密 |
| `base` | string | 可选 | URL补全前缀，以 `/` 结尾，与提取值拼接（先过滤开头的 `.` 或 `/`） |
| `replace` | string | 可选 | 替换提取值中的 `${变量}`（如 `${url}`），配合 `extra` 使用 |
| `extra` | object | 可选 | 额外字段提取，供 `replace` 使用 |
| `isclean` | boolean | 可选 | 是否清除空格 |
| `isbalance` | boolean | 可选 | 是否检测括号对称性，去除第一个不对称括号及后续内容 |
| `isnull` | boolean | 可选 | 是否允许该字段为空 |
| `format` | string | 可选 | 值 `date` 表示转换为 `YYYYMMdd` 格式 |
| `prepath` | boolean | 可选 | 使用 `urllib.parse.urljoin` 补全链接（处理顺序：base第一，prepath最后） |

**预定义字段名（不可变）：**

| 字段名 | 是否必填 | 说明 |
|--------|----------|------|
| `title` | ✅ | 公告标题 |
| `url` | ✅ | 公告详情链接（浏览器地址栏URL） |
| `entrance_url` | ✅ | 列表数据请求入口URL，表示首次获取公告列表数据的真实请求地址，通常对应第一页请求，不是详情页URL |
| `publish_time` | ✅ | 发文时间，需转为 `YYYYMMdd` |
| `project_code` | 可选 | 项目编号 |
| `industry` | 可选 | 业务类型（若列表有） |
| `notice_type` | 可选 | 公告类型（若列表有） |

---

## 3. 详情配置（`detail`）

### 3.1 基础参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string | ✅ | 同 `list.mode` |
| `method` | string | ✅ | 同 `list.method` |
| `checkselenium` | list | 可选 | URL包含某字符串时启用SELENIUM（如跳转外站） |
| `headers` | object | 可选 | 同 `list.headers`，支持 `$exec` |
| `404` | string | 可选 | 页面包含此内容则判定为404 |
| `iframe` | list | 可选 | 详情在iframe中，按顺序给出xpath表达式（多层嵌套） |

### 3.2 详情字段提取（`detail.fields`）

字段名及规则同 `list.fields`，额外增加：

| 属性 | 类型 | 说明 |
|------|------|------|
| `request` | object | 若正文需单独请求，配置同 `list` 基础参数，响应内容作为 `content` |
| `candidate` | object | 候选提取方式（当原解析失效或进入其他站点时启用） |
| `istimestamp` | boolean | 提取结果为时间戳，需转为时间字符串 |
| `ismulti` | boolean | 提取结果按其他字段数量生成列表（用于多附件等） |

**预定义字段名（不可变）：**

| 字段名 | 是否必填 | 说明 |
|--------|----------|------|
| `content` | ✅ | 详情正文内容 |
| `title` | ✅ | 标题（详情页可能覆盖列表标题） |
| `publish_time` | ✅ | 发文时间 |
| `project_code` | 可选 | 项目编号 |
| `notice_type` | 可选 | 公告类型 |

### 3.3 附件配置（`detail.attachment`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enable` | boolean | ✅ | 是否下载附件 |
| `mode` | string | 可选 | 附件请求模式（默认同详情） |
| `headers` | object | 可选 | 附件请求头 |
| `iframe` | object | 可选 | 提取附件所在iframe的URL，字段规则同 `fields` |
| `click` | object | 可选 | 若需点击获取附件URL/文件名，配置xpath（此时 `mode` 需为 `SELENIUM`） |
| `attach` | object | 可选 | 独立请求获取附件列表（见3.4） |
| `captcha` | object | 可选 | 验证码处理配置（见3.5） |
| `fields` | object | 可选 | 附件字段提取（见3.6） |

### 3.4 独立附件请求（`detail.attachment.attach`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | 请求链接，可含 `${xxxx}` 变量（从详情字段替换） |
| `mode` | string | ✅ | 同 `list.mode` |
| `method` | string | ✅ | HTTP方法 |
| `headers` | object | 可选 | 请求头 |
| `captcha` | object | 可选 | 同3.5 |
| `fields` | object | 可选 | 从详情结果中提取变量值，供 `url` 替换 |

### 3.5 验证码配置（`captcha`）

通用结构（可用于 `list`、`detail`、`attachment`）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enable` | boolean | 可选 | 是否启用，默认 `True` |
| `startcheck` | string | 可选 | 检测URL或响应是否包含此内容，若存在则进入验证码流程 |
| `steps` | list | ✅ | 按顺序执行的步骤列表（每个步骤对象见下） |

**步骤对象（step）：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 步骤名称（如 `init_page`、`get_image`、`get_file`） |
| `method` | string | ✅ | HTTP方法 |
| `url` | string | ✅ | 请求URL，支持 `${变量}` 替换（`list_url`、`captcha_code`、`img_str`、`small_img_str`、`y_pos`、`img_height`、`img_width` 为内置变量） |
| `issave` | boolean | 可选 | 是否固证（默认仅list/detail/attach获取结果时固证） |
| `headers` | object | 可选 | 请求头，支持 `${变量}` |
| `fields` | object | 可选 | 提取响应中的字段（如 `verificationCodeGuid`），供后续替换 |
| `respheaders` | list | 可选 | 需提取的响应头参数名列表 |
| `response_type` | string | 可选 | 响应类型：`image`、`base64`、`json`、`file`、`list` |
| `captcha_config` | object | 可选 | 验证码识别配置（见下） |
| `check_success` | string | 可选 | 检测响应体包含此内容表示验证成功 |
| `check_fail` | string | 可选 | 检测响应体包含此内容表示验证失败 |
| `isredirect` | boolean | 可选 | 是否跟随重定向 |

**`captcha_config` 字段：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | ✅ | 验证码类型：`abc_num`（字母数字）、`math`（数值计算）、`multi_slide`（缺口滑块，自动Y）、`block_puzzle`（缺口滑块，自定义Y） |
| `length` | integer | 可选 | 验证码长度（如4） |
| `iscase` | boolean | 可选 | 是否区分大小写（默认False） |

### 3.6 附件字段提取（`detail.attachment.fields`）

预定义字段名：

| 字段名 | 必填 | 说明 |
|--------|------|------|
| `url` | ✅ | 附件下载链接 |
| `name` | ✅ | 附件名称 |
| `size` | 可选 | 附件大小（字节），若大于阈值则不下载 |

字段属性同 `list.fields`，额外：

| 属性 | 类型 | 说明 |
|------|------|------|
| `ifelse` | list | 条件生成URL：`[条件, 真URL, 假URL]` 或 `[[条件1, URL1], [条件2, URL2], ..., 默认URL]` |
| `ishtml` | boolean | 下载的文件为HTML（若真） |

---

## 4. 翻页配置（`pagination`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enable` | boolean | ✅ | 是否启用翻页 |
| `url` | string | ✅ | 翻页URL模板，含 `${page_param}`（页码变量），可含 `${starttime}` / `${endtime}`（时间查询）和 `${__VIEWSTATE}` 等额外变量 |
| `headers` | object | 可选 | 翻页请求头 |
| `max_page` | integer | 可选 | 最大翻页数（不限制则不写） |
| `extra` | object | 可选 | 提取翻页URL中额外变量（如 `__VIEWSTATE`），字段规则同 `list.fields` |
| `page_param` | object | ✅ | 页码参数配置（见下） |

### 4.1 页码参数（`page_param`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `current` | integer | ✅ | 当前URL中的页码数（首页） |
| `start` | integer | ✅ | 首页页码数 |
| `step` | integer | ✅ | 翻页步长（默认1） |
| `offset` | integer | 可选 | 多步长起始偏移量 |
| `total` | object | 条件 | 总页码数提取（`type` + `value`），与 `count`/`next` 至少一个存在 |
| `count` | object | 条件 | 总记录数提取，与 `total`/`next` 至少一个存在 |
| `next` | object | 条件 | 下一页链接提取（存在则继续），与 `total`/`count` 至少一个存在 |
| `per_num` | integer | 可选 | 每页记录数 |

---

## 附录A：解密类型（`decrypt`）

按顺序处理，每个元素为对象，`type` 为必填，其他为参数：

| type | 参数 | 说明 |
|------|------|------|
| `Base64` | `encode`（默认utf-8） | Base64解码 |
| `URL` | 无 | URL解码 |
| `REPLACE` | `origin`, `dest` | 字符串替换（正则） |
| `TRUNCATE` | `start`, `end` | 截断（含start不含end） |
| `AES` | `key`, `mode`, `padding`, `iv` | AES解密 |
| `RSA` | `pri_key`, `adding` | RSA私钥解密 |

## 附录B：加密类型（`encrypt`）

| type | 参数 | 说明 |
|------|------|------|
| `MD5` | `salt` | MD5加密 |
| `SHA` | `algorithm`（sha1/sha256/sha512）, `salt` | SHA系列 |
| `HMAC-SHA256` | `key` | HMAC带密钥加密 |
| `Base64` | `encode`（默认utf-8） | Base64编码 |
| `URL` | 无 | URL编码 |
| `REPLACE` | `origin`, `dest` | 字符串替换 |
| `TRUNCATE` | `start`, `end` | 截断 |
| `AES` | `key`, `mode`, `padding`, `iv` | AES加密 |
| `RSA` | `pub_key`, `adding` | RSA公钥加密 |

## 附录C：自定义请求头加密（`$exec`）

在 `headers` 中，值可写为 `$exec(python代码)`，代码需定义变量 `result` 作为返回值。代码中可使用 `${变量名}` 引用之前 `$exec` 的结果或其他字段。示例：

```python
$exec(import base64\nfrom datetime import datetime\nnow = datetime.now()\nformatted_time = now.strftime(\"%Y-%m-%d %H:%M:%S\")\nfirst_encode = base64.b64encode(formatted_time.encode('utf-8')).decode('utf-8')\nresult = base64.b64encode(first_encode.encode('utf-8')).decode('utf-8'))