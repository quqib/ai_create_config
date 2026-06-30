# 网站采集配置生成规则


## 一、目标

本 Skill 用于生成政府公共资源交易网站采集配置。

输入：

- 网站 URL
- 网站分类信息
- 网站结构
- 示例配置


输出：

符合项目规范的 Python 配置文件。


生成文件必须：

- 可以被 Python import
- 符合 config 示例结构
- 放置到 result 目录


---

# 二、分析原则


## 数据来源优先级


按照以下顺序分析：


1. API接口

2. JSON数据

3. HTML源码

4. 浏览器渲染


优先选择：

REQUESTS


只有以下情况使用：

SELENIUM


条件：

- 页面必须执行 JavaScript
- 数据由 JS 动态生成
- 存在浏览器交互


禁止：

为了方便直接使用 SELENIUM。


---


# 三、分类规则


网站中的栏目结构需要完整解析。


例如：


交易信息

    政府采购

        采购公告

        中标公告

        合同公告


应该生成：


result/{site}/

    caigougonggao.py

    zhongbiaogonggao.py

    hetonggonggao.py



禁止生成：


government_purchase.py（合并所有类型的单一文件）



原因：

一个最终公告类型对应一个 Python 配置文件。


---


# 四、多级分类规则


如果网站存在：

省

    市

        区县


仍然采用平铺结构，所有配置文件放在 result/{site}/ 目录下，每个公告类型对应单独的 .py 文件。


例如：

result/{site}/
    caigougonggao.py
    zhongbiaogonggao.py
    hetonggonggao.py

禁止：

把所有配置放在一个目录（如 result/{site}/all.py）。


---


# 五、配置来源规则


生成配置时参考：


1. config目录中的示例 Python 文件

2. config_schema.md

3. SKILL.md


三者优先级：

config_schema.md

>

示例配置

>

普通经验


禁止：

自己创造字段。


---


# 六、字段规则


必须包含：


root:

- name
- host
- source_site
- industry
- notice_type


list:

- mode
- method
- fields


detail:

- mode
- method
- fields


pagination:

- enable
- page_param


---


# 七、captcha规则


默认：

captcha=False



不要主动分析：

- 验证码
- 滑块
- 登录
- JS逆向


如果发现必须依赖验证码：

不要绕过。


只增加：

needCaptcha=True


并停止生成该配置。


---


# 八、Python要求


生成文件要求：


1. 文件扩展名：

.py


2. 可以直接执行：

import xxx


3. 不生成说明文字。


4. 不生成 JSON。


5. 不生成 Markdown。


只生成 Python 配置。


---


# 九、错误处理


如果无法确定：


不要猜测。


使用：


TODO


标记。


例如：


# TODO: API参数需要人工确认



---


# 十、输出规则


所有结果保存：

result/{site}/
    caigougonggao.py
    zhongbiaogonggao.py
    hetonggonggao.py






例如：


result/

    hainan/

        hainan_

            result/{site}/

                bidding_notice.py


