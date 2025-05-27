#!/usr/bin/env python3
"""
测试安全扫描器功能
"""

import os
import tempfile
import shutil
from pathlib import Path
from security_scanner import SecurityScanner

def create_test_files(test_dir: Path):
    """创建测试文件"""
    # 创建包含API密钥的文件
    with open(test_dir / "api_config.py", "w") as f:
        f.write("""
# 配置文件
API_KEY = "sk-test_fake_key_for_testing_only_not_real"
  OPENAI_KEY = "sk-proj-test_fake_key_for_testing_only"
DATABASE_URL = "postgresql://user:password123@localhost:5432/mydb"
""")
    
    # 创建.env文件（应该被忽略）
    with open(test_dir / ".env", "w") as f:
        f.write("""
OPENAI_API_KEY=sk-test_fake_key_for_testing_only_not_real
DATABASE_PASSWORD=secret123
""")
    
    # 创建配置文件
    with open(test_dir / "config.json", "w") as f:
        f.write("""
{
      "api_key": "sk-test_fake_key_for_testing_only",
              "secret_token": "ghp_test_fake_token_for_testing_only"
}
""")
    
    # 创建示例文件（不应该报告）
    with open(test_dir / "examples.py", "w") as f:
        f.write("""
# 示例代码
# 请将your_api_key_here替换为实际的API密钥
API_KEY = "your_api_key_here"  # 示例
# TEST_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
""")
    
    # 创建不完整的.gitignore
    with open(test_dir / ".gitignore", "w") as f:
        f.write("""
__pycache__/
*.pyc
""")
    
    # 创建requirements.txt（有未固定版本）
    with open(test_dir / "requirements.txt", "w") as f:
        f.write("""
requests>=2.25.0
numpy>=1.20.0
flask==2.0.1
""")
    
    # 创建私钥文件
    key_file = test_dir / "private.key"
    with open(key_file, "w") as f:
        f.write("""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----""")
    
    # 设置错误的权限
    os.chmod(key_file, 0o644)

def test_security_scanner():
    """测试安全扫描器"""
    print("🧪 开始测试安全扫描器...")
    
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建测试文件
        create_test_files(test_dir)
        
        # 运行安全扫描
        scanner = SecurityScanner(str(test_dir))
        report = scanner.scan_project()
        
        # 验证结果
        print(f"\n📊 扫描结果:")
        print(f"总问题数: {len(report.issues)}")
        print(f"严重问题: {report.summary.get('critical', 0)}")
        print(f"高危问题: {report.summary.get('high', 0)}")
        print(f"中危问题: {report.summary.get('medium', 0)}")
        print(f"低危问题: {report.summary.get('low', 0)}")
        
        # 检查是否发现了预期的问题类型
        categories = [issue.category for issue in report.issues]
        
        expected_categories = [
            "secret_leak",      # API密钥泄露
            "incomplete_gitignore",  # 不完整的.gitignore
            "file_permission",  # 文件权限问题
            "dependency_security",  # 依赖安全
            "config_secrets"    # 配置文件敏感信息
        ]
        
        found_categories = set(categories)
        print(f"\n🔍 发现的问题类型: {', '.join(found_categories)}")
        
        success = True
        for expected in expected_categories:
            if expected in found_categories:
                print(f"✅ 成功检测: {expected}")
            else:
                print(f"❌ 未检测到: {expected}")
                success = False
        
        # 验证示例代码未被误报
        example_issues = [issue for issue in report.issues 
                         if "examples.py" in issue.file_path]
        if example_issues:
            print(f"❌ 误报示例代码: {len(example_issues)} 个")
            success = False
        else:
            print("✅ 正确忽略示例代码")
        
        # 打印详细报告
        print("\n" + "="*50)
        scanner.print_report(report)
        
        return success

def test_gitignore_creation():
    """测试.gitignore模板创建"""
    print("\n🧪 测试.gitignore模板创建...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        from security_scanner import create_gitignore_template
        
        gitignore_content = create_gitignore_template()
        gitignore_path = test_dir / ".gitignore"
        
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        # 验证内容
        required_entries = [
            ".env", "config.json", "*.key", "*.pem",
            "__pycache__/", ".DS_Store"
        ]
        
        success = True
        for entry in required_entries:
            if entry in gitignore_content:
                print(f"✅ 包含: {entry}")
            else:
                print(f"❌ 缺少: {entry}")
                success = False
        
        return success

def test_fix_functionality():
    """测试自动修复功能"""
    print("\n🧪 测试自动修复功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建不完整的.gitignore
        gitignore_path = test_dir / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write("__pycache__/\n")
        
        # 创建权限错误的敏感文件
        key_file = test_dir / "secret.key"
        with open(key_file, "w") as f:
            f.write("secret content")
        os.chmod(key_file, 0o644)
        
        # 扫描
        scanner = SecurityScanner(str(test_dir))
        report = scanner.scan_project()
        
        initial_issues = len(report.issues)
        print(f"修复前问题数: {initial_issues}")
        
        # 执行修复
        from security_scanner import fix_security_issues
        fix_security_issues(report, str(test_dir))
        
        # 重新扫描
        new_report = scanner.scan_project()
        final_issues = len(new_report.issues)
        print(f"修复后问题数: {final_issues}")
        
        success = final_issues < initial_issues
        if success:
            print("✅ 自动修复功能正常")
        else:
            print("❌ 自动修复功能异常")
        
        return success

def main():
    """主测试函数"""
    print("🚀 开始测试安全扫描器")
    print("=" * 50)
    
    test_results = []
    
    # 运行测试
    test_results.append(("安全扫描功能", test_security_scanner()))
    test_results.append(("Gitignore模板", test_gitignore_creation()))
    test_results.append(("自动修复功能", test_fix_functionality()))
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📋 测试结果总结")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！安全扫描器功能正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 