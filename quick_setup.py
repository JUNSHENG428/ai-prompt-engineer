#!/usr/bin/env python3
"""
快速设置脚本
帮助用户快速配置AI提示工程师项目
"""

import os
import sys
import json
from pathlib import Path

def create_streamlit_secrets():
    """创建Streamlit secrets配置"""
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    secrets_file = streamlit_dir / "secrets.toml"
    
    if secrets_file.exists():
        print(f"✅ Streamlit secrets文件已存在: {secrets_file}")
        return
    
    secrets_content = '''# Streamlit Secrets Configuration
# 这个文件用于安全地存储API密钥和其他敏感信息
# 请不要将包含真实密钥的文件提交到版本控制

# OpenAI API配置
# OPENAI_API_KEY = "your_openai_api_key_here"

# DeepSeek API配置  
# DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# Anthropic Claude API配置
# ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

# Google API配置
# GOOGLE_API_KEY = "your_google_api_key_here"

# 使用说明：
# 1. 取消注释相应的行并填入您的真实API密钥
# 2. 确保此文件已添加到.gitignore中
# 3. 重启Streamlit应用以加载新的配置
'''
    
    with open(secrets_file, 'w', encoding='utf-8') as f:
        f.write(secrets_content)
    
    print(f"✅ 已创建Streamlit secrets模板: {secrets_file}")

def create_env_file():
    """创建.env文件模板"""
    env_file = Path(".env")
    
    if env_file.exists():
        print(f"✅ .env文件已存在: {env_file}")
        return
    
    env_content = '''# 环境变量配置
# 这个文件用于存储API密钥和其他配置
# 请不要将包含真实密钥的文件提交到版本控制

# OpenAI API密钥
# OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek API密钥
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Anthropic Claude API密钥
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API密钥
# GOOGLE_API_KEY=your_google_api_key_here

# 使用说明：
# 1. 取消注释相应的行并填入您的真实API密钥
# 2. 在终端中运行: source .env (Linux/macOS) 或使用python-dotenv加载
'''
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ 已创建.env模板文件: {env_file}")

def create_config_template():
    """创建config.json模板"""
    config_file = Path("config.json")
    
    if config_file.exists():
        print(f"✅ config.json文件已存在: {config_file}")
        return
    
    config_data = {
        "api_key": "",
        "api_provider": "deepseek",
        "model": "deepseek-chat",
        "default_format": "standard",
        "language": "zh",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已创建config.json模板: {config_file}")

def check_gitignore():
    """检查.gitignore配置"""
    gitignore_file = Path(".gitignore")
    
    if not gitignore_file.exists():
        print("⚠️ 未找到.gitignore文件")
        return
    
    with open(gitignore_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_entries = [
        ".env",
        "config.json",
        ".streamlit/secrets.toml"
    ]
    
    missing_entries = []
    for entry in required_entries:
        if entry not in content:
            missing_entries.append(entry)
    
    if missing_entries:
        print(f"⚠️ .gitignore缺少以下条目: {', '.join(missing_entries)}")
        print("请手动添加这些条目以防止敏感信息泄露")
    else:
        print("✅ .gitignore配置正确")

def interactive_setup():
    """交互式设置"""
    print("🚀 AI提示工程师 - 快速设置")
    print("=" * 50)
    
    print("\n1. 创建配置文件模板...")
    create_streamlit_secrets()
    create_env_file()
    create_config_template()
    
    print("\n2. 检查安全配置...")
    check_gitignore()
    
    print("\n3. 设置API密钥")
    print("您可以选择以下任一方式设置API密钥：")
    print("   a) 编辑 .streamlit/secrets.toml 文件")
    print("   b) 编辑 .env 文件")
    print("   c) 设置环境变量")
    print("   d) 在Streamlit应用中直接输入")
    print("   e) 使用安全API管理器: python secure_api_manager.py --set")
    
    choice = input("\n请选择设置方式 (a/b/c/d/e) 或按Enter跳过: ").lower().strip()
    
    if choice == 'a':
        print(f"\n请编辑文件: .streamlit/secrets.toml")
        print("取消注释相应的行并填入您的API密钥")
    elif choice == 'b':
        print(f"\n请编辑文件: .env")
        print("取消注释相应的行并填入您的API密钥")
    elif choice == 'c':
        provider = input("请选择API提供商 (deepseek/openai): ").lower().strip()
        if provider in ['deepseek', 'openai']:
            env_var = f"{provider.upper()}_API_KEY"
            print(f"\n请在终端中运行:")
            print(f"export {env_var}='your_api_key_here'")
        else:
            print("无效的提供商选择")
    elif choice == 'd':
        print("\n启动应用后，在侧边栏中输入API密钥")
    elif choice == 'e':
        print("\n请运行: python secure_api_manager.py --set --provider your_provider")
    
    print("\n4. 启动应用")
    print("运行以下命令启动应用:")
    print("streamlit run streamlit_app.py")
    
    print("\n✅ 设置完成！")
    print("如果遇到问题，请查看README.md中的详细说明")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # 自动模式，只创建文件
        create_streamlit_secrets()
        create_env_file()
        create_config_template()
        check_gitignore()
        print("✅ 自动设置完成")
    else:
        # 交互模式
        interactive_setup()

if __name__ == "__main__":
    main() 