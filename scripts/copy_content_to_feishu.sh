#!/bin/bash
# 快速打开本地文件，方便复制到飞书文档

echo "=========================================="
echo "飞书文档链接和本地文件"
echo "=========================================="
echo ""
echo "1. 实现思路和 Prompt 说明"
echo "   飞书链接: https://bytedance.feishu.cn/docx/R6cGdejzaofVw7xKEVNchnNEnge"
echo "   本地文件: docs/实现思路和Prompt说明.md"
echo ""
echo "2. 文章生成 Prompt"
echo "   飞书链接: https://bytedance.feishu.cn/docx/H6SjdziUqoOrMvxVjEFc0rLpnec"
echo "   本地文件: config/prompts/article_generation.md"
echo ""
echo "3. 大纲生成 Prompt"
echo "   飞书链接: https://bytedance.feishu.cn/docx/B7QddXT8yooiGrxSdpocV0yfnXb"
echo "   本地文件: config/prompts/outline_generation.md"
echo ""
echo "4. 引用提取 Prompt"
echo "   飞书链接: https://bytedance.feishu.cn/docx/UGK7dwmV7onmDxxPubCcek2wnVd"
echo "   本地文件: config/prompts/quote_extraction.md"
echo ""
echo "=========================================="
echo "正在打开本地文件..."
echo "=========================================="

# 打开本地文件
open docs/实现思路和Prompt说明.md
open config/prompts/article_generation.md
open config/prompts/outline_generation.md
open config/prompts/quote_extraction.md

echo "✓ 所有文件已打开"
echo ""
echo "请复制每个文件的内容，然后粘贴到对应的飞书文档中"
