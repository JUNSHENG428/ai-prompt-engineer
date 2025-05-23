#!/usr/bin/env python
"""
API密钥管理模块

这个模块提供了安全获取API密钥的方法，按照以下优先级：
1. 环境变量
2. .env文件
3. Streamlit secrets
4. config.json文件
5. 用户交互输入
"""

import os
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Any

# 尝试导入dotenv，如果安装了的话
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# 尝试导入streamlit，如果安装了的话
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def get_api_key(provider: str = "deepseek") -> Optional[str]:
    """
    安全地获取API密钥，按照优先级顺序尝试多种方法
    
    Args:
        provider: API提供商名称 ("deepseek" 或 "openai")
        
    Returns:
        API密钥字符串或None（如果找不到）
    """
    env_var_name = f"{provider.upper()}_API_KEY"
    
    # 1. 首先检查环境变量
    api_key = os.environ.get(env_var_name)
    if api_key:
        print(f"✓ 已从环境变量加载 {provider} API密钥")
        return api_key
    
    # 2. 尝试从.env文件加载
    if DOTENV_AVAILABLE:
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv()
            api_key = os.getenv(env_var_name)
            if api_key:
                print(f"✓ 已从.env文件加载 {provider} API密钥")
                return api_key
    
    # 3. 尝试从Streamlit secrets加载
    if STREAMLIT_AVAILABLE:
        try:
            api_key = st.secrets.get(env_var_name)
            if api_key:
                print(f"✓ 已从Streamlit secrets加载 {provider} API密钥")
                return api_key
        except:
            pass  # Streamlit secrets不可用或未配置
    
    # 4. 尝试从config.json加载
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                api_key = config.get("api_key")
                if api_key:
                    print(f"✓ 已从config.json加载API密钥")
                    return api_key
        except Exception as e:
            print(f"无法从config.json加载: {e}")
    
    # 没有找到API密钥
    return None


