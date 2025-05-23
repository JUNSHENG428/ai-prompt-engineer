# AI提示工程师安装与设置指南

本文档提供了详细的安装步骤和API密钥设置指南，帮助您正确设置AI提示工程师项目。

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/ai-prompt-engineer.git
cd ai-prompt-engineer
```

### 2. 设置虚拟环境（推荐）

#### Linux/macOS
```bash
python -m venv venv
source venv/bin/activate
```

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## API密钥设置

AI提示工程师支持多种方式设置API密钥。按照以下优先级自动查找密钥：

1. 环境变量
2. .env文件
3. Streamlit secrets
4. config.json

### 方法一：使用专用工具设置API密钥（推荐）

项目提供了专门的API密钥管理工具：

```bash
# 设置Deepseek API密钥
python api_secrets.py --set --provider deepseek

# 设置OpenAI API密钥
python api_secrets.py --set --provider openai

# 设置Claude API密钥
python api_secrets.py --set --provider claude

# 检查当前设置的密钥 
python api_secrets.py --get --provider deepseek
# (也可以使用 --provider openai 或 --provider claude)
```

此工具会提示您输入API密钥，并提供多种安全存储选项。

### 方法二：手动设置环境变量

#### Linux/macOS

临时设置(仅当前会话有效)：
```bash
export DEEPSEEK_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_api_key_here"
export CLAUDE_API_KEY="your_claude_api_key_here"
```

永久设置：
```bash
echo 'export DEEPSEEK_API_KEY="your_api_key_here"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
echo 'export CLAUDE_API_KEY="your_claude_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows CMD

临时设置：
```cmd
set DEEPSEEK_API_KEY=your_api_key_here
set OPENAI_API_KEY=your_api_key_here
set CLAUDE_API_KEY=your_claude_api_key_here
```

永久设置：
```cmd
setx DEEPSEEK_API_KEY "your_api_key_here"
setx OPENAI_API_KEY "your_api_key_here"
setx CLAUDE_API_KEY "your_claude_api_key_here"
```

#### Windows PowerShell

临时设置：
```powershell
$env:DEEPSEEK_API_KEY="your_api_key_here"
$env:OPENAI_API_KEY="your_api_key_here"
$env:CLAUDE_API_KEY="your_claude_api_key_here"
```

永久设置：
```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "your_api_key_here", "User")
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_api_key_here", "User")
[Environment]::SetEnvironmentVariable("CLAUDE_API_KEY", "your_claude_api_key_here", "User")
```

### 方法三：使用.env文件

1. 复制示例环境变量文件：
```bash
cp .env.example .env
```

2. 编辑.env文件，填入您的API密钥：
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
```

### 方法四：Streamlit Secrets（仅Streamlit应用）

1. 创建Streamlit secrets目录和文件：
```bash
mkdir -p .streamlit
```

2. 创建secrets.toml文件：
```bash
echo 'DEEPSEEK_API_KEY = "your_deepseek_api_key_here"' > .streamlit/secrets.toml
echo 'OPENAI_API_KEY = "your_openai_api_key_here"' >> .streamlit/secrets.toml
echo 'CLAUDE_API_KEY = "your_claude_api_key_here"' >> .streamlit/secrets.toml
```

### 方法五：使用配置文件（不推荐用于生产环境）

1. 复制配置模板：
```bash
cp config.template.json config.json
```

2. 编辑config.json文件，添加API密钥：
```json
{
  "api_key": "your_api_key_here",
  "api_provider": "deepseek",
  "model": "deepseek-chat",
  "default_format": "standard",
  "language": "zh"
}
```

## 获取API密钥

### 获取DeepSeek API密钥

1. 访问 [DeepSeek Platform](https://platform.deepseek.com)
2. 注册或登录您的账户
3. 导航到API密钥部分
4. 创建新的API密钥

### 获取OpenAI API密钥

1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 注册或登录您的OpenAI账户
3. 创建新的API密钥

### 获取Anthropic Claude API密钥

1. 访问 [Anthropic Console](https://console.anthropic.com/settings/keys)
2. 注册或登录您的Anthropic账户
3. 导航到API密钥部分 (通常在账户设置或API设置中)
4. 创建新的API密钥

## 启动应用

### 使用Streamlit界面（推荐）

```bash
streamlit run streamlit_app.py
```

### 使用命令行工具

生成标准格式的提示 (默认使用config.json中或环境变量中设置的提供商):
```bash
python prompt_engineer.py "您的需求描述" --format standard
```

指定API提供商和模型 (示例使用Claude):
```bash
python prompt_engineer.py "用Claude模型分析最近的AI趋势" --api-provider claude --model claude-3-opus-20240229
```

## 常见问题解决

### API密钥不被识别

1. 检查密钥是否正确设置：
```bash
python api_secrets.py --get
```

2. 确认环境变量已正确设置：
```bash
# Linux/macOS
echo $DEEPSEEK_API_KEY

# Windows CMD
echo %DEEPSEEK_API_KEY%

# Windows PowerShell
echo $env:DEEPSEEK_API_KEY
```

3. 尝试直接在命令行指定API密钥：
```bash
python prompt_engineer.py "测试需求" --api-key "your_api_key_here"
```

### 依赖问题

如果遇到依赖相关错误，尝试：

```bash
pip install -r requirements.txt --upgrade
```

### 安全注意事项

- 永远不要将API密钥提交到版本控制系统
- 使用环境变量是最安全的做法
- 定期轮换您的API密钥
- 考虑为不同的应用程序使用不同的API密钥

## 下一步

成功安装和配置后，请参考[README.md](README.md)了解如何使用AI提示工程师的所有功能。 