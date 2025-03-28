# 安全指南

本文档提供了AI提示工程师项目的安全最佳实践，重点关注API密钥管理和数据安全。

## 目录

- [API密钥安全](#api密钥安全)
  - [密钥泄露的风险](#密钥泄露的风险)
  - [安全使用API密钥的最佳实践](#安全使用api密钥的最佳实践)
  - [密钥泄露时的应对措施](#密钥泄露时的应对措施)
- [数据安全](#数据安全)
  - [提示和生成内容的隐私](#提示和生成内容的隐私)
  - [敏感信息处理](#敏感信息处理)
- [代码安全](#代码安全)
  - [依赖管理](#依赖管理)
  - [安全更新](#安全更新)
- [报告安全问题](#报告安全问题)

## API密钥安全

### 密钥泄露的风险

API密钥泄露可能导致：

1. **未授权使用**：他人可使用您的密钥访问API，产生大量费用
2. **账户滥用**：可能导致违反服务条款或API速率限制
3. **数据泄露**：如果API有权访问敏感数据，可能导致更严重的安全事件
4. **信誉损害**：影响您或您组织的声誉和信任度

### 安全使用API密钥的最佳实践

#### 1. 环境变量

最安全的API密钥存储方式是使用环境变量：

```bash
# Linux/macOS
export DEEPSEEK_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_api_key_here"

# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_api_key_here"
$env:OPENAI_API_KEY="your_api_key_here"
```

#### 2. 使用.env文件（开发环境）

适用于开发环境：

```
DEEPSEEK_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
```

确保：
- `.env`文件已添加到`.gitignore`
- 从不将此文件提交到版本控制
- 限制此文件的访问权限

#### 3. 使用密钥管理服务

在生产环境中：
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

#### 4. 使用专用工具（推荐）

本项目提供`api_secrets.py`工具：

```bash
python api_secrets.py --set --provider deepseek
```

此工具提供多种安全存储选项。

#### 5. 密钥轮换与权限限制

- 定期更换API密钥
- 使用最小权限原则
- 为不同环境使用不同密钥
- 启用API密钥使用监控

### 密钥泄露时的应对措施

如果您怀疑API密钥已泄露：

1. **立即撤销/重置密钥**：
   - OpenAI: 访问[API密钥页面](https://platform.openai.com/api-keys)撤销
   - DeepSeek: 访问[平台设置](https://platform.deepseek.com)撤销

2. **检查使用记录**：
   - 审查API使用历史
   - 寻找异常活动

3. **限制损失**：
   - 设置API使用限额
   - 暂时停用相关服务

4. **防止再次发生**：
   - 审查密钥存储方式
   - 加强安全措施
   - 实施自动密钥轮换

## 数据安全

### 提示和生成内容的隐私

AI提示工程师项目本地处理大部分数据，但提示和生成的内容会发送到API提供商。请注意：

1. **不要在提示中包含敏感信息**：
   - 个人身份信息(PII)
   - 财务或医疗数据
   - 机密商业信息
   - 安全凭据

2. **了解API提供商的数据政策**：
   - OpenAI: [数据使用政策](https://openai.com/policies/api-data-usage-policies)
   - DeepSeek: [隐私政策](https://platform.deepseek.com/privacy)

3. **考虑数据驻留需求**：
   - 某些监管环境可能限制数据传输
   - 验证API提供商的服务器位置

### 敏感信息处理

如果您需要处理包含敏感信息的提示：

1. **数据屏蔽**：在发送前移除或屏蔽敏感数据
2. **本地模型**：考虑使用本地部署的模型（计划中的功能）
3. **内容过滤**：实施数据过滤机制

## 代码安全

### 依赖管理

定期更新项目依赖以修复安全漏洞：

```bash
pip install -r requirements.txt --upgrade
```

使用依赖扫描工具检查漏洞：

```bash
pip install safety
safety check -r requirements.txt
```

### 安全更新

确保及时应用安全更新：

1. 关注项目的GitHub安全公告
2. 订阅API提供商的安全通知
3. 定期检查依赖更新

## 报告安全问题

如发现安全漏洞，请**不要**创建公开的GitHub Issue。请：

1. 发送电子邮件至[security@example.com](mailto:security@example.com)
2. 提供漏洞详细信息
3. 如可能，提供重现步骤
4. 我们将在48小时内回复

负责任的披露将获得适当的认可。

---

*最后更新: 2023年12月* 