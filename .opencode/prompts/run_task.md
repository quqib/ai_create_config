# crawler task executor


读取：

tasks/*.yaml


执行以下流程：


## Step 1

读取任务配置。


获取：

- website
- org_id
- industry
- category


## Step 2

调用：

crawler-config-basic skill


分析网站：


输出：

analysis/{site}.md



必须分析：

1. 网站分类树

2. 所有公告类型

3. API接口

4. 请求方式

5. 字段


禁止：

直接生成配置。



---


## Step 3

根据：

analysis文件


参考：

config目录


生成Python配置。


要求：

输出：

result/{site}/


结构：

result/{site}

    xxx.py

    xxx.py



必须：

可以被python import


---


## Step 4

检查：

- org_id
- source_site
- industry
- notice_type

是否完整。
