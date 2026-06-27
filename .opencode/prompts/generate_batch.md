
---

# 📁 ③ generate_batch.md（批量生成器）

```markdown
# BATCH DSL GENERATION

---

## INPUT

config directory:
config/

---

## TASK

遍历 config 中所有网站配置

对每个网站执行：

1. analyze_site
2. generate_single

---

## OUTPUT

每个网站生成独立目录：

result/{{site}}/

---

## FILE STRUCTURE

result/
   hainan/
      purchase.py
      contract.py
   anhui/
      purchase.py

---

## EXECUTION RULES

### 必须顺序执行
- 不能并发跳过
- 不能遗漏网站

### 失败处理

如果失败：

写入：

result/_errors.log

---

## STRICT MODE

禁止：

- 合并网站
- 跳过分析
- 跳过生成