# 批量配置生成任务


使用：

crawler-config-batch skill



目标网站：

{{website}}



任务：


分析整个网站。


自动发现所有公告分类。


例如：


- 采购公告

- 更正公告

- 中标公告

- 成交公告

- 合同公告



然后：

针对每个分类生成独立 DSL。



---

# 工作流程


## Step 1

分析网站。


找到：

category列表。



## Step 2

遍历每个category。


分析：

- list URL

- API

- 参数

- 分页

- detail URL



## Step 3

生成配置。


保存：


result/{{site}}/


例如：


result/anhui/


    purchase.json

    change.json

    result.json

    contract.json



---

# 规则


当前：

captcha=false



不要：

- 写代码

- 修改爬虫框架

- 处理验证码



如果遇到：

验证码

输出：

captcha_required.md


---

# 最终输出


生成：

1. 配置文件

2. 分析报告

3. 未解决问题列表
