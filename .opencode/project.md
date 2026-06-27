# AI Crawler Configuration Project


## 项目目标

本项目用于自动生成政府采购网站爬虫 DSL 配置。

目标：

输入：

- 网站入口 URL
- 网站结构
- API信息
- 页面规则


输出：

符合项目规范的 crawler DSL 配置文件。


---

# 项目背景


目前系统需要支持大量政府采购网站。

每个网站可能包含：

- 采购公告
- 更正公告
- 中标公告
- 成交公告
- 合同公告
- 其他公告


不同公告类型需要独立配置。


---

# 配置类型


## 普通配置

特点：

- 无验证码
- 无登录
- 无滑块
- 无特殊 token


captcha:

false


处理方式：

直接通过：

- API
- HTML
- JSON


生成配置。



## 高级配置

特点：

存在：

- 验证码
- cookie生成
- JS加密
- token计算
- 请求签名


captcha:

true


高级配置需要额外分析。


---

# DSL结构


配置主要包含：


## 网站入口

entranceUrl


## 列表页

list:


包含：

- URL
- method
- params
- headers



## 详情页

detail:


包含：

- URL规则
- 字段解析


## 分页

pagination:


包含：

- page参数
- offset
- cursor


## 字段


fields:


包含：

- title
- publishTime
- content
- url



---

# AI工作原则


1. 优先寻找 API。

2. API存在时不要模拟浏览器。

3. 不直接生成Python代码。

4. 输出必须符合DSL。

5. 不确定的信息必须标记。

6. 不允许猜测接口。


---

# 输出位置


所有生成配置保存：

result/


例如：

result/

    anhui/

        purchase.json

        contract.json

        result.json