def save_api_key(api_key: str, provider: str = "deepseek", method: str = "env") -> bool:
    """
    保存API密钥到指定位置
    
    Args:
        api_key: 要保存的API密钥
        provider: API提供商名称
        method: 保存方法 ("env", "dotenv", "config", "streamlit")
        
    Returns:
        是否成功保存
    """
    env_var_name = f"{provider.upper()}_API_KEY"
    
    if method == "env":
        # 仅打印指导，不实际设置环境变量（因为Python无法永久设置环境变量）
        if os.name == "posix":  # Linux/Mac
            print(f"\n在终端执行以下命令设置环境变量:\n")
            print(f"echo 'export {env_var_name}=\"{api_key}\"' >> ~/.bashrc")
            print(f"source ~/.bashrc\n")
        else:  # Windows
            print(f"\n在命令提示符执行以下命令设置环境变量:\n")
            print(f"setx {env_var_name} \"{api_key}\"\n")
        return True
        
    elif method == "dotenv" and DOTENV_AVAILABLE:
        # 创建或更新.env文件
        env_content = ""
        env_path = Path(".env")
        
        # 如果文件存在，先读取内容
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # 过滤掉已有的同名环境变量
                env_content = "".join([line for line in lines if not line.startswith(f"{env_var_name}=")])
        
        # 添加新的环境变量
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"{env_content}\n{env_var_name}=\"{api_key}\"\n")
            
        print(f"✓ API密钥已保存到 .env 文件")
        return True
        
    elif method == "config":
        # 保存到config.json
        config = {}
        config_path = Path("config.json")
        
        # 如果文件存在，先读取内容
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                pass
        
        # 更新API密钥
        config["api_key"] = api_key
        config["api_provider"] = provider
        
        # 写入文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"✓ API密钥已保存到 config.json 文件")
        return True
        
    elif method == "streamlit" and STREAMLIT_AVAILABLE:
        # 创建Streamlit secrets目录和文件
        secrets_dir = Path(".streamlit")
        secrets_dir.mkdir(exist_ok=True)
        
        secrets_path = secrets_dir / "secrets.toml"
        secrets_content = ""
        
        # 如果文件存在，先读取内容
        if secrets_path.exists():
            with open(secrets_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # 过滤掉已有的同名密钥
                secrets_content = "".join([line for line in lines if not line.startswith(f"{env_var_name} =")])
        
        # 添加新的密钥
        with open(secrets_path, "w", encoding="utf-8") as f:
            f.write(f"{secrets_content}\n{env_var_name} = \"{api_key}\"\n")
            
        print(f"✓ API密钥已保存到 .streamlit/secrets.toml 文件")
        return True
    
    # 如果没有合适的方法
    return False


def prompt_for_api_key(provider: str = "deepseek") -> Optional[str]:
    """
    通过命令行提示用户输入API密钥
    
    Args:
        provider: API提供商名称
        
    Returns:
        用户输入的API密钥或None（如果用户取消）
    """
    print(f"\n未找到 {provider.upper()} API密钥。")
    print(f"您可以从 {get_provider_url(provider)} 获取API密钥\n")
    
    try:
        # 使用getpass隐藏输入内容
        api_key = getpass.getpass(f"请输入您的 {provider.upper()} API密钥 (输入内容将被隐藏): ")
        
        if not api_key:
            print("未输入API密钥，操作取消")
            return None
            
        # 询问是否保存
        save_choice = input("是否保存此API密钥以便下次使用? (y/n): ").strip().lower()
        
        if save_choice == 'y':
            # 选择保存方法
            print("\n选择保存API密钥的方法:")
            print("1. 环境变量 (推荐，最安全)")
            if DOTENV_AVAILABLE:
                print("2. .env文件 (方便但不要上传到Git)")
            print("3. config.json (不推荐用于生产环境)")
            if STREAMLIT_AVAILABLE:
                print("4. Streamlit secrets (适用于Streamlit应用)")
                
            method_choice = input("\n请选择 (1-4): ").strip()
            
            # 映射选择到方法
            method_map = {
                "1": "env",
                "2": "dotenv" if DOTENV_AVAILABLE else None,
                "3": "config",
                "4": "streamlit" if STREAMLIT_AVAILABLE else None
            }
            
            if method_choice in method_map and method_map[method_choice]:
                save_api_key(api_key, provider, method_map[method_choice])
            else:
                print("选择无效，API密钥未保存")
        
        return api_key
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def get_provider_url(provider: str) -> str:
    """返回API提供商的网站URL"""
    provider_urls = {
        "deepseek": "https://platform.deepseek.com",
        "openai": "https://platform.openai.com/api-keys",
        "claude": "https://console.anthropic.com/settings/keys",
    }
    return provider_urls.get(provider.lower(), "提供商官方网站")


def get_api_config() -> Dict[str, Any]:
    """
    获取完整的API配置
    
    Returns:
        包含API配置的字典
    """
    config = {
        "api_key": None,
        "api_provider": "deepseek",
        "model": "deepseek-chat"
    }
    
    # 尝试从config.json加载完整配置
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            print(f"无法从config.json加载配置: {e}")
    
    # 确保API密钥是最新的
    config["api_key"] = get_api_key(config["api_provider"])
    
    return config


def create_config_template():
    """创建不含真实API密钥的配置模板文件"""
    template = {
        "api_key": "YOUR_API_KEY_HERE",
        "api_provider": "deepseek",
        "model": "deepseek-chat",
        "default_format": "standard",
        "language": "zh"
    }
    
    with open("config.template.json", "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print("✓ 已创建配置模板文件 config.template.json")


if __name__ == "__main__":
    # 如果直接运行这个脚本，提供简单的API密钥管理界面
    import argparse
    
    parser = argparse.ArgumentParser(description="API密钥管理工具")
    parser.add_argument("--set", help="设置API密钥", action="store_true")
    parser.add_argument("--get", help="获取当前API密钥", action="store_true")
    parser.add_argument("--provider", help="API提供商 (deepseek, openai, or claude)", 
                        choices=['deepseek', 'openai', 'claude'], default="deepseek")
    parser.add_argument("--create-template", help="创建配置模板文件", action="store_true")
    
    args = parser.parse_args()
    
    if args.set:
        api_key = prompt_for_api_key(args.provider)
        if api_key:
            print(f"API密钥已设置")
    
    elif args.get:
        api_key = get_api_key(args.provider)
        if api_key:
            # 只显示部分API密钥作为安全措施
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
            print(f"当前{args.provider.upper()}的API密钥: {masked_key}")
        else:
            print(f"未找到{args.provider.upper()}的API密钥")
    
    elif args.create_template:
        create_config_template()
    
    else:
        parser.print_help() 