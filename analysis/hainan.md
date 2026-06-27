# 海南省公共资源交易服务平台 - 网站分析报告

## 1. 网站概况

- 站点名称：海南省公共资源交易服务平台
- 域名：`https://ggzy.hainan.gov.cn/`
- SiteIDCode：4600000022
- 入口页：`/ggzyjy/jyxx/jyxx_list.html`（交易信息，栏目 `cms_003`，categorynum `003`）
- 编码：页面声明 UTF-8，但 API 响应为 **GBK/GB2312** 编码（需注意 `apparent_encoding`，参考引擎 `base.py` 中 `resp.encoding = resp.apparent_encoding or "utf-8"`）。
- 验证码：本次分析入口及详情均**未发现验证码/登录/滑块**。`captcha=false`。

## 2. 网站结构

- 首页：`/ggzyjy/`
- 栏目树：左侧 `.column-second` 二级栏目 + `.column-third` 三级栏目，部分四级（框架协议采购）。
- 列表页：`jyxx_list.html` 类页面，**静态 HTML 为空壳**，列表数据由 JS（`jyxx_list_fullsearch.js`）调用全文检索 API 异步渲染（Mustache 模板 `#info-item` 注入 `#info-list`）。**必须使用 API，不能用 HTML 解析列表。**
- 详情页：`/jyxx/{cat...}/{yyyyMMdd}/{infoid}.html`，正文服务端渲染，可直接 HTML 解析。

### 栏目三级路径规则

URL 形如 `/ggzyjy/jyxx/{二级6位}/{三级9位}/jyxx_list.html`，例如：
- 政府采购 采购公告：`/ggzyjy/jyxx/003002/003002002/jyxx_list.html`（categorynum=`003002002`）
- 工程建设 招标公告：`/ggzyjy/jyxx/003001/003001002/jyxx_list.html`（categorynum=`003001002`）
- 框架协议采购有四级：`/ggzyjy/jyxx/003002/003002010/003002010001/jyxx_list.html`（categorynum=`003002010001`）

## 3. 数据来源 —— REST API（已实测验证）

列表页**有 REST API**，POST + JSON 请求体，全文检索引擎。

- API URL：`https://ggzy.hainan.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNew`
  - 来源：`/ggzyjy/js/common.js` 中 `var fullsearchUrl = "/inteligentsearch/rest/esinteligentsearch/getFullTextDataNew";`
- Method：`POST`
- Content-Type：`application/json`
- 请求体关键字段（来自 `jyxx_list_fullsearch.js`）：

```json
{
  "token": "",
  "pn": 0,            // 起始行偏移 = pageIndex * pageSize（0 基）
  "rn": 10,           // 每页条数
  "sdt": "", "edt": "",
  "wd": " ",          // 关键词（空格代表全部，需 encodeURIComponent）
  "inc_wd": "", "exc_wd": "",
  "fields": "title",
  "cnum": "001",
  "sort": "{\"webdate\":\"0\"}",   // 0=降序
  "ssort": "title",
  "cl": 200,          // content 截断长度
  "terminal": "",
  "condition": [
    {
      "fieldName": "categorynum",
      "equal": "003002002",     // ★ 三级栏目号，likeType=2（前缀匹配），isLike=true
      "notEqual": null, "equalList": null, "notEqualList": null,
      "isLike": true, "likeType": 2
    }
  ],
  "time": [
    {"fieldName":"webdate","startTime":"1970-01-01 00:00:00","endTime":"2999-12-31 23:59:59"}
  ],
  "highlights": "title",
  "statistics": null, "unionCondition": null,
  "accuracy": "", "noParticiple": "1",
  "searchRange": [],
  "isBusiness": "1"
}
```

### 实测响应结构（categorynum=003002002 验证通过）

```json
{
  "result": {
    "totalcount": 33572,
    "records": [
      {
        "titlenew": "公告标题",
        "title": "公告标题",
        "infoid": "8a1d1abc9ef2af7a019f0418728b30cb",
        "linkurl": "/jyxx/003002/003002002/20260626/8a1d1abc9ef2af7a019f0418728b30cb.html",
        "webdate": "2026-06-26 21:27:10",
        "infodate": "2026-06-26 21:27:14",
        "xiaquncode": "460000",
        "xiaquname": "海南省 省中心",
        "zhuanzai": "海南省政府网",        // 信息来源
        "categorynum": "003002002",
        "categoryname": "采购公告",
        "content": "正文截断片段..."        // cl=200 截断，不可用于详情正文
      }
    ],
    "categorys": [{"categorynum":"001","count":"33572","categoryname":"项目信息"}],
    "maxScore": 5.0, "scorllId": "...", "executetime": "0.014"
  }
}
```

