# 海南省公共资源交易服务平台 - 网站分析报告

> 最后实测：2026-06-29（38 个 categorynum 全量验证 + 详情页选择器实测）。

## 1. 网站概况

- 站点名称：海南省公共资源交易服务平台
- 域名：`https://ggzy.hainan.gov.cn/`
- SiteIDCode：4600000022
- 入口页：`/ggzyjy/jyxx/jyxx_list.html`（交易信息，栏目 `cms_003`，categorynum `003`）
- 编码：页面声明 UTF-8，但列表 API 响应为 **GB18030** 编码（实测 `Content-Type` 头谎报 `charset=UTF-8`，但原始字节按 GB18030 解码才得到正常中文，UTF-8 解码乱码）。引擎 `base.py` 中 `resp.encoding = resp.apparent_encoding or "utf-8"` 可正确探测；DSL 无需特殊处理。详情页为真 UTF-8。
- 验证码：本次分析入口及详情均**未发现验证码/登录/滑块**。`captcha=false`。

## 2. 网站结构

- 首页：`/ggzyjy/`
- 栏目树：左侧 `.column-second` 二级栏目 + `.column-third` 三级栏目，部分四级（框架协议采购）。
- 列表页：`jyxx_list.html` 类页面，**静态 HTML 为空壳**，列表数据由 JS（`jyxx_list_fullsearch.js`）调用全文检索 API 异步渲染（Mustache 模板 `#info-item` 注入 `#info-list`）。**必须使用 API，不能用 HTML 解析列表。**
- 详情页：正文服务端渲染，可直接 HTML 解析。API 返回的 `linkurl` 形如 `/jyxx/{cat...}/{yyyyMMdd}/{infoid}.html`，列表 JS 会前置 `rootPath=/ggzyjy`。实测两种路径（`/jyxx/...` 与 `/ggzyjy/jyxx/...`）均返回 200 且内容一致；DSL 中用 `prepath:true` 直接拼 host 即可（`https://ggzy.hainan.gov.cn` + linkurl）。

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
- **必须请求头**（缺一不可）：`Referer`（对应栏目列表页 URL）+ `Origin` + `User-Agent` + `X-Requested-With: XMLHttpRequest`。缺头时 API 返回 HTML 错误页（HTTP 200，长度 ~2915）而非 JSON，极易误判成功。
- 请求体关键字段（来自 `jyxx_list_fullsearch.js`）：

```json
{
  "token": "",
  "pn": 0,            // 起始行偏移 = pageIndex * pageSize（0 基）★ 必须是 int
  "rn": 10,           // 每页条数  ★ 必须是 int
  "sdt": "", "edt": "",
  "wd": " ",          // 关键词（空格代表全部，需 encodeURIComponent）
  "inc_wd": "", "exc_wd": "",
  "fields": "title",
  "cnum": "001",
  "sort": "{\"webdate\":\"0\"}",   // 0=降序
  "ssort": "title",
  "cl": 200,          // content 截断长度  ★ 必须是 int
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

> ★ 数值字段（`pn`/`rn`/`cl`）若以字符串形式发送，服务器返回 HTML 错误页（HTTP 200）。引擎 `M@$` 负载解析默认保留字符串，故这些字段须用 `@json:` 包裹（如 `pn=@json:0`）以保证 JSON 序列化为 `int`。

### 实测响应结构（categorynum=003002002 验证通过，2026-06-29 total=33575）

```json
{
  "result": {
    "totalcount": 33575,
    "records": [
      {
        "titlenew": "公告标题",
        "title": "公告标题",
        "infoid": "8a1d1abc9ef2af7a019f1164796b6dc2",
        "linkurl": "/jyxx/003002/003002002/20260629/8a1d1abc9ef2af7a019f1164796b6dc2.html",
        "webdate": "2026-06-29 11:42:10",
        "infodate": "2026-06-29 11:42:14",
        "xiaquncode": "460000",
        "xiaquname": "海南省 省中心",
        "zhuanzai": "海南省政府网",        // 信息来源
        "categorynum": "003002002",
        "categoryname": "采购公告",
        "content": "正文截断片段..."        // cl=200 截断，不可用于详情正文
      }
    ],
    "categorys": [{"categorynum":"001","count":"33575","categoryname":"项目信息"}],
    "maxScore": 5.0, "scorllId": "...", "executetime": "0.014"
  }
}
```

要点：
- `totalcount` 直接给出总条数 → 可推断总页数 = ceil(totalcount / rn)。
- `linkurl` 以 `/` 开头，需前缀拼接 host `https://ggzy.hainan.gov.cn`（引擎 `prepath:true`）。
- `webdate` 取前 10 位即日期；`infodate` 为入库时间，列表页用 `webdate`。
- `content` 字段被截断，**详情正文必须取详情页**，不能依赖 API 的 content。

