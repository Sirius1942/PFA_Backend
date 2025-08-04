#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷测试运行脚本
"""

import sys
import subprocess

def main():
    """运行基本测试"""
    try:
        # 运行基本测试
        result = subprocess.run([sys.executable, "run_basic_tests.py"], 
                              capture_output=False, text=True)
        return result.returncode
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
