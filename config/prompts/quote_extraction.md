# 引用金句提取 Prompt

从投票邮件正文中提取正面评价、祝贺语或支持性陈述。

## 规则
- 优先选择 IPMC 成员（binding votes）的邮件
- 查找以下类型的表达：
  - 明确祝贺（"Congratulations", "Congrats", "Well done"）
  - 正面评价（"Great work", "Excellent", "Impressive"）
  - 支持性陈述（"I support", "I'm happy to see", "This is great news"）
  - 对项目的积极评价（"Strong community", "Mature project"）
- 如果正文很长，提取最相关的 1-2 句话
- 保持原文，不要改写或总结
- 如果没有合适引用，返回空字符串（不要输出解释或道歉）

## 输出格式
每条引用使用 Markdown blockquote：
> 引用内容 — 姓名