## 4. 完整分类树（全量实测 2026-06-29）

所有分类共用同一 API，仅 `condition[0].equal`（categorynum）不同。栏目路径规则一致。

### 一级：003 交易信息

#### 003001 工程建设
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003001001 | 招标计划 | /ggzyjy/jyxx/003001/003001001/jyxx_list.html | 10284 |
| 003001002 | 招标公告 | /ggzyjy/jyxx/003001/003001002/jyxx_list.html | 31509 |
| 003001003 | 资格预审公告 | /ggzyjy/jyxx/003001/003001003/jyxx_list.html | 161 |
| 003001004 | 变更公告 | /ggzyjy/jyxx/003001/003001004/jyxx_list.html | 6388 |
| 003001005 | 中标候选人公示 | /ggzyjy/jyxx/003001/003001005/jyxx_list.html | 8560 |
| 003001006 | 中标公告 | /ggzyjy/jyxx/003001/003001006/jyxx_list.html | 38900 |
| 003001007 | 异常公告 | /ggzyjy/jyxx/003001/003001007/jyxx_list.html | 2213 |

#### 003002 政府采购 ★（本次重点）
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003002002 | 采购公告 | /ggzyjy/jyxx/003002/003002002/jyxx_list.html | 33575 |
| 003002003 | 变更公告 | /ggzyjy/jyxx/003002/003002003/jyxx_list.html | 4598 |
| 003002004 | 采购结果公告 | /ggzyjy/jyxx/003002/003002004/jyxx_list.html | 34264 |
| 003002005 | 合同公示 | /ggzyjy/jyxx/003002/003002005/jyxx_list.html | 6305 |
| 003002006 | 异常公告 | /ggzyjy/jyxx/003002/003002006/jyxx_list.html | 4122 |
| 003002007 | 意向公开 | /ggzyjy/jyxx/003002/003002007/jyxx_list.html | 4422 |
| 003002008 | 单一来源公示 | /ggzyjy/jyxx/003002/003002008/jyxx_list.html | 119 |
| 003002009 | 履约验收公示 | /ggzyjy/jyxx/003002/003002009/jyxx_list.html | 3540 |
| 003002010 | 框架协议采购（含四级，共71条） | /ggzyjy/jyxx/003002/003002010/jyxx_list.html | 71 |

##### 003002010 框架协议采购（四级）
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003002010001 | 征集公告 | /ggzyjy/jyxx/003002/003002010/003002010001/jyxx_list.html | 45 |
| 003002010002 | 入围结果公告 | /ggzyjy/jyxx/003002/003002010/003002010002/jyxx_list.html | 26 |
| 003002010003 | 终止公告 | /ggzyjy/jyxx/003002/003002010/003002010003/jyxx_list.html | 0 |
| 003002010004 | 供应商退出框架协议公告 | /ggzyjy/jyxx/003002/003002010/003002010004/jyxx_list.html | 0 |
| 003002010005 | 采购公告 | /ggzyjy/jyxx/003002/003002010/003002010005/jyxx_list.html | 0 |
| 003002010006 | 成交结果单笔公告 | /ggzyjy/jyxx/003002/003002010/003002010006/jyxx_list.html | 0 |
| 003002010007 | 废标公告 | /ggzyjy/jyxx/003002/003002010/003002010007/jyxx_list.html | 0 |
| 003002010008 | 成交结果汇总公告 | /ggzyjy/jyxx/003002/003002010/003002010008/jyxx_list.html | 0 |

