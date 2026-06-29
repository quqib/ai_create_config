# crawler-config-basic


## 技能说明


该技能用于自动生成公共资源交易网站爬虫配置文件。


支持业务类型包括：

- 政府采购
- 工程建设
- 产权交易
- 土地交易
- 林权交易
- 其他公共资源交易业务



输出结果：

Python 配置文件


不是：

- JSON
- Markdown
- 新的数据格式



生成的 Python 文件必须能够被现有爬虫框架直接导入执行。



---


# 配置生成流程



## 第一步：读取项目说明


读取：

project.md



目的：

了解：

- 项目目录结构
- 配置输入位置
- 配置输出位置
- Python配置规范



---


## 第二步：读取配置结构规范


读取：

config_schema.md



目的：

理解：

- 配置有哪些字段
- 字段类型
- 字段作用
- 字段嵌套关系



注意：

config_schema.md 只说明：

"有什么字段"



不负责说明：

"字段应该怎么写"



---


## 第三步：读取生成规则


读取：

config_rule.md



目的：

遵守：

- 文件生成规则
- 分类拆分规则
- 目录规则
- 命名规则
- 验证码处理规则



---


## 第四步：读取分类规则


读取：

category_rule.md



目的：

分析网站中的业务分类。


例如：


交易信息

    政府采购

        采购公告

        中标公告

        成交公告


需要拆分为：


government_purchase/

    caigou_notice.py

    bid_result.py



不要默认网站只有政府采购。


必须根据网站实际导航结构分析。


---


## 第五步：读取配置编写手册


读取：

writing_manual.md



非常重要。


该文件规定：


- DSL特殊语法
- 固定字段写法
- 常用解析方式
- 禁止错误写法
- 历史配置经验


生成配置前必须先阅读。


例如：


- @json使用规则

- textall()使用规则

- project_code固定regex

- publish_time处理规则

- URL处理规则

- 分页规则



---


## 第六步：读取examples


读取：

examples/


学习：


- Python文件结构
- 变量名称
- 配置排列方式
- 请求方式
- 字段解析方式



注意：


examples只是参考。


禁止直接复制：

- URL
- 参数
- XPath
- JSONPath



必须根据目标网站重新分析。



---


## 第七步：分析目标网站



分析：


1. 网站分类结构


2. 数据来源


优先级：


API

>

JSON接口

>

HTML

>

浏览器渲染



3. 请求方式


确认：

- GET
- POST



4. 分页方式


确认：

- page
- offset
- cursor
- 下一页链接



5. 详情页结构


确认：

- 标题
- 发布时间
- 项目编号
- 正文
- 附件



禁止猜测。


所有：

- URL
- 参数
- XPath
- JSONPath

必须来源于真实页面。



---


## 第八步：生成配置文件



输出目录：


result/{省份}/{城市}/{业务类型}/



例如：


result/


    hainan/


        hainan_city/


            government_purchase/


                bidding_notice.py



---


# 输入


必须提供：


- 网站URL



可选提供：


- 省份

- 城市

- YAML任务文件

- 指定业务类型

- 已存在配置示例



如果存在 YAML 文件：


优先按照 YAML 执行。



---


# 输出要求


只允许生成：


Python .py 文件



禁止生成：

- JSON配置
- Markdown说明
- 解释文字



生成文件必须：


- 可以 import

- 符合现有项目结构

- 包含必要变量



---


# 强制规则



## 配置格式


禁止创建新的配置格式。


必须遵循：


1. writing_manual.md

2. config_rule.md

3. config_schema.md

4. examples



---


## 不允许猜测


禁止凭空生成：


- API地址

- 请求参数

- XPath

- JSONPath

- 加密方式



如果无法确定：

保留 TODO。



---


## 文件命名规则


目录和文件名：

使用：

- 英文

- 拼音



例如：


government_purchase

bidding_notice.py



Python变量中：

可以保留中文业务名称。



---


# 文件读取优先级


如果规则冲突：


优先级如下：


1. writing_manual.md


2. config_rule.md


3. config_schema.md


4. category_rule.md


5. examples


6. AI自身知识


