# AI提示工程师 - 安全功能指南

本文档介绍AI提示工程师项目中的安全功能，帮助您保护API密钥和敏感信息。

## 概述

我们的安全功能套件包括：
- **安全API管理器** - 加密存储API密钥
- **安全扫描器** - 检测API密钥泄露和安全风险
- **Git预提交钩子** - 防止敏感信息提交
- **自动化测试** - 验证安全功能正常工作

## 1. 安全API管理器

### 功能特性
- ✅ **主密码保护** - 使用PBKDF2加密算法
- ✅ **多种存储方式** - 安全存储/环境变量/配置文件
- ✅ **格式验证** - 支持OpenAI、DeepSeek、Anthropic、Google等
- ✅ **安全审计** - 检查存储方式的安全性

### 使用方法

#### 设置API密钥
```bash
# 交互式设置（推荐）
python secure_api_manager.py --set

# 指定提供商
python secure_api_manager.py --set --provider openai
```

#### 管理API密钥
```bash
# 列出已配置的提供商
python secure_api_manager.py --list

# 验证所有API密钥格式
python secure_api_manager.py --validate

# 删除指定提供商的密钥
python secure_api_manager.py --remove openai
```

#### 安全检查
```bash
# 执行完整安全检查
python secure_api_manager.py --security-check
```

## 2. 安全扫描器

### 检测能力
- 🔍 **API密钥泄露** - 检测9种常见API密钥格式
- 🔍 **硬编码密码** - 数据库密码、JWT令牌等
- 🔍 **文件权限** - 敏感文件的访问权限检查
- 🔍 **.gitignore配置** - 确保敏感文件被正确忽略
- 🔍 **Git历史** - 检查提交历史中的敏感信息
- 🔍 **依赖安全** - 检查未固定版本的依赖

### 使用方法

#### 基本扫描
```bash
# 扫描当前项目
python security_scanner.py

# 扫描指定路径
python security_scanner.py --path /path/to/project
```

#### 导出和修复
```bash
# 导出详细报告
python security_scanner.py --output security_report.json

# 自动修复常见问题
python security_scanner.py --fix
```

#### 创建安全模板
```bash
# 创建标准的.gitignore模板
python security_scanner.py --create-gitignore
```

### 扫描报告解读

扫描报告按严重程度分类：
- 🔴 **CRITICAL** - 立即需要处理的严重安全风险
- 🟠 **HIGH** - 高优先级安全问题
- 🟡 **MEDIUM** - 中等优先级问题
- 🟢 **LOW** - 低优先级建议

## 3. Git预提交钩子

### 功能特性
- ⚡ **实时检测** - 在提交前自动检查暂存文件
- 🧠 **智能识别** - 区分真实密钥和示例代码
- 📋 **清晰反馈** - 提供详细的问题报告和修复建议
- ⚙️ **可配置** - 支持自定义检查规则

### 安装和使用

#### 安装钩子
```bash
# 自动安装和配置
python install_git_hooks.py --install

# 仅安装钩子
python install_git_hooks.py --install
```

#### 管理钩子
```bash
# 测试钩子功能
python install_git_hooks.py --test

# 卸载钩子
python install_git_hooks.py --uninstall

# 创建配置文件
python install_git_hooks.py --config
```

#### 钩子配置

编辑 `.git_hooks_config` 文件：
```ini
# 是否启用安全检查
ENABLE_SECURITY_CHECK=true

# 检查级别 (strict, normal, loose)
CHECK_LEVEL=normal

# 是否允许跳过检查
ALLOW_SKIP=true

# 检查的文件类型
CHECKED_EXTENSIONS=.py,.js,.ts,.java,.json
```

#### 跳过检查
```bash
# 临时跳过安全检查（不推荐）
git commit --no-verify
```

## 4. 安全最佳实践

### API密钥管理
1. **使用安全存储** - 优先使用我们的安全API管理器
2. **环境变量** - 适合CI/CD和生产环境
3. **避免配置文件** - 除非确保不会被提交

### 项目安全
1. **定期扫描** - 建立持续的安全扫描流程
2. **团队培训** - 制定安全编码规范
3. **版本控制** - 使用Git钩子防止意外提交

### 文件权限
```bash
# 设置敏感文件的正确权限
chmod 600 .env
chmod 600 config.json
chmod 600 *.key
chmod 600 *.pem
```

### .gitignore配置
确保包含以下重要项目：
```gitignore
# API密钥和敏感信息
.env
.env.*
config.json
secrets.json
credentials.json
*.key
*.pem
id_rsa
id_dsa

# 安全存储目录
~/.ai_prompt_engineer/
```

## 5. 故障排除

### 常见问题

#### Q: 钩子阻止了正常提交怎么办？
A: 
1. 检查报告中的具体问题
2. 确认是否为测试用的虚假密钥，添加"test"或"example"标识
3. 将真实密钥移至环境变量或安全存储

#### Q: 如何处理误报？
A:
1. 在代码中添加明确的示例标识（如"example", "test", "demo"）
2. 使用注释标明示例代码
3. 配置自定义排除模式

#### Q: 安全扫描器运行缓慢？
A:
1. 排除大型二进制文件目录
2. 使用 `--path` 参数扫描特定目录
3. 检查文件大小限制（默认10MB）

#### Q: 忘记主密码怎么办？
A:
1. 删除 `~/.ai_prompt_engineer/.secure_config.enc` 和 `.key_hash`
2. 重新设置API密钥和主密码
3. 建议使用密码管理器保存主密码

### 性能优化

对于大型项目：
```bash
# 只扫描源代码目录
python security_scanner.py --path ./src

# 排除特定目录
# 在security_scanner.py中配置exclude_patterns
```

## 6. 测试和验证

### 运行安全测试
```bash
# 测试所有安全功能
python test_security_scanner.py

# 测试完整功能套件
python test_new_features.py
```

### 验证安装
```bash
# 检查安全API管理器
python -c "from secure_api_manager import SecureAPIManager; print('✅ 安全API管理器正常')"

# 检查安全扫描器
python -c "from security_scanner import SecurityScanner; print('✅ 安全扫描器正常')"

# 检查Git钩子
ls -la .git/hooks/pre-commit && echo "✅ Git钩子已安装"
```

## 7. 集成到CI/CD

### GitHub Actions示例
```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run security scan
      run: |
        python security_scanner.py
        if [ $? -eq 2 ]; then
          echo "严重安全问题发现，构建失败"
          exit 1
        fi
```

### 退出码说明
- `0` - 无安全问题或仅有低/中等问题
- `1` - 发现高优先级安全问题  
- `2` - 发现严重安全问题

## 8. 高级配置

### 自定义密钥模式
在 `security_scanner.py` 中添加新的检测模式：
```python
self.secret_patterns["custom_key"] = {
    "pattern": r"your_custom_pattern",
    "description": "自定义密钥",
    "severity": "critical"
}
```

### 自定义排除规则
```python
self.exclude_patterns.extend([
    r"your_custom_exclude_pattern",
    r"test_data/",
    r"examples/"
])
```

## 9. 支持和贡献

如果您发现安全问题或有改进建议：
1. 创建Issue描述问题
2. 提供重现步骤
3. 建议解决方案

对于安全漏洞，请私下联系维护者。

## 10. 更新日志

### v2.0 安全功能
- ✅ 添加安全API管理器
- ✅ 添加安全扫描器
- ✅ 添加Git预提交钩子
- ✅ 添加自动化测试套件
- ✅ 添加自动修复功能

---

**安全提醒**: 请定期更新安全工具和模式，以检测新型威胁。永远不要在公共仓库中存储真实的API密钥或敏感信息。 