> 003002010 用 `likeType:2` 前缀匹配即可覆盖全部四级（45+26=71 与上级 71 一致）。四级单独为 0 的类型可暂不单独建配置。

#### 003003 产权交易
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003003001 | 挂牌公告 | /ggzyjy/jyxx/003003/003003001/jyxx_list.html | 14998 |
| 003003002 | 成交公告 | /ggzyjy/jyxx/003003/003003002/jyxx_list.html | 4748 |
| 003003003 | 已经撤牌 | /ggzyjy/jyxx/003003/003003003/jyxx_list.html | 5 |

> 注：旧版分析表中 003003 路径误写为 `/ggzyjy/jyxx/003002/003003001/...`，实测正确路径为 `/ggzyjy/jyxx/003003/003003001/...`（二级段为 003003，非 003002）。已修正。

#### 003004 自然资源要素
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003004001 | 出让公告 | /ggzyjy/jyxx/003004/003004001/jyxx_list.html | 1833 |
| 003004002 | 结果公告 | /ggzyjy/jyxx/003004/003004002/jyxx_list.html | 1291 |
| 003004003 | 其他公告 | /ggzyjy/jyxx/003004/003004003/jyxx_list.html | 336 |

#### 003005 林地
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003005001 | 出让公告 | /ggzyjy/jyxx/003005/003005001/jyxx_list.html | 74 |
| 003005002 | 招标公告 | /ggzyjy/jyxx/003005/003005002/jyxx_list.html | 0 |
| 003005003 | 结果公告 | /ggzyjy/jyxx/003005/003005003/jyxx_list.html | 54 |

#### 003006 药品耗材
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003006001 | 通知公告 | /ggzyjy/jyxx/003006/003006001/jyxx_list.html | 144 |
| 003006002 | 服务大厅 | /ggzyjy/jyxx/003006/003006002/jyxx_list.html | 4 |
| 003006003 | 咨询方式 | /ggzyjy/jyxx/003006/003006003/jyxx_list.html | 0 |

#### 003007 非依法招标
| categorynum | 名称 | 入口 | 实测总数 |
|---|---|---|---|
| 003007001 | 招标公告 | /ggzyjy/jyxx/003007/003007001/jyxx_list.html | 21 |
| 003007002 | 答疑澄清公告 | /ggzyjy/jyxx/003007/003007002/jyxx_list.html | 18 |
| 003007003 | 结果公告 | /ggzyjy/jyxx/003007/003007003/jyxx_list.html | 17 |

## 5. 政府采购公告类型逐项分析 ★

9 个类型结构高度一致，仅 `categorynum` 与 `Referer` 不同。下表为统一规则，逐项差异详见末列。

### 5.1 公告类型清单（含实测总数）

| categorynum | 类型 | 列表入口 | 实测总数 | 四级 |
|---|---|---|---|---|
| 003002002 | 采购公告 | `/ggzyjy/jyxx/003002/003002002/jyxx_list.html` | 33575 | - |
| 003002003 | 变更公告 | `/ggzyjy/jyxx/003002/003002003/jyxx_list.html` | 4598 | - |
| 003002004 | 采购结果公告 | `/ggzyjy/jyxx/003002/003002004/jyxx_list.html` | 34264 | - |
| 003002005 | 合同公示 | `/ggzyjy/jyxx/003002/003002005/jyxx_list.html` | 6305 | - |
| 003002006 | 异常公告 | `/ggzyjy/jyxx/003002/003002006/jyxx_list.html` | 4122 | - |
| 003002007 | 意向公开 | `/ggzyjy/jyxx/003002/003002007/jyxx_list.html` | 4422 | - |
| 003002008 | 单一来源公示 | `/ggzyjy/jyxx/003002/003002008/jyxx_list.html` | 119 | - |
| 003002009 | 履约验收公示 | `/ggzyjy/jyxx/003002/003002009/jyxx_list.html` | 3540 | - |
| 003002010 | 框架协议采购 | `/ggzyjy/jyxx/003002/003002010/jyxx_list.html` | 71 | 含 003002010001~008 |

