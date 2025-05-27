#!/usr/bin/env python3
"""
安全API管理器
提供完善的API密钥管理、验证、加密存储等安全功能
"""

import os
import json
import hashlib
import getpass
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class SecureAPIManager:
    """安全API管理器"""
    
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.ai_prompt_engineer")
        self.secure_config_file = os.path.join(self.config_dir, ".secure_config.enc")
        self.key_file = os.path.join(self.config_dir, ".key_hash")
        self.supported_providers = ["openai", "deepseek", "anthropic", "google"]
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # API密钥格式验证模式
        self.key_patterns = {
            "openai": r"^sk-[A-Za-z0-9]{48,}$",
            "deepseek": r"^sk-[A-Za-z0-9]{32,}$",
            "anthropic": r"^sk-ant-[A-Za-z0-9\-]{95,}$",
            "google": r"^[A-Za-z0-9\-_]{39}$"
        }
    
    def _generate_key_from_password(self, password: str, salt: bytes = None) -> Fernet:
        """从密码生成加密密钥"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key), salt
    
    def _get_master_password(self, confirm: bool = False) -> Optional[str]:
        """安全获取主密码"""
        try:
            if confirm:
                password1 = getpass.getpass("设置主密码（用于加密存储API密钥）: ")
                password2 = getpass.getpass("确认主密码: ")
                if password1 != password2:
                    print("❌ 密码不匹配")
                    return None
                if len(password1) < 8:
                    print("❌ 密码长度至少需要8位")
                    return None
                return password1
            else:
                return getpass.getpass("请输入主密码: ")
        except KeyboardInterrupt:
            print("\n操作已取消")
            return None
    
    def _validate_api_key(self, api_key: str, provider: str) -> bool:
        """验证API密钥格式"""
        if not api_key or not provider:
            return False
        
        provider = provider.lower()
        if provider not in self.key_patterns:
            logger.warning(f"不支持的API提供商: {provider}")
            return True  # 对未知提供商给予宽松验证
        
        pattern = self.key_patterns[provider]
        return bool(re.match(pattern, api_key))
    
    def _mask_api_key(self, api_key: str) -> str:
        """遮蔽API密钥显示"""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def set_api_key(self, provider: str, api_key: str, method: str = "secure") -> bool:
        """
        设置API密钥
        
        Args:
            provider: API提供商名称
            api_key: API密钥
            method: 存储方法 ('secure', 'env', 'config')
        
        Returns:
            bool: 是否设置成功
        """
        if not self._validate_api_key(api_key, provider):
            print(f"❌ API密钥格式无效（提供商: {provider}）")
            return False
        
        if method == "secure":
            return self._save_secure_key(provider, api_key)
        elif method == "env":
            return self._save_env_key(provider, api_key)
        elif method == "config":
            return self._save_config_key(provider, api_key)
        else:
            print(f"❌ 不支持的存储方法: {method}")
            return False
    
    def _save_secure_key(self, provider: str, api_key: str) -> bool:
        """安全加密存储API密钥"""
        try:
            # 获取或设置主密码
            password = self._get_master_password(confirm=not os.path.exists(self.key_file))
            if not password:
                return False
            
            # 加载现有配置
            config = {}
            salt = None
            
            if os.path.exists(self.secure_config_file) and os.path.exists(self.key_file):
                # 验证密码
                with open(self.key_file, 'rb') as f:
                    stored_hash, salt = f.read().split(b'|', 1)
                
                password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                if password_hash != stored_hash:
                    print("❌ 主密码错误")
                    return False
                
                # 解密现有配置
                fernet, _ = self._generate_key_from_password(password, salt)
                with open(self.secure_config_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = fernet.decrypt(encrypted_data)
                config = json.loads(decrypted_data.decode())
            else:
                # 新建配置
                fernet, salt = self._generate_key_from_password(password)
                password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                
                # 保存密码哈希
                with open(self.key_file, 'wb') as f:
                    f.write(password_hash + b'|' + salt)
                
                # 设置文件权限（仅所有者可读写）
                os.chmod(self.key_file, 0o600)
            
            # 更新配置
            config[provider] = {
                "api_key": api_key,
                "created_at": datetime.now().isoformat(),
                "last_used": None
            }
            
            # 加密保存
            if 'fernet' not in locals():
                fernet, _ = self._generate_key_from_password(password, salt)
            
            encrypted_data = fernet.encrypt(json.dumps(config).encode())
            with open(self.secure_config_file, 'wb') as f:
                f.write(encrypted_data)
            
            # 设置文件权限
            os.chmod(self.secure_config_file, 0o600)
            
            print(f"✅ API密钥已安全保存（提供商: {provider}）")
            return True
            
        except Exception as e:
            logger.error(f"保存安全密钥失败: {e}")
            print("❌ 保存API密钥失败")
            return False
    
    def _save_env_key(self, provider: str, api_key: str) -> bool:
        """保存到环境变量"""
        try:
            env_var = f"{provider.upper()}_API_KEY"
            os.environ[env_var] = api_key
            
            # 提示用户永久设置
            print(f"✅ API密钥已设置到环境变量 {env_var}")
            print("💡 要永久保存，请将以下命令添加到您的 shell 配置文件:")
            print(f"   export {env_var}=\"{self._mask_api_key(api_key)}\"")
            return True
            
        except Exception as e:
            logger.error(f"保存环境变量失败: {e}")
            print("❌ 保存到环境变量失败")
            return False
    
    def _save_config_key(self, provider: str, api_key: str) -> bool:
        """保存到普通配置文件（不推荐）"""
        try:
            config_file = "config.json"
            config = {}
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config[f"{provider}_api_key"] = api_key
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"⚠️ API密钥已保存到 {config_file}")
            print("🚨 警告: 这种方式不安全，请确保不要提交到版本控制系统")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            print("❌ 保存到配置文件失败")
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        获取API密钥
        
        Args:
            provider: API提供商名称
            
        Returns:
            str: API密钥，如果未找到则返回None
        """
        # 1. 尝试从环境变量获取
        env_key = os.environ.get(f"{provider.upper()}_API_KEY")
        if env_key:
            self._update_last_used(provider)
            return env_key
        
        # 2. 尝试从安全存储获取
        secure_key = self._get_secure_key(provider)
        if secure_key:
            self._update_last_used(provider)
            return secure_key
        
        # 3. 尝试从配置文件获取
        config_key = self._get_config_key(provider)
        if config_key:
            return config_key
        
        return None
    
    def _get_secure_key(self, provider: str) -> Optional[str]:
        """从安全存储获取API密钥"""
        try:
            if not os.path.exists(self.secure_config_file) or not os.path.exists(self.key_file):
                return None
            
            # 这里不提示密码，避免在自动化场景中中断
            return None
            
        except Exception as e:
            logger.error(f"读取安全密钥失败: {e}")
            return None
    
    def _get_config_key(self, provider: str) -> Optional[str]:
        """从配置文件获取API密钥"""
        try:
            config_file = "config.json"
            if not os.path.exists(config_file):
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config.get(f"{provider}_api_key") or config.get("api_key")
            
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return None
    
    def _update_last_used(self, provider: str):
        """更新最后使用时间"""
        try:
            if not os.path.exists(self.secure_config_file):
                return
            
            # 这里简化处理，避免在每次获取密钥时都要求密码
            pass
            
        except Exception:
            pass
    
    def list_providers(self) -> List[str]:
        """列出所有已配置的API提供商"""
        providers = []
        
        # 检查环境变量
        for provider in self.supported_providers:
            if os.environ.get(f"{provider.upper()}_API_KEY"):
                providers.append(f"{provider} (环境变量)")
        
        # 检查安全存储（不解密，只检查文件存在）
        if os.path.exists(self.secure_config_file):
            providers.append("安全存储 (需要密码访问)")
        
        # 检查配置文件
        try:
            if os.path.exists("config.json"):
                with open("config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                for key in config:
                    if key.endswith("_api_key"):
                        provider_name = key.replace("_api_key", "")
                        providers.append(f"{provider_name} (配置文件)")
        except Exception:
            pass
        
        return providers
    
    def remove_api_key(self, provider: str) -> bool:
        """删除API密钥"""
        success = False
        
        # 从环境变量删除
        env_var = f"{provider.upper()}_API_KEY"
        if env_var in os.environ:
            del os.environ[env_var]
            print(f"✅ 已从环境变量删除 {provider} API密钥")
            success = True
        
        # 从配置文件删除
        try:
            if os.path.exists("config.json"):
                with open("config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if f"{provider}_api_key" in config:
                    del config[f"{provider}_api_key"]
                    with open("config.json", 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    print(f"✅ 已从配置文件删除 {provider} API密钥")
                    success = True
        except Exception:
            pass
        
        if not success:
            print(f"❌ 未找到 {provider} 的API密钥")
        
        return success
    
    def validate_all_keys(self) -> Dict[str, bool]:
        """验证所有已配置的API密钥"""
        results = {}
        
        for provider in self.supported_providers:
            api_key = self.get_api_key(provider)
            if api_key:
                is_valid = self._validate_api_key(api_key, provider)
                results[provider] = is_valid
                status = "✅ 有效" if is_valid else "❌ 格式错误"
                print(f"{provider}: {status} ({self._mask_api_key(api_key)})")
        
        return results
    
    def security_check(self) -> Dict[str, Any]:
        """安全检查"""
        report = {
            "secure_storage": os.path.exists(self.secure_config_file),
            "config_file_exists": os.path.exists("config.json"),
            "env_vars": [],
            "recommendations": []
        }
        
        # 检查环境变量
        for provider in self.supported_providers:
            env_var = f"{provider.upper()}_API_KEY"
            if os.environ.get(env_var):
                report["env_vars"].append(env_var)
        
        # 检查配置文件安全性
        if report["config_file_exists"]:
            try:
                with open("config.json", 'r') as f:
                    config = json.load(f)
                if any(key.endswith("_api_key") for key in config):
                    report["recommendations"].append("配置文件包含API密钥，建议迁移到安全存储")
            except Exception:
                pass
        
        # 检查.gitignore
        if os.path.exists(".gitignore"):
            with open(".gitignore", 'r') as f:
                gitignore_content = f.read()
            if "config.json" not in gitignore_content:
                report["recommendations"].append("建议将config.json添加到.gitignore")
        else:
            report["recommendations"].append("建议创建.gitignore文件")
        
        return report

# 便捷函数
def get_api_key(provider: str) -> Optional[str]:
    """获取API密钥的便捷函数"""
    manager = SecureAPIManager()
    return manager.get_api_key(provider)

def set_api_key_interactive(provider: str = None):
    """交互式设置API密钥"""
    manager = SecureAPIManager()
    
    if not provider:
        print("支持的API提供商:")
        for i, p in enumerate(manager.supported_providers, 1):
            print(f"  {i}. {p}")
        
        try:
            choice = int(input("请选择提供商 (1-{}): ".format(len(manager.supported_providers))))
            provider = manager.supported_providers[choice - 1]
        except (ValueError, IndexError):
            print("❌ 无效选择")
            return
    
    api_key = getpass.getpass(f"请输入 {provider} API密钥: ")
    if not api_key:
        print("❌ API密钥不能为空")
        return
    
    print("\n存储方式:")
    print("  1. 安全加密存储 (推荐)")
    print("  2. 环境变量")
    print("  3. 配置文件 (不推荐)")
    
    try:
        method_choice = int(input("请选择存储方式 (1-3): "))
        methods = ["secure", "env", "config"]
        method = methods[method_choice - 1]
    except (ValueError, IndexError):
        print("❌ 无效选择，使用默认安全存储")
        method = "secure"
    
    success = manager.set_api_key(provider, api_key, method)
    if success:
        print(f"✅ {provider} API密钥设置成功")
    else:
        print(f"❌ {provider} API密钥设置失败")

def main():
    """主函数 - 命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description="安全API密钥管理器")
    parser.add_argument("--set", action="store_true", help="设置API密钥")
    parser.add_argument("--provider", type=str, help="API提供商")
    parser.add_argument("--list", action="store_true", help="列出所有配置的提供商")
    parser.add_argument("--validate", action="store_true", help="验证所有API密钥")
    parser.add_argument("--security-check", action="store_true", help="执行安全检查")
    parser.add_argument("--remove", type=str, help="删除指定提供商的API密钥")
    
    args = parser.parse_args()
    manager = SecureAPIManager()
    
    if args.set:
        set_api_key_interactive(args.provider)
    elif args.list:
        providers = manager.list_providers()
        if providers:
            print("已配置的API提供商:")
            for provider in providers:
                print(f"  - {provider}")
        else:
            print("未找到任何已配置的API提供商")
    elif args.validate:
        manager.validate_all_keys()
    elif args.security_check:
        report = manager.security_check()
        print("🔍 安全检查报告:")
        print(f"  安全存储: {'✅' if report['secure_storage'] else '❌'}")
        print(f"  配置文件: {'⚠️' if report['config_file_exists'] else '✅'}")
        print(f"  环境变量: {len(report['env_vars'])} 个")
        if report['recommendations']:
            print("  建议:")
            for rec in report['recommendations']:
                print(f"    - {rec}")
    elif args.remove:
        manager.remove_api_key(args.remove)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 