要点：
- `totalcount` 直接给出总条数 → 可推断总页数 = ceil(totalcount / rn)。
- `linkurl` 以 `/` 开头，需前缀拼接 host `https://ggzy.hainan.gov.cn`（引擎 `prepath:true`）。
- `webdate` 取前 10 位即日期；`infodate` 为入库时间，列表页用 `webdate`。
- `content` 字段被截断，**详情正文必须取详情页**，不能依赖 API 的 content。

## 4. 分类清单（categorynum → 名称 → 入口 URL）

二级 / 三级栏目（含四级框架协议）。URL 相对根路径 `/ggzyjy`。

### 003001 工程建设
| categorynum | 名称 | 入口 |
|---|---|---|
| 003001001 | 招标计划 | /ggzyjy/jyxx/003001/003001001/jyxx_list.html |
| 003001002 | 招标公告 | /ggzyjy/jyxx/003001/003001002/jyxx_list.html |
| 003001003 | 资格预审公告 | /ggzyjy/jyxx/003001/003001003/jyxx_list.html |
| 003001004 | 变更公告 | /ggzyjy/jyxx/003001/003001004/jyxx_list.html |
| 003001005 | 中标候选人公示 | /ggzyjy/jyxx/003001/003001005/jyxx_list.html |
| 003001006 | 中标公告 | /ggzyjy/jyxx/003001/003001006/jyxx_list.html |
| 003001007 | 异常公告 | /ggzyjy/jyxx/003001/003001007/jyxx_list.html |

### 003002 政府采购
| categorynum | 名称 | 入口 |
|---|---|---|
| 003002002 | 采购公告 | /ggzyjy/jyxx/003002/003002002/jyxx_list.html |
| 003002003 | 变更公告 | /ggzyjy/jyxx/003002/003002003/jyxx_list.html |
| 003002004 | 采购结果公告 | /ggzyjy/jyxx/003002/003002004/jyxx_list.html |
| 003002005 | 合同公示 | /ggzyjy/jyxx/003002/003002005/jyxx_list.html |
| 003002006 | 异常公告 | /ggzyjy/jyxx/003002/003002006/jyxx_list.html |
| 003002007 | 意向公开 | /ggzyjy/jyxx/003002/003002007/jyxx_list.html |
| 003002008 | 单一来源公示 | /ggzyjy/jyxx/003002/003002008/jyxx_list.html |
| 003002009 | 履约验收公示 | /ggzyjy/jyxx/003002/003002009/jyxx_list.html |
| 003002010 | 框架协议采购（二级，含四级） | /ggzyjy/jyxx/003002/003002010/jyxx_list.html |

#### 003002010 框架协议采购（四级）
| categorynum | 名称 | 入口 |
|---|---|---|
| 003002010001 | 征集公告 | /ggzyjy/jyxx/003002/003002010/003002010001/jyxx_list.html |
| 003002010002 | 入围结果公告 | /ggzyjy/jyxx/003002/003002010/003002010002/jyxx_list.html |
| 003002010003 | 终止公告 | /ggzyjy/jyxx/003002/003002010/003002010003/jyxx_list.html |
| 003002010004 | 供应商退出框架协议公告 | /ggzyjy/jyxx/003002/003002010/003002010004/jyxx_list.html |
| 003002010005 | 采购公告 | /ggzyjy/jyxx/003002/003002010/003002010005/jyxx_list.html |
| 003002010006 | 成交结果单笔公告 | /ggzyjy/jyxx/003002/003002010/003002010006/jyxx_list.html |
| 003002010007 | 废标公告 | /ggzyjy/jyxx/003002/003002010/003002010007/jyxx_list.html |
| 003002010008 | 成交结果汇总公告 | /ggzyjy/jyxx/003002/003002010/003002010008/jyxx_list.html |

### 003003 产权交易
| categorynum | 名称 | 入口 |
|---|---|---|
| 003003001 | 挂牌公告 | /ggzyjy/jyxx/003002/003003001/jyxx_list.html |
| 003003002 | 成交公告 | /ggzyjy/jyxx/003002/003003002/jyxx_list.html |
| 003003003 | 已经撤牌 | /ggzyjy/jyxx/003002/003003003/jyxx_list.html |

### 003004 自然资源要素
| categorynum | 名称 | 入口 |
|---|---|---|
| 003004001 | 出让公告 | /ggzyjy/jyxx/003004/003004001/jyxx_list.html |
| 003004002 | 结果公告 | /ggzyjy/jyxx/003004/003004002/jyxx_list.html |
| 003004003 | 其他公告 | /ggzyjy/jyxx/003004/003004003/jyxx_list.html |

> 注：003003 / 003004 / 003005 / 003006 / 007 等非政府采购分类也共用同一 API，按需生成。本表覆盖主要公告类型；003005 林地、003006 药品耗材、003007 非依法招标结构同上，URL 路径规则一致（见上表对应栏目链接）。

## 5. 分页分析

