# 单配置生成任务


使用：

crawler-config-basic skill


网站：

{{website}}


公告类型：

{{category}}



任务：


根据网站分析结果生成一个 DSL 配置。


要求：


## 分析


确认：

1. 列表入口

2. 请求方式

3. 请求参数

4. 分页规则

5. 详情页规则

6. 字段映射



## 生成


生成：

result/{{site}}/{{category}}.json



配置必须包含：


- entranceUrl

- list

- detail

- pagination

- fields



## 限制


当前网站：

captcha=false



不要处理：

- 验证码
- 登录
- JS逆向



如果发现：

验证码

输出：

needCaptcha=true


不要绕过。