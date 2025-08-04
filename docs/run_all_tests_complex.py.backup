#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一测试运行器
运行所有unittest测试用例并统计结果
"""

import unittest
import sys
import os
import time
from pathlib import Path
from io import StringIO
import yaml

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))


class TestResult:
    """测试结果统计"""
    
    def __init__(self):
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_skipped = 0
        self.module_results = {}
        self.start_time = None
        self.end_time = None
    
    @property
    def total_passed(self):
        return self.total_tests - self.total_failures - self.total_errors - self.total_skipped
    
    @property
    def success_rate(self):
        if self.total_tests == 0:
            return 0
        return (self.total_passed / self.total_tests) * 100
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0


def discover_and_run_tests(verbosity=2):
    """发现并运行所有测试"""
    print("🚀 私人金融分析师 - 统一测试套件")
    print("=" * 80)
    
    # 创建测试结果对象
    test_result = TestResult()
    test_result.start_time = time.time()
    
    # 发现所有测试模块
    test_modules = [
        'tests.auth.case.test_auth_unittest',
        'tests.stocks.case.test_stocks_unittest', 
        'tests.assistant.case.test_assistant_unittest',
        'tests.users.case.test_users_unittest',
        'tests.system.case.test_system_unittest'
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
    
    print(f"\n📊 共加载 {len(loaded_modules)} 个测试模块")
    print(f"模块列表: {', '.join(loaded_modules)}")
    print("\n" + "=" * 80)
    
    # 运行测试
    runner = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=verbosity
    )
    
    print("🔄 开始执行测试...\n")
    result = runner.run(suite)
    
    # 统计结果
    test_result.total_tests = result.testsRun
    test_result.total_failures = len(result.failures)
    test_result.total_errors = len(result.errors)
    test_result.total_skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    test_result.end_time = time.time()
    
    # 按模块统计
    for test_case in result.failures + result.errors:
        test = test_case[0]
        module_name = test.__class__.__module__.split('.')[1] if '.' in test.__class__.__module__ else 'unknown'
        if module_name not in test_result.module_results:
            test_result.module_results[module_name] = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
        
        if test_case in result.failures:
            test_result.module_results[module_name]['failures'] += 1
        else:
            test_result.module_results[module_name]['errors'] += 1
    
    return test_result, result


def print_detailed_results(test_result, unittest_result):
    """打印详细测试结果"""
    print("\n" + "=" * 80)
    print("📊 详细测试结果统计")
    print("=" * 80)
    
    # 总体统计
    print(f"⏱️  总耗时: {test_result.duration:.2f} 秒")
    print(f"🧪 总测试数: {test_result.total_tests}")
    print(f"✅ 通过: {test_result.total_passed}")
    print(f"❌ 失败: {test_result.total_failures}")
    print(f"🔥 错误: {test_result.total_errors}")
    print(f"⏭️  跳过: {test_result.total_skipped}")
    print(f"📈 成功率: {test_result.success_rate:.1f}%")
    
    # 失败和错误概述
    if unittest_result.failures:
        print(f"\n❌ 失败测试 ({len(unittest_result.failures)} 个):")
        for i, (test, traceback) in enumerate(unittest_result.failures[:5], 1):  # 只显示前5个
            print(f"  {i}. {test}")
    
    if unittest_result.errors:
        print(f"\n🔥 错误测试 ({len(unittest_result.errors)} 个):")
        for i, (test, traceback) in enumerate(unittest_result.errors[:5], 1):  # 只显示前5个
            print(f"  {i}. {test}")
    
    # 总结
    print("\n" + "=" * 80)
    if test_result.total_failures == 0 and test_result.total_errors == 0:
        print("🎉 所有测试通过！系统功能正常！")
        status = "✅ 成功"
    else:
        print(f"⚠️  发现 {test_result.total_failures + test_result.total_errors} 个问题，请检查相关功能")
        status = "⚠️ 部分失败"
    
    print(f"状态: {status}")
    print("=" * 80)


def save_test_report(test_result, unittest_result):
    """保存测试报告"""
    report_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_tests': test_result.total_tests,
            'passed': test_result.total_passed,
            'failed': test_result.total_failures,
            'errors': test_result.total_errors,
            'skipped': test_result.total_skipped,
            'success_rate': test_result.success_rate,
            'duration': test_result.duration
        },
        'modules': test_result.module_results,
        'failures': [
            {
                'test': str(test),
                'error': traceback
            }
            for test, traceback in unittest_result.failures
        ],
        'errors': [
            {
                'test': str(test),
                'error': traceback
            }
            for test, traceback in unittest_result.errors
        ]
    }
    
    # 保存为YAML格式
    report_file = f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.yaml"
    with open(report_file, 'w', encoding='utf-8') as f:
        yaml.dump(report_data, f, default_flow_style=False, allow_unicode=True)
    
    print(f"📄 测试报告已保存: {report_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='运行所有unittest测试')
    parser.add_argument('-v', '--verbosity', type=int, default=2, choices=[0, 1, 2],
                       help='输出详细程度 (0=静默, 1=正常, 2=详细)')
    parser.add_argument('-s', '--save-report', action='store_true',
                       help='保存测试报告到文件')
    
    args = parser.parse_args()
    
    try:
        # 检查服务是否运行
        import requests
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code != 200:
                print("⚠️  警告: 后端服务可能未正常运行")
            else:
                print("✅ 后端服务运行正常")
        except requests.exceptions.ConnectionError:
            print("❌ 错误: 无法连接到后端服务 (http://localhost:8000)")
            print("请确保后端服务正在运行，然后重新执行测试")
            return 1
        except requests.exceptions.Timeout:
            print("⚠️  警告: 后端服务响应超时")
        
        # 运行测试
        test_result, unittest_result = discover_and_run_tests(args.verbosity)
        
        # 打印结果
        print_detailed_results(test_result, unittest_result)
        
        # 保存报告
        if args.save_report:
            save_test_report(test_result, unittest_result)
        
        # 返回适当的退出代码
        if test_result.total_failures > 0 or test_result.total_errors > 0:
            return 1
        else:
            return 0
            
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