### 5.2 列表请求方式（9 类统一）

- **API URL**：`https://ggzy.hainan.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNew`
- **Method**：`POST`
- **mode**：`REQUESTS`
- **Content-Type**：`application/json`
- **必须请求头**：
  - `Referer`: `https://ggzy.hainan.gov.cn/ggzyjy/jyxx/003002/{categorynum}/jyxx_list.html`（按类型变化）
  - `Origin`: `https://ggzy.hainan.gov.cn`
  - `User-Agent`: 浏览器 UA
  - `X-Requested-With`: `XMLHttpRequest`
- **请求体**：见 §3 模板，`condition[0].equal` 改为对应 categorynum（`likeType:2` 前缀匹配，故 003002010 自动覆盖其下四级）。
- **数值字段** `pn`/`rn`/`cl` 必须为 int（DSL 中用 `@json:` 包裹）。

### 5.3 参数

- `categorynum`：通过 `condition[0]` 注入，9 类分别取值为上表 categorynum。`isLike:true, likeType:2`（前缀匹配）。
- `xiaquncode`（地区，可选）：加入 `condition` 第二条，如三亚 `equal:"460200", likeType:2` 前缀匹配覆盖下属区。不传则返回全省。
- `pn`：偏移量（见分页）。
- `rn`：每页条数，默认 10。
- `sort`：`{"webdate":"0"}` 发布时间降序。
- `time`：`webdate` 时间范围，默认 1970~2999。

### 5.4 分页方式（9 类统一）

- **偏移量分页**，非游标、非页码参数。
- `pn = pageIndex * rn`（0 基），`rn = 10`。
- 总条数：响应 `result.totalcount`。
- 总页数：`ceil(totalcount / rn)`。
- DSL 映射：`pagination.page_param` 用 `current=0, start=0, step=rn(10), offset=0, per_num=10`；`count` 用 jsonpath `$.result.totalcount` 引擎自动换算页数。子任务 URL 模板 `pn=@json:${page_param}`，引擎按 `page*step+offset` 替换。

### 5.5 详情页规则（9 类统一）

- **URL**：`{host} + linkurl`，如 `https://ggzy.hainan.gov.cn/jyxx/003002/003002002/20260629/{infoid}.html`。
  - `linkurl` 来自列表 API（以 `/` 开头），`prepath:true` 拼 host。
  - `/jyxx/...` 与 `/ggzyjy/jyxx/...` 均返回 200 且内容一致。
- **Method**：`GET`
- **mode**：`REQUESTS`（服务端渲染，无需 JS）
- **鉴权**：无

### 5.6 字段结构（9 类统一）

#### 列表字段（来自 API `result.records`，type=`jsonpath`）

| 业务字段 | API 字段 | jsonpath | 处理 |
|---|---|---|---|
| 标题 title | `titlenew` | `$.result.records[*].titlenew` | 直接取；亦可用 `title` |
| 链接 url | `linkurl` | `$.result.records[*].linkurl` | `prepath:true` 拼 host `https://ggzy.hainan.gov.cn` |
| 发布时间 publish_time | `webdate` | `$.result.records[*].webdate` | 取前 10 位 `YYYY-MM-DD`，`format:"date"` |
| 地区 | `xiaquname` | `$.result.records[*].xiaquname` | 可选，例 "海南省 省中心" |
| 信息来源 | `zhuanzai` | `$.result.records[*].zhuanzai` | 可选 |
| 公告ID | `infoid` | `$.result.records[*].infoid` | 可选，详情 URL 自带 |

> 注意：API 返回 `content` 为 `cl` 截断片段，**不可用作详情正文**，详情正文必须取详情页 `#noticeArea`。

#### 详情字段（来自详情页 HTML，type=`xpath`，2026-06-29 实测）

