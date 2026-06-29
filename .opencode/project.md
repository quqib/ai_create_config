# AI Crawler Config Generator


## Project Goal

本项目用于自动生成政府采购网站 Python DSL 配置。


输入：

- 网站URL


输出：

Python配置文件：

result/{site}/{category}.py


生成文件必须可以直接被Python import执行。


---

# Important

生成目标不是JSON。

禁止生成：

- json配置
- markdown配置
- python爬虫代码


必须生成：

Python dict DSL


---

# Pipeline


所有任务必须按照：


1. analyze_site

网站结构分析


2. generate_single

生成单个Python DSL


3. generate_batch

批量生成



禁止跳过分析直接生成。


---

# Output Rule


所有结果必须保存：


result/


例如：

result/

    hainan/

        government_purchase.py



禁止只在聊天窗口输出代码。



---

# DSL Requirement


生成结构必须参考：

config目录中的示例Python文件。


包括：

- configure
- entrance_url


结构必须兼容现有执行框架。



---

# Analysis Rule


分析阶段必须确认：

- list接口
- detail接口
- pagination
- fields
- headers
- params
- mode



---

# Request Mode


优先：

REQUESTS


只有无法获取数据：

才使用：

SELENIUM


---

# Captcha


如果发现：

- 登录
- 验证码
- token动态生成


标记：

captcha=True


不要绕过。

