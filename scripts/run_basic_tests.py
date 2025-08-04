#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本测试运行器
运行所有基本功能测试用例
"""

import unittest
import sys
import os
import time
from pathlib import Path
import yaml

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def discover_and_run_tests(verbosity=2):
    """发现并运行所有基本测试"""
    print("🚀 私人金融分析师 - 基本功能测试套件")
    print("=" * 80)
    
    start_time = time.time()
    
    # 基本测试模块
    test_modules = [
        'tests.auth.case.test_auth_basic',
        'tests.stocks.case.test_stocks_basic',
        'tests.assistant.case.test_assistant_basic',
        'tests.users.case.test_users_basic',
        'tests.system.case.test_system_basic'
    ]
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    loaded_modules = []
    for module_name in test_modules:
        try:
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
            module_short_name = module_name.split('.')[1]  # 获取模块名
            loaded_modules.append(module_short_name)
            print(f"✅ 加载测试模块: {module_name}")
        except Exception as e:
            print(f"❌ 加载测试模块失败 {module_name}: {e}")
    
    print(f"\n📊 共加载 {len(loaded_modules)} 个基本测试模块")
    print(f"模块列表: {', '.join(loaded_modules)}")
    print("\n" + "=" * 80)
    
    # 运行测试
    runner = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=verbosity
    )
    
    print("🔄 开始执行基本功能测试...\n")
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    return result, duration, loaded_modules


def print_test_summary(result, duration, modules):
    """打印测试总结"""
    print("\n" + "=" * 80)
    print("📊 基本功能测试结果")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"⏱️  总耗时: {duration:.2f} 秒")
    print(f"🧪 总测试数: {total_tests}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failures}")
    print(f"🔥 错误: {errors}")
    print(f"⏭️  跳过: {skipped}")
    print(f"📈 成功率: {success_rate:.1f}%")
    
    print(f"\n📋 测试模块: {', '.join(modules)}")
    
    # 失败和错误概述
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for i, (test, traceback) in enumerate(result.failures[:3], 1):  # 只显示前3个
            print(f"  {i}. {test}")
    
    if result.errors:
        print(f"\n🔥 错误的测试:")
        for i, (test, traceback) in enumerate(result.errors[:3], 1):  # 只显示前3个
            print(f"  {i}. {test}")
    
    # 总结
    print("\n" + "=" * 80)
    if failures == 0 and errors == 0:
        print("🎉 所有基本功能测试通过！")
        status = "✅ 成功"
    else:
        print(f"⚠️  发现 {failures + errors} 个问题")
        status = "⚠️ 部分失败"
    
    print(f"状态: {status}")
    print("=" * 80)
    
    return failures + errors == 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='运行基本功能测试')
    parser.add_argument('-v', '--verbosity', type=int, default=2, choices=[0, 1, 2],
                       help='输出详细程度 (0=静默, 1=正常, 2=详细)')
    
    args = parser.parse_args()
    
    try:
        # 检查服务是否运行
        import requests
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务运行正常")
            else:
                print("⚠️  警告: 后端服务响应异常")
        except requests.exceptions.ConnectionError:
            print("❌ 错误: 无法连接到后端服务 (http://localhost:8000)")
            print("请确保后端服务正在运行，然后重新执行测试")
            return 1
        except requests.exceptions.Timeout:
            print("⚠️  警告: 后端服务响应超时")
        
        # 运行测试
        result, duration, modules = discover_and_run_tests(args.verbosity)
        
        # 打印结果
        success = print_test_summary(result, duration, modules)
        
        # 返回适当的退出代码
        return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n💥 测试运行器发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