| 业务字段 | xpath                                                                 | 备注 |
|---|-----------------------------------------------------------------------|---|
| 标题 title | `//h3[@class='infotitle']/text()`                                     | 实测存在 |
| 发布时间 publish_time | `//div[contains(@class,'article-sources')]/textall()`                 | regex `(\d{4}-\d{2}-\d{2})`；`<meta name="InfoDate">` 可兜底 |
| 正文 content | `//div[@id='noticeArea']`                                             | 含内联样式，需清洗 |
| 项目编号 project_code | `//div[@id='noticeArea']/textall()`                                   | regex `(?:项目编号|采购编号|招标编号)\s*[：:]\s*([A-Za-z0-9\-]+)`；`isbalance`/`isclean`；实测样本 `SCIT-HNZG-2026030002` |
| 附件 attachment | `//div[contains(@class,'shengzf-Attach')]//ul/li/a[@href and @title]` | `@href` 直链 `https://ccgp-hainan.gov.cn/gpx-public-file?accessCode=...`；`@title`=文件名 |
| 附件兜底 candidate | `//a[contains(@href,'gpx-public-file')]`                              | 正文末尾可能重复出现，作 candidate 兜底 |

详情页 `<meta name="ArticleTite">`、`<meta name="InfoDate">` 实测存在，可作标题/时间兜底。

附件说明：`accessCode` 为 MD5 JWT，无需二次解析即可下载；指向外域 `ccgp-hainan.gov.cn`。

## 6. 请求方式与模式选择

- list：**`mode:"REQUESTS"`, `method:"POST"`**，请求体 JSON。无需浏览器自动化。
  - 注意：`entrance_url` 为 API URL，POST + JSON body 通过引擎 `M@$` 负载机制构造；数值字段须 `@json:` 包裹；必带 Referer/Origin/UA/X-Requested-With。
- detail：**`mode:"REQUESTS"`, `method:"GET"`**，HTML 解析（`xpath`）。无需 JS。
- 静态请求即可获得数据，不建议 `SELENIUM`。

## 7. 未解决 / 待确认问题

1. **API 无鉴权 token 即可访问**（实测 token="" 可返回数据），但若有 IP/频控未知；建议保持合理间隔。
2. **附件链接** 指向 `ccgp-hainan.gov.cn/gpx-public-file?accessCode=...`（外域政府云），`accessCode` 为 MD5 JWT，无需二次解析即可下载；但部分附件可能为 zip 集包文件，引擎需按文件类型处理。
3. **四级栏目（框架协议）** 是否需要单独配置 vs 合并到 `003002010`：categorynum 前缀匹配下，用 `003002010` 可覆盖全部四级（实测 71 一致）；若要单独分类，需用精确四级号并把 `likeType` 改为非前缀。建议按业务需求逐类生成；四级中 6 个类型当前为 0 条，可暂不单独建配置。
4. **`pn` 上限**：深度翻页（如 >1000 页）是否被引擎截断未验证；如遇截断可加 `time` 条件按日期分段。
5. **`wd` 编码**：JS 中对 `wd`/`inc_wd`/`exc_wd` 做 `encodeURIComponent`，但引擎 `M@$` 通过 `parse_qs(unquote(...))` 已 URL 解码；空格关键词 `wd=" "` 在 DSL 中用 `%20` 表达即可。

## 8. 结论

- 数据源：✅ REST API（POST JSON），列表无验证码。
- 详情：✅ 服务端渲染 HTML，可直接 xpath。
- 模式：list=`REQUESTS`/POST，detail=`REQUESTS`/GET。
- 政府采购 9 类（003002002~003002010）结构完全一致，仅 `categorynum` 与 `Referer` 不同 → 适合按公告类型批量生成。
- 框架协议（003002010）可用前缀匹配覆盖 8 个四级子类。
- 全站 7 个二级分类（003001~003007）共 38 个 categorynum 均共用同一 API，结构同上，可按需扩展。
- captcha：false。

> 本文件仅分析，未生成 Python 配置。
