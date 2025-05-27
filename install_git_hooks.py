#!/usr/bin/env python3
"""
安装Git钩子脚本
自动安装和配置安全检查钩子
"""

import os
import shutil
import stat
from pathlib import Path

def install_pre_commit_hook():
    """安装预提交钩子"""
    print("🔧 安装Git预提交钩子...")
    
    # 检查是否为Git仓库
    git_dir = Path(".git")
    if not git_dir.exists():
        print("❌ 当前目录不是Git仓库")
        return False
    
    # 创建hooks目录
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # 预提交钩子路径
    pre_commit_hook = hooks_dir / "pre-commit"
    
    # 检查是否已存在钩子
    if pre_commit_hook.exists():
        print("⚠️ 预提交钩子已存在")
        response = input("是否覆盖? (y/N): ")
        if response.lower() != 'y':
            return False
        
        # 备份现有钩子
        backup_path = pre_commit_hook.with_suffix('.backup')
        shutil.copy2(pre_commit_hook, backup_path)
        print(f"✅ 已备份现有钩子到: {backup_path}")
    
    # 复制钩子文件
    hook_source = Path("git_hooks/pre-commit")
    if not hook_source.exists():
        print("❌ 未找到钩子源文件: git_hooks/pre-commit")
        return False
    
    shutil.copy2(hook_source, pre_commit_hook)
    
    # 设置执行权限
    os.chmod(pre_commit_hook, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    
    print("✅ 预提交钩子安装成功")
    return True

def test_hook():
    """测试钩子功能"""
    print("\n🧪 测试钩子功能...")
    
    # 创建测试文件
    test_file = Path("test_security.py")
    with open(test_file, "w") as f:
        f.write('API_KEY = "sk-test1234567890abcdef1234567890abcdef1234567890"\n')
    
    try:
        # 添加到暂存区
        import subprocess
        subprocess.run(["git", "add", str(test_file)], check=True)
        
        # 运行钩子测试
        hook_path = Path(".git/hooks/pre-commit")
        if hook_path.exists():
            result = subprocess.run([str(hook_path)], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("✅ 钩子正常工作 - 成功阻止了包含敏感信息的提交")
            else:
                print("⚠️ 钩子可能未正常工作")
        else:
            print("❌ 钩子文件不存在")
        
        # 清理测试文件
        subprocess.run(["git", "reset", "HEAD", str(test_file)], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 删除测试文件
        if test_file.exists():
            test_file.unlink()

def create_hook_config():
    """创建钩子配置文件"""
    print("\n📝 创建钩子配置...")
    
    config_content = """
# Git钩子配置
# 可以在这里自定义敏感信息检查的规则

# 是否启用安全检查
ENABLE_SECURITY_CHECK=true

# 检查级别 (strict, normal, loose)
CHECK_LEVEL=normal

# 是否允许跳过检查（使用--no-verify）
ALLOW_SKIP=true

# 自定义排除模式（正则表达式）
CUSTOM_EXCLUDE_PATTERNS=

# 检查的文件类型
CHECKED_EXTENSIONS=.py,.js,.ts,.java,.json,.yaml,.yml,.env,.config
"""
    
    config_path = Path(".git_hooks_config")
    with open(config_path, "w") as f:
        f.write(config_content.strip())
    
    print(f"✅ 配置文件已创建: {config_path}")

def show_usage():
    """显示使用说明"""
    print("\n📖 使用说明:")
    print("="*50)
    print("1. 钩子已安装，将在每次git commit时自动运行")
    print("2. 如果检测到敏感信息，提交将被阻止")
    print("3. 请将敏感信息移至环境变量或安全存储")
    print()
    print("💡 有用的命令:")
    print("  - 跳过检查提交: git commit --no-verify")
    print("  - 查看暂存文件: git diff --cached --name-only")
    print("  - 手动运行检查: .git/hooks/pre-commit")
    print()
    print("🔧 维护命令:")
    print("  - 卸载钩子: rm .git/hooks/pre-commit")
    print("  - 查看钩子状态: ls -la .git/hooks/")
    print("  - 编辑钩子配置: nano .git_hooks_config")

def uninstall_hook():
    """卸载钩子"""
    print("\n🗑️ 卸载Git钩子...")
    
    pre_commit_hook = Path(".git/hooks/pre-commit")
    if pre_commit_hook.exists():
        pre_commit_hook.unlink()
        print("✅ 预提交钩子已卸载")
    else:
        print("ℹ️ 预提交钩子不存在")
    
    config_path = Path(".git_hooks_config")
    if config_path.exists():
        config_path.unlink()
        print("✅ 钩子配置已删除")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git安全钩子管理器")
    parser.add_argument("--install", action="store_true", help="安装预提交钩子")
    parser.add_argument("--uninstall", action="store_true", help="卸载预提交钩子")
    parser.add_argument("--test", action="store_true", help="测试钩子功能")
    parser.add_argument("--config", action="store_true", help="创建配置文件")
    
    args = parser.parse_args()
    
    if args.uninstall:
        uninstall_hook()
        return
    
    if args.test:
        test_hook()
        return
    
    if args.config:
        create_hook_config()
        return
    
    if args.install or not any(vars(args).values()):
        print("🛡️ Git安全钩子安装器")
        print("="*30)
        
        success = install_pre_commit_hook()
        if success:
            create_hook_config()
            test_hook()
            show_usage()
        else:
            print("❌ 安装失败")

if __name__ == "__main__":
    main() 