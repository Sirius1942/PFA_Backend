#!/usr/bin/env python3
"""
测试脚本运行器
一键运行所有测试脚本
"""

import subprocess
import sys
import os

def run_test(test_name, command):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"🧪 运行 {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_name} - 测试通过")
            if result.stdout:
                # 只显示关键信息
                lines = result.stdout.split('\n')
                success_lines = [line for line in lines if '✅' in line or '📊' in line or '🎉' in line]
                if success_lines:
                    for line in success_lines[:5]:  # 只显示前5个成功信息
                        print(f"   {line}")
        else:
            print(f"❌ {test_name} - 测试失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {test_name} - 运行异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 私人金融分析师 - 测试套件运行器")
    print("=" * 80)
    
    # 检查当前目录
    if not os.path.exists("tests"):
        print("❌ 找不到tests目录，请在项目根目录运行此脚本")
        return
    
    # 定义测试
    tests = [
        ("登录API测试", "python tests/test_login_api.py"),
        ("技术指标测试", "python tests/test_technical.py"),
        ("系统综合测试", "python tests/test_system.py"),
        ("AI代理测试", "python -m tests.test_agent"),
    ]
    
    # 运行测试
    results = []
    for test_name, command in tests:
        success = run_test(test_name, command)
        results.append((test_name, success))
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常！")
    else:
        print(f"⚠️ {total - passed} 项测试失败，请检查相关组件")

if __name__ == "__main__":
    main()