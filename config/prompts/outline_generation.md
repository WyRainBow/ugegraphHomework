# 大纲生成 Prompt

请生成文章大纲，只包含标题，不要写正文。

## 输出格式（JSON）
{
  "headline_suggestions": ["标题1", "标题2", "标题3"],
  "sections": [
    {"heading": "H2 标题", "notes": "简短说明"},
    {"heading": "H3 标题", "notes": "简短说明"}
  ],
  "keyword_placement": "关键词布局建议"
}