- 分页方式：**偏移量（offset）分页**，非游标、非页码参数。
- `pn` = 起始行 = `(page - 1) * rn`，`rn` = 每页条数（页面默认 10）。
- 总条数：响应 `result.totalcount`。
- 总页数：`ceil(totalcount / rn)`。
- 排序：`sort={"webdate":"0"}`（发布时间降序）。
- DS DSL 映射建议：`pagination.page_param` 中 `current=1, start=0(pn), step=rn, per_num=10`，`count` 用 jsonpath `$.result.totalcount` 提取并换算；或直接以 `pn` 作为 page_param（start=0, step=10）。
- 注意：该 API 每页最大返回受引擎限制，未见明显上限；`rn` 建议保持 10。

## 6. 字段分析

### 6.1 列表字段（来自 API `result.records`）

| 业务字段 | API 字段 | 处理 |
|---|---|---|
| 标题 title | `titlenew` 或 `title` | 直接取 |
| 链接 url | `linkurl` | 前缀补 host（`https://ggzy.hainan.gov.cn`）|
| 发布时间 publish_time | `webdate` | 取前 10 位 `YYYY-MM-DD`，`format:"date"` |
| 地区 | `xiaquname` | 可选 |
| 信息来源 | `zhuanzai` | 可选 |

### 6.2 详情字段（来自详情页 HTML，已实测）

URL 形如 `https://ggzy.hainan.gov.cn/jyxx/003002/003002002/20260626/{infoid}.html`。

| 业务字段 | 选择器 / 来源 | 备注 |
|---|---|---|
| 标题 title | `//h3[@class='infotitle']/text()` | |
| 发布时间 publish_time | `//div[@class='article-sources']//p[contains(.,'信息时间')]/text()` | regex `(\d{4}-\d{2}-\d{2})` |
| 正文 content | `//div[@id='noticeArea']` | 含样式内联，需清洗 |
| 项目编号 project_code | `#noticeArea` 内文本中 `项目编号：HNGP2026-085` | regex; `isbalance`/`isclean` 可选 |
| 采购人 | `_notice_content_noticePurchase-purchaserOrgName` span 文本 | 可选 |
| 代理机构 | `_notice_content_noticeAgency-agencyName` span 文本 | 可选 |
| 附件 attachment | `//div[@class='shengzf-Attach']//ul/li/a[@href and @title]` | `@href` 为直链（含 `gpx-public-file?accessCode=...`）；另注：正文末尾 `a[contains(@href,'gpx-public-file')]` 也可能出现重复附件，可用 candidate 兜底 |

详情页 `<meta name="ArticleTite">`、`<meta name="InfoDate">` 亦可作为兜底来源。

## 7. 请求方式与模式选择

- list：**`mode:"REQUESTS"`, `method:"POST"`**，请求体 JSON。无需浏览器自动化。
  - 注意：`entrance_url` 为 API URL，因是 POST + JSON body，不能简单用 URL query 传参；建议参考引擎 `M@$` 负载机制或直接在 `captcha`/预置步骤中构造。categorynum、pn 通过 condition 注入。
  - 备选：可对 API 做 GET 式拼接（引擎不支持纯 GET，仍走 POST body）。具体 DSL 写法见生成阶段。
- detail：**`mode:"REQUESTS"`, `method:"GET"`**，HTML 解析（`xpath`）。无需 JS。
- 静态请求即可获得数据，不建议 `SELENIUM`。

## 8. 未解决 / 待确认问题

1. **API 无鉴权 token 即可访问**（实测 token="" 可返回数据），但若有 IP/频控未知；建议保持合理间隔。
2. **附件链接** 指向 `ccgp-hainan.gov.cn/gpx-public-file?accessCode=...`（外域政府云），`accessCode` 为 MD5 JWT，无需二次解析即可下载；但部分附件可能为 zip 集包文件，引擎需按文件类型处理。
3. **四级栏目（框架协议）** 是否需要单独配置 vs 合并到 `003002010`：categorynum 前缀匹配下，用 `003002010` 可覆盖全部四级；若要单独分类，需用精确 6 位四级号（`likeType` 改为非前缀，或精确 `equal`）。建议按业务需求逐类生成。
4. **`pn` 上限**：深度翻页（如 >1000 页）是否被引擎截断未验证；如遇截断可加 `time` 条件按日期分段。
5. **003003/003004 等 URL 路径笔误风险**：产权交易栏目实际路径为 `/ggzyjy/jyxx/003003/...`（上表 003003 行路径误写成 003002，应以左侧菜单 `data-href` 为准）。生成配置时以菜单实际链接为准。

## 9. 结论

- 数据源：✅ REST API（POST JSON），列表无验证码。
- 详情：✅ 服务端渲染 HTML，可直接 xpath。
- 模式：list=`REQUESTS`/POST，detail=`REQUESTS`/GET。
- 适合按 categorynum 批量生成多个分类配置，结构高度一致。
- captcha：false。
