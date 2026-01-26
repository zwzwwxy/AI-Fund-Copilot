#!/usr/bin/env python3
"""
生成 GitHub Secrets 格式的持仓配置

用法：
    python tools/generate_secrets.py

功能：
    1. 读取 holdings.json
    2. 生成可以在 GitHub Secrets 中使用的格式
    3. 输出到控制台，方便复制
"""

import json
import os

def main():
    holdings_file = "holdings.json"

    if not os.path.exists(holdings_file):
        print(f"[ERROR] 文件不存在: {holdings_file}")
        return

    with open(holdings_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    holdings_json = json.dumps(data, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("GitHub Secrets 配置")
    print("=" * 60)
    print("\n在 GitHub 仓库 Settings → Secrets and variables → Actions 中创建：")
    print("\nSecret 名称: HOLDINGS_JSON")
    print("-" * 60)
    print(f"\n值:\n\n{holdings_json}")
    print("\n" + "-" * 60)
    print("\n使用方法：")
    print("1. 复制上面的值")
    print("2. 在 GitHub Secrets 中创建新的 Secret")
    print("3. 粘贴值，保存")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
