#!/bin/bash
# 安装依赖脚本

echo "正在安装依赖..."
pip3 install -r requirements.txt

echo ""
echo "依赖安装完成！"
echo ""
echo "现在可以运行: python3 scripts/generate_article.py"
