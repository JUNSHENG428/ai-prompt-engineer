#!/usr/bin/env python3
"""
安全扫描器
检测API密钥泄露、敏感信息暴露和其他安全风险
"""

import os
import re
import json
import subprocess
import hashlib
import stat
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class SecurityIssue:
    """安全问题描述"""
    severity: str  # critical, high, medium, low
    category: str  # api_key_leak, hardcoded_secret, file_permission, etc.
    description: str
    file_path: str = ""
    line_number: int = 0
    context: str = ""
    recommendation: str = ""

@dataclass
class SecurityReport:
    """安全扫描报告"""
    scan_time: str
    project_path: str
    issues: List[SecurityIssue] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.issues = []
        
        # API密钥和敏感信息的正则模式
        self.secret_patterns = {
            "openai_api_key": {
                "pattern": r"sk-[A-Za-z0-9]{48,}",
                "description": "OpenAI API密钥",
                "severity": "critical"
            },
            "deepseek_api_key": {
                "pattern": r"sk-[A-Za-z0-9]{32,}",
                "description": "DeepSeek API密钥",
                "severity": "critical"
            },
            "anthropic_api_key": {
                "pattern": r"sk-ant-[A-Za-z0-9\-]{95,}",
                "description": "Anthropic API密钥",
                "severity": "critical"
            },
            "google_api_key": {
                "pattern": r"AIza[A-Za-z0-9\-_]{35}",
                "description": "Google API密钥",
                "severity": "critical"
            },
            "aws_access_key": {
                "pattern": r"AKIA[A-Z0-9]{16}",
                "description": "AWS访问密钥",
                "severity": "critical"
            },
            "github_token": {
                "pattern": r"ghp_[A-Za-z0-9]{36}",
                "description": "GitHub个人访问令牌",
                "severity": "critical"
            },
            "jwt_token": {
                "pattern": r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
                "description": "JWT令牌",
                "severity": "medium"
            },
            "private_key": {
                "pattern": r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
                "description": "私钥",
                "severity": "critical"
            },
            "password": {
                "pattern": r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]{8,}['\"]?",
                "description": "硬编码密码",
                "severity": "high"
            },
            "database_url": {
                "pattern": r"(postgresql|mysql|mongodb)://[^:]+:[^@]+@[^/]+",
                "description": "数据库连接字符串",
                "severity": "high"
            }
        }
        
        # 需要排除的文件和目录
        self.exclude_patterns = [
            r"\.git/",
            r"__pycache__/",
            r"\.pyc$",
            r"node_modules/",
            r"\.env\.example$",
            r"\.gitignore$",
            r"requirements\.txt$",
            r"package\.json$",
            r"README\.md$",
            r"\.png$", r"\.jpg$", r"\.jpeg$", r"\.gif$",
            r"\.pdf$", r"\.zip$", r"\.tar\.gz$"
        ]
        
        # 敏感文件名模式
        self.sensitive_files = [
            r"\.env$",
            r"config\.json$",
            r"secrets\.json$",
            r"credentials\.json$",
            r"\.key$",
            r"\.pem$",
            r"id_rsa$",
            r"id_dsa$"
        ]
    
    def scan_project(self) -> SecurityReport:
        """扫描整个项目"""
        print(f"🔍 开始扫描项目: {self.project_path}")
        
        # 清空之前的问题
        self.issues = []
        
        # 执行各种安全检查
        self._scan_files_for_secrets()
        self._check_file_permissions()
        self._check_gitignore()
        self._check_git_history()
        self._check_environment_files()
        self._check_configuration_files()
        self._check_dependency_security()
        
        # 生成报告
        report = self._generate_report()
        print(f"✅ 扫描完成，发现 {len(self.issues)} 个安全问题")
        
        return report
    
    def _scan_files_for_secrets(self):
        """扫描文件中的敏感信息"""
        print("  📄 扫描文件中的敏感信息...")
        
        for file_path in self._get_scannable_files():
            self._scan_file(file_path)
    
    def _get_scannable_files(self) -> List[Path]:
        """获取需要扫描的文件列表"""
        files = []
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.project_path))
                
                # 检查是否应该排除此文件
                if any(re.search(pattern, relative_path) for pattern in self.exclude_patterns):
                    continue
                
                # 只扫描文本文件
                if self._is_text_file(file_path):
                    files.append(file_path)
        
        return files
    
    def _is_text_file(self, file_path: Path) -> bool:
        """判断是否为文本文件"""
        try:
            # 检查文件大小（跳过过大的文件）
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return False
            
            # 尝试读取文件开头部分
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:  # 包含空字节的可能是二进制文件
                    return False
            
            return True
        except (OSError, PermissionError):
            return False
    
    def _scan_file(self, file_path: Path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                self._check_line_for_secrets(file_path, line_num, line)
                
        except (OSError, PermissionError, UnicodeDecodeError):
            pass
    
    def _check_line_for_secrets(self, file_path: Path, line_num: int, line: str):
        """检查单行是否包含敏感信息"""
        for secret_type, config in self.secret_patterns.items():
            pattern = config["pattern"]
            matches = re.finditer(pattern, line)
            
            for match in matches:
                # 检查是否为注释或示例
                if self._is_likely_example(line, match.group()):
                    continue
                
                issue = SecurityIssue(
                    severity=config["severity"],
                    category="secret_leak",
                    description=f"发现可能的{config['description']}",
                    file_path=str(file_path.relative_to(self.project_path)),
                    line_number=line_num,
                    context=line.strip(),
                    recommendation=f"移除硬编码的{config['description']}，使用环境变量或安全存储"
                )
                self.issues.append(issue)
    
    def _is_likely_example(self, line: str, secret: str) -> bool:
        """判断是否可能是示例或占位符"""
        line_lower = line.lower()
        
        # 检查注释
        if any(comment in line for comment in ['#', '//', '/*', '*', '<!--']):
            return True
        
        # 检查示例标识
        example_indicators = [
            'example', 'sample', 'demo', 'test', 'placeholder', 'your_api_key',
            'your_key_here', 'replace_with', 'xxx', '***', '...'
        ]
        
        if any(indicator in line_lower for indicator in example_indicators):
            return True
        
        # 检查是否包含明显的占位符字符
        if re.search(r'x{8,}|\.{3,}|\*{3,}', secret):
            return True
        
        return False
    
    def _check_file_permissions(self):
        """检查文件权限"""
        print("  🔒 检查文件权限...")
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.project_path))
                
                # 检查敏感文件
                if any(re.search(pattern, relative_path) for pattern in self.sensitive_files):
                    self._check_sensitive_file_permissions(file_path)
    
    def _check_sensitive_file_permissions(self, file_path: Path):
        """检查敏感文件权限"""
        try:
            file_stat = file_path.stat()
            file_mode = stat.filemode(file_stat.st_mode)
            
            # 检查是否对其他用户可读
            if file_stat.st_mode & (stat.S_IRGRP | stat.S_IROTH):
                issue = SecurityIssue(
                    severity="medium",
                    category="file_permission",
                    description="敏感文件对其他用户可读",
                    file_path=str(file_path.relative_to(self.project_path)),
                    context=f"权限: {file_mode}",
                    recommendation="设置文件权限为600 (仅所有者可读写)"
                )
                self.issues.append(issue)
                
        except OSError:
            pass
    
    def _check_gitignore(self):
        """检查.gitignore配置"""
        print("  📝 检查.gitignore配置...")
        
        gitignore_path = self.project_path / ".gitignore"
        
        if not gitignore_path.exists():
            issue = SecurityIssue(
                severity="medium",
                category="missing_gitignore",
                description="缺少.gitignore文件",
                recommendation="创建.gitignore文件以防止敏感文件被提交"
            )
            self.issues.append(issue)
            return
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            # 检查重要的忽略项
            important_ignores = [
                "config.json",
                ".env",
                "*.key",
                "*.pem",
                "secrets.json",
                "credentials.json"
            ]
            
            for ignore_item in important_ignores:
                if ignore_item not in gitignore_content:
                    issue = SecurityIssue(
                        severity="medium",
                        category="incomplete_gitignore",
                        description=f".gitignore缺少重要项目: {ignore_item}",
                        file_path=".gitignore",
                        recommendation=f"在.gitignore中添加 {ignore_item}"
                    )
                    self.issues.append(issue)
                    
        except (OSError, UnicodeDecodeError):
            pass
    
    def _check_git_history(self):
        """检查Git历史中的敏感信息"""
        print("  📚 检查Git历史...")
        
        if not (self.project_path / ".git").exists():
            return
        
        try:
            # 获取最近的提交历史
            result = subprocess.run(
                ["git", "log", "--oneline", "-20"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if any(keyword in line.lower() for keyword in 
                          ['password', 'secret', 'key', 'token', 'credential']):
                        issue = SecurityIssue(
                            severity="high",
                            category="git_history",
                            description="Git提交消息中可能包含敏感信息",
                            context=line.strip(),
                            recommendation="检查相关提交，如有必要请重写Git历史"
                        )
                        self.issues.append(issue)
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    def _check_environment_files(self):
        """检查环境变量文件"""
        print("  🌍 检查环境变量文件...")
        
        env_files = [".env", ".env.local", ".env.production", ".env.development"]
        
        for env_file in env_files:
            env_path = self.project_path / env_file
            if env_path.exists():
                # 检查.env文件是否在.gitignore中
                gitignore_path = self.project_path / ".gitignore"
                if gitignore_path.exists():
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        gitignore_content = f.read()
                    
                    if env_file not in gitignore_content:
                        issue = SecurityIssue(
                            severity="critical",
                            category="env_not_ignored",
                            description=f"环境文件{env_file}未在.gitignore中忽略",
                            file_path=env_file,
                            recommendation=f"将{env_file}添加到.gitignore中"
                        )
                        self.issues.append(issue)
    
    def _check_configuration_files(self):
        """检查配置文件"""
        print("  ⚙️ 检查配置文件...")
        
        config_files = ["config.json", "settings.json", "secrets.json"]
        
        for config_file in config_files:
            config_path = self.project_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查是否包含API密钥
                    if any(keyword in content.lower() for keyword in 
                          ['api_key', 'secret', 'password', 'token']):
                        issue = SecurityIssue(
                            severity="high",
                            category="config_secrets",
                            description=f"配置文件{config_file}可能包含敏感信息",
                            file_path=config_file,
                            recommendation="移除敏感信息，使用环境变量或安全存储"
                        )
                        self.issues.append(issue)
                        
                except (OSError, UnicodeDecodeError):
                    pass
    
    def _check_dependency_security(self):
        """检查依赖安全性"""
        print("  📦 检查依赖安全性...")
        
        # 检查requirements.txt
        req_path = self.project_path / "requirements.txt"
        if req_path.exists():
            try:
                with open(req_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否固定版本
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                unfixed_deps = []
                
                for line in lines:
                    if line and not line.startswith('#'):
                        if '>=' in line or '>' in line or '~=' in line:
                            unfixed_deps.append(line)
                
                if unfixed_deps:
                    issue = SecurityIssue(
                        severity="medium",
                        category="dependency_security",
                        description="存在未固定版本的依赖",
                        file_path="requirements.txt",
                        context=f"未固定版本的依赖: {', '.join(unfixed_deps[:3])}...",
                        recommendation="固定依赖版本以避免潜在的安全风险"
                    )
                    self.issues.append(issue)
                    
            except (OSError, UnicodeDecodeError):
                pass
    
    def _generate_report(self) -> SecurityReport:
        """生成安全报告"""
        # 按严重程度统计
        summary = {
            "critical": len([i for i in self.issues if i.severity == "critical"]),
            "high": len([i for i in self.issues if i.severity == "high"]),
            "medium": len([i for i in self.issues if i.severity == "medium"]),
            "low": len([i for i in self.issues if i.severity == "low"])
        }
        
        # 生成建议
        recommendations = self._generate_recommendations()
        
        report = SecurityReport(
            scan_time=datetime.now().isoformat(),
            project_path=str(self.project_path),
            issues=self.issues,
            summary=summary,
            recommendations=recommendations
        )
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        # 基于发现的问题生成建议
        if any(i.category == "secret_leak" for i in self.issues):
            recommendations.append("🔐 使用环境变量或安全存储管理API密钥，避免硬编码")
        
        if any(i.category == "env_not_ignored" for i in self.issues):
            recommendations.append("📝 确保所有环境文件都在.gitignore中")
        
        if any(i.category == "file_permission" for i in self.issues):
            recommendations.append("🔒 设置敏感文件的正确权限(600)")
        
        if any(i.category == "git_history" for i in self.issues):
            recommendations.append("📚 检查Git历史，如有必要清理敏感信息")
        
        # 通用建议
        recommendations.extend([
            "🛡️ 定期更新依赖以修复安全漏洞",
            "🔍 建立持续的安全扫描流程",
            "📖 为团队制定安全编码规范",
            "🚨 配置Git预提交钩子防止敏感信息泄露"
        ])
        
        return recommendations
    
    def print_report(self, report: SecurityReport):
        """打印安全报告"""
        print("\n" + "="*60)
        print("🛡️  安全扫描报告")
        print("="*60)
        
        print(f"📅 扫描时间: {report.scan_time}")
        print(f"📁 项目路径: {report.project_path}")
        print(f"📊 问题总数: {len(report.issues)}")
        
        # 统计信息
        print("\n📈 问题统计:")
        severity_colors = {
            "critical": "🔴",
            "high": "🟠", 
            "medium": "🟡",
            "low": "🟢"
        }
        
        for severity, count in report.summary.items():
            if count > 0:
                print(f"  {severity_colors[severity]} {severity.upper()}: {count}")
        
        # 详细问题
        if report.issues:
            print("\n🔍 发现的问题:")
            for i, issue in enumerate(report.issues, 1):
                severity_icon = severity_colors.get(issue.severity, "⚪")
                print(f"\n{i}. {severity_icon} {issue.description}")
                if issue.file_path:
                    print(f"   📁 文件: {issue.file_path}")
                if issue.line_number:
                    print(f"   📍 行号: {issue.line_number}")
                if issue.context:
                    print(f"   📝 内容: {issue.context}")
                if issue.recommendation:
                    print(f"   💡 建议: {issue.recommendation}")
        
        # 安全建议
        if report.recommendations:
            print("\n💡 安全建议:")
            for rec in report.recommendations:
                print(f"  - {rec}")
        
        print("\n" + "="*60)
    
    def export_report(self, report: SecurityReport, output_path: str):
        """导出报告为JSON文件"""
        report_dict = {
            "scan_time": report.scan_time,
            "project_path": report.project_path,
            "summary": report.summary,
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "description": issue.description,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "context": issue.context,
                    "recommendation": issue.recommendation
                }
                for issue in report.issues
            ],
            "recommendations": report.recommendations
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        print(f"📄 报告已导出到: {output_path}")

def create_gitignore_template() -> str:
    """创建.gitignore模板"""
    return """# API密钥和敏感信息
.env
.env.*
config.json
secrets.json
credentials.json
*.key
*.pem
id_rsa
id_dsa

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# 日志文件
*.log
logs/

# 数据库
*.db
*.sqlite3

# 备份文件
*.bak
*.backup
"""

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="项目安全扫描器")
    parser.add_argument("--path", "-p", default=".", help="要扫描的项目路径")
    parser.add_argument("--output", "-o", help="输出报告文件路径")
    parser.add_argument("--create-gitignore", action="store_true", help="创建.gitignore模板")
    parser.add_argument("--fix", action="store_true", help="自动修复一些安全问题")
    
    args = parser.parse_args()
    
    if args.create_gitignore:
        gitignore_path = Path(args.path) / ".gitignore"
        if gitignore_path.exists():
            print("⚠️ .gitignore文件已存在")
            response = input("是否覆盖? (y/N): ")
            if response.lower() != 'y':
                return
        
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(create_gitignore_template())
        print(f"✅ 已创建.gitignore模板: {gitignore_path}")
        return
    
    # 执行安全扫描
    scanner = SecurityScanner(args.path)
    report = scanner.scan_project()
    
    # 打印报告
    scanner.print_report(report)
    
    # 导出报告
    if args.output:
        scanner.export_report(report, args.output)
    
    # 自动修复
    if args.fix:
        fix_security_issues(report, args.path)
    
    # 返回适当的退出码
    if report.summary.get("critical", 0) > 0:
        return 2
    elif report.summary.get("high", 0) > 0:
        return 1
    else:
        return 0

def fix_security_issues(report: SecurityReport, project_path: str):
    """自动修复一些安全问题"""
    print("\n🔧 尝试自动修复安全问题...")
    
    project_path = Path(project_path)
    fixed_count = 0
    
    for issue in report.issues:
        if issue.category == "incomplete_gitignore":
            gitignore_path = project_path / ".gitignore"
            if gitignore_path.exists():
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n# Added by security scanner\n")
                    if "config.json" in issue.description:
                        f.write("config.json\n")
                    elif ".env" in issue.description:
                        f.write(".env\n")
                    elif "*.key" in issue.description:
                        f.write("*.key\n")
                print(f"✅ 已修复: {issue.description}")
                fixed_count += 1
        
        elif issue.category == "file_permission" and issue.file_path:
            file_path = project_path / issue.file_path
            if file_path.exists():
                try:
                    os.chmod(file_path, 0o600)
                    print(f"✅ 已修复文件权限: {issue.file_path}")
                    fixed_count += 1
                except OSError as e:
                    print(f"❌ 修复权限失败 {issue.file_path}: {e}")
    
    print(f"✅ 自动修复了 {fixed_count} 个问题")

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code) 