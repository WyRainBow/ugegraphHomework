#!/bin/bash
# 推送本地 Git 到 GitHub

set -e

echo "========================================"
echo "推送本地 Git 到 GitHub"
echo "========================================"

cd /Users/wy770/Apache

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    echo "✗ 当前目录不是 Git 仓库"
    echo "正在初始化 Git 仓库..."
    git init
    git remote add origin https://github.com/WyRainBow/hugegraph-work.git 2>/dev/null || git remote set-url origin https://github.com/WyRainBow/hugegraph-work.git
    echo "✓ Git 仓库已初始化"
fi

# 显示当前状态
echo ""
echo "当前 Git 状态:"
git status --short

# 添加所有文件
echo ""
echo "添加所有文件..."
git add .

# 检查是否有变更
if git diff --cached --quiet && git diff-index --quiet HEAD --; then
    echo "⚠ 没有需要提交的变更"
else
    echo "✓ 文件已添加到暂存区"
    
    # 提交
    echo ""
    echo "提交变更..."
    git commit -m "Update: Apache HugeGraph project

- 添加 HugeGraph plans 目录
- 更新项目文档
- 更新配置文件" || echo "⚠ 提交失败或无需提交"
fi

# 设置分支为 main（如果还没有）
current_branch=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$current_branch" ]; then
    echo ""
    echo "创建并切换到 main 分支..."
    git checkout -b main 2>/dev/null || git branch -M main
fi

# 确保远程仓库配置正确
echo ""
echo "检查远程仓库配置..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/WyRainBow/hugegraph-work.git
echo "✓ 远程仓库: https://github.com/WyRainBow/hugegraph-work.git"

# 推送
echo ""
echo "推送到 GitHub..."
echo "分支: $(git branch --show-current 2>/dev/null || echo 'main')"
git push -u origin $(git branch --show-current 2>/dev/null || echo main) 2>&1 | tail -20

echo ""
echo "========================================"
echo "✓ 推送完成！"
echo "========================================"
