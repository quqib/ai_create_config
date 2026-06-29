```markdown
# Batch Generate Config


目标：

批量生成Python DSL配置。



输入：

config/



流程：


for each python config:

    analyze_site

    generate_single



---

# Output


保存：


result/{site}/



例如：

result/

    hainan/

        government_purchase.py



---

# Rules


1.

不要修改config


2.

失败记录：

analysis/error.log


3.

每个网站独立目录


4.

生成文件必须可以import


