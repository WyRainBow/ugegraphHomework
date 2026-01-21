#!/usr/bin/env python3
"""移动 HugeGraph plans 目录"""
import shutil
from pathlib import Path

source = Path("/Users/wy770/.cursor/plans/HugeGraph")
target = Path("/Users/wy770/Apache/HugeGraph")

print("=" * 60)
print("移动 HugeGraph plans 目录")
print("=" * 60)
print(f"\n源目录: {source}")
print(f"目标目录: {target}")

# 检查源目录是否存在
if not source.exists():
    print(f"\n✗ 源目录不存在: {source}")
    exit(1)

print(f"\n✓ 源目录存在")

# 如果目标目录已存在，先删除
if target.exists():
    print(f"⚠ 目标目录已存在，先删除...")
    shutil.rmtree(target)
    print(f"✓ 已删除旧目录")

# 移动目录
try:
    print(f"\n正在移动目录...")
    shutil.move(str(source), str(target))
    print(f"✓ 移动成功！")
    
    # 列出移动后的文件
    print(f"\n移动后的文件列表:")
    for file in sorted(target.rglob("*.md")):
        print(f"  - {file.relative_to(target)}")
    
    print(f"\n" + "=" * 60)
    print(f"✓ 完成！HugeGraph 目录已移动到: {target}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 移动失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
