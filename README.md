# AI 提示工程师 2.0

这个项目提供了用于生成格式良好、详细的提示词的工具，基于自动提示工程（Automatic Prompt Engineering）的概念，并提供了美观易用的用户界面。

![界面预览](images/screenshot.png)

## 功能特点

- **直观美观的 UI**：现代化设计，多种主题选择
- **六种提示格式**：标准格式、专家讨论、带示例模式、编程任务、Cursor 优化、系统架构
- **🧑‍💻 编程模板库**：专门针对编程任务的预设模板，涵盖代码生成、调试、重构、测试等场景
- **🤖 智能建议器**：分析用户需求，自动推荐最适合的模板和改进建议
- **智能质量评估**：从清晰度、具体性、完整性、结构性和可操作性五个维度评估提示质量
- **编程专用优化**：专为 Cursor、GitHub Copilot 等 AI 编程工具定制的提示格式
- **企业级安全**：API 密钥加密存储、安全扫描、Git 钩子防泄露
- **历史记录**：保存和管理您生成的所有提示词
- **自定义设置**：灵活配置 API 参数和生成选项
- **多模型支持**：兼容 DeepSeek 和 OpenAI 的多种模型
- **跨平台**：基于 Web 技术，可在任何设备上运行

## 组件

项目包含三个主要实现：

1. **auto_prompt_engineer.py**: 完整的 APE 实现，包括：

   - 执行任务的推断模型
   - 评估提示的评分模型
   - 可选的生成提示变体的重采样模型
   - 查找最佳提示的迭代优化过程

2. **prompt_engineer.py**: 简化的实用实现，它：

   - 连接到语言模型 API 生成提示
   - 提供三种格式：标准、专家讨论和基于示例
   - 可以使用或不使用 API 密钥（回退到模拟响应）

3. **streamlit_app.py**: 用户友好的图形界面，提供：
   - 简单直观的提示生成界面
   - 多种主题和自定义选项
   - 历史记录管理和提示复用功能
   - 详细的使用指南和提示技巧

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/auto-prompting_engineer.git
cd auto-prompting_engineer

# 安装所需包
pip install -r requirements.txt
```

## API 密钥设置指南

本项目提供了多种设置 API 密钥的方式，以确保您的密钥安全：

### 方法 1：使用环境变量（最安全）

Linux/macOS:

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_api_key_here"
```

Windows (CMD):

```cmd
set DEEPSEEK_API_KEY=your_api_key_here
set OPENAI_API_KEY=your_api_key_here
```

Windows (PowerShell):

```powershell
$env:DEEPSEEK_API_KEY="your_api_key_here"
$env:OPENAI_API_KEY="your_api_key_here"
```

### 方法 2：使用.env 文件

1. 复制示例文件并重命名

```bash
cp .env.example .env
```

2. 编辑.env 文件，添加您的 API 密钥

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 方法 3：使用 Streamlit secrets

如果您使用 Streamlit，可以创建一个 secrets.toml 文件：

```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
```

然后在 secrets.toml 中添加您的 API 密钥：

```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
```

### 方法 4：使用 API 密钥管理工具

本项目提供了一个专门的 API 密钥管理工具：

```bash
python api_secrets.py --set --provider deepseek
```

此工具会安全地提示您输入密钥，并指导您选择最安全的存储方式。

### 方法 5：在图形界面中设置

启动应用后，您也可以在侧边栏中设置 API 密钥。务必注意，这种方式下密钥可能会存储在 config.json 文件中，不适合共享环境。

## 安全功能

本项目提供了企业级的安全功能，帮助您保护 API 密钥和敏感信息：

### 1. 安全 API 管理器

使用加密存储和主密码保护您的 API 密钥：

```bash
# 安全设置API密钥
python secure_api_manager.py --set --provider openai

# 列出已配置的提供商
python secure_api_manager.py --list

# 验证所有API密钥
python secure_api_manager.py --validate

# 执行安全检查
python secure_api_manager.py --security-check
```

特性：

- **主密码保护**：使用 PBKDF2 加密存储 API 密钥
- **多种存储方式**：安全存储、环境变量、配置文件
- **格式验证**：自动验证不同提供商的 API 密钥格式
- **安全审计**：检查存储方式的安全性

### 2. 安全扫描器

检测项目中的 API 密钥泄露和安全风险：

```bash
# 扫描当前项目
python security_scanner.py

# 扫描指定路径
python security_scanner.py --path /path/to/project

# 导出扫描报告
python security_scanner.py --output security_report.json

# 自动修复一些安全问题
python security_scanner.py --fix

# 创建.gitignore模板
python security_scanner.py --create-gitignore
```

检测内容：

- **API 密钥泄露**：OpenAI、DeepSeek、Anthropic、Google 等
- **硬编码密码**：数据库密码、JWT 令牌等
- **文件权限**：敏感文件的访问权限
- **.gitignore 配置**：检查是否正确忽略敏感文件
- **Git 历史**：检查提交历史中的敏感信息
- **依赖安全**：检查未固定版本的依赖

### 3. Git 预提交钩子

防止敏感信息被意外提交到版本控制：

```bash
# 安装Git钩子
python install_git_hooks.py --install

# 测试钩子功能
python install_git_hooks.py --test

# 卸载钩子
python install_git_hooks.py --uninstall
```

钩子功能：

- **实时检测**：在提交前自动检查暂存文件
- **智能识别**：区分真实密钥和示例代码
- **清晰反馈**：提供详细的问题报告和修复建议
- **可配置**：支持自定义检查规则

### 4. 测试安全功能

验证所有安全功能是否正常工作：

```bash
# 测试安全扫描器
python test_security_scanner.py

# 测试完整功能（包括安全功能）
python test_new_features.py
```

## 安全注意事项

为了保护您的 API 密钥：

1. **永远不要**将包含真实 API 密钥的文件上传到 GitHub 或其他公共仓库
2. .gitignore 已配置为排除以下文件：
   - config.json (实际配置)
   - .env (环境变量)
   - .streamlit/secrets.toml (Streamlit 密钥)
3. 如果您需要分享代码，请使用模板文件代替：
   - config.template.json
   - .env.example

## 使用方法

### 图形界面使用

启动图形界面:

```bash
streamlit run streamlit_app.py
```

使用图形界面:

1. 在左侧输入框中输入你的需求
2. 选择提示格式（标准、专家讨论或带示例）
3. 配置 API 设置（API 密钥、提供商、模型）
4. 点击"生成提示"按钮
5. 生成的提示将显示在右侧，可以复制或下载

### 命令行使用

#### 基本提示生成

生成标准格式的提示：

```bash
python prompt_engineer.py "创建一个城市园艺指南"
```

#### 专家讨论提示

生成模拟专家讨论主题的提示：

```bash
python prompt_engineer.py "设计一个可持续发展的智能城市" --format expert-panel
```

#### 包含示例的提示

生成包含示例以便更好理解的提示：

```bash
python prompt_engineer.py "为产品创建客户推荐" --format examples --examples examples.json
```

## 使用 Deepseek API

使用 Deepseek API 生成提示：

```bash
python prompt_engineer.py "分析市场趋势" --api-provider deepseek --model deepseek-chat
```

## 新功能使用示例

### 🧑‍💻 编程模板库

使用专门的编程模板生成针对性的提示：

#### 命令行使用

```bash
# 函数生成模板
python programming_prompt_templates.py

# 生成特定模板的提示
python -c "
from programming_prompt_templates import get_programming_templates
templates = get_programming_templates()
prompt = templates.generate_prompt('function_generation',
    language='Python',
    function_description='计算两个数的最大公约数',
    input_parameters='a (int), b (int)',
    return_value='int - 最大公约数',
    constraints='输入必须为正整数'
)
print(prompt)
"
```

#### 图形界面使用

1. 启动应用后，点击"🧑‍💻 编程模板"标签页
2. 选择任务类型（代码生成、调试、重构等）
3. 选择 AI 工具（Cursor、GitHub Copilot 等）
4. 选择匹配的模板
5. 填写模板变量
6. 点击"生成 Prompt"

#### 支持的模板类型

- **函数生成**：创建特定功能的函数
- **代码审查**：全面的代码质量检查
- **Bug 修复**：定位和修复代码问题
- **API 设计**：RESTful API 或 GraphQL 设计
- **测试编写**：单元测试、集成测试
- **Cursor 优化**：专为 Cursor AI 编辑器优化
- **GitHub Copilot 优化**：配合 Copilot 的代码优化

### 🤖 智能建议器

自动分析需求并推荐最适合的模板：

#### 命令行使用

```python
from prompt_advisor import PromptAdvisor

advisor = PromptAdvisor()
result = advisor.analyze_and_recommend("我想用Python创建一个函数来处理CSV文件数据")

print(f"任务类型: {result['analysis']['task_type']}")
print(f"推荐模板: {result['recommendations'][0]['template_name']}")
```

#### 图形界面使用

1. 点击"🤖 智能建议"标签页
2. 在文本框中详细描述您的编程需求
3. 点击"分析需求"
4. 查看智能分析结果：
   - 任务类型识别
   - 编程语言检测
   - 复杂度评估
   - 模板推荐
   - 改进建议

#### 智能分析功能

- **任务类型检测**：自动识别 12 种编程任务类型
- **语言识别**：支持主流编程语言检测
- **AI 工具适配**：针对不同 AI 工具的优化建议
- **复杂度评估**：simple/medium/complex 三级评估
- **缺失信息提醒**：指出需要补充的关键信息
- **个性化推荐**：基于相关性评分的模板推荐

### 编程任务提示生成

生成专门的编程任务提示：

```bash
python prompt_engineer.py "创建一个Python函数计算斐波那契数列" --format coding --programming-language Python --coding-task-type general
```

### Cursor AI 优化提示

为 Cursor 编辑器生成优化的提示：

```bash
python prompt_engineer.py "实现用户登录功能" --format cursor --project-context "React + Node.js项目" --file-types React JavaScript
```

### 系统架构设计提示

生成系统架构设计提示：

```bash
python prompt_engineer.py "设计微服务电商系统" --format architecture --system-type microservice --technologies React Node.js PostgreSQL Docker
```

### 提示质量评估

评估提示词质量：

```python
from prompt_quality_evaluator import PromptQualityEvaluator

evaluator = PromptQualityEvaluator()
report = evaluator.evaluate_prompt(your_prompt, original_requirement)
print(evaluator.generate_detailed_report(report))
```

## 将项目上传到 GitHub 时的安全建议

如果您想将此项目上传到您自己的 GitHub 仓库，请遵循以下步骤以确保 API 密钥安全：

1. **检查敏感文件**：确保您不会上传包含真实 API 密钥的文件

   ```bash
   # 检查所有可能包含API密钥的文件
   grep -r "sk-" --include="*.py" --include="*.json" .
   ```

2. **删除敏感配置**：

   ```bash
   # 如果您已经使用过API密钥，请创建干净的模板
   python api_secrets.py --create-template
   ```

3. **确认.gitignore 正常工作**：

   ```bash
   # 查看哪些文件会被提交
   git add .
   git status
   ```

4. **使用预提交检查**（可选）：
   ```bash
   # 安装预提交钩子以自动检测密钥泄露
   pip install pre-commit
   pre-commit install
   ```

## 示例 JSON 格式

`examples.json`文件应包含以下格式的输入输出对：

```json
[
  {
    "input": "创建营销活动",
    "output": "# 营销活动\n\n## 目标受众\n..."
  },
  {
    "input": "解释机器学习",
    "output": "# 机器学习解释\n\n..."
  }
]
```

## 系统要求

- Python 3.7+
- 网络连接（用于 API 调用）
- 支持现代 Web 浏览器（Chrome, Firefox, Safari, Edge 等）

## 常见问题

**问**: 为什么我收到 API 错误？  
**答**: 请确保您的 API 密钥正确，并且有足够的配额。使用`python api_secrets.py --get`检查当前设置的 API 密钥。

**问**: 如何获得最佳结果？  
**答**: 提供详细、具体的需求描述，尝试不同的提示格式，并根据初始结果迭代改进。

**问**: 我可以保存我的配置吗？  
**答**: 是的，在侧边栏中点击"保存设置"按钮，设置将保存到 config.json 文件。请注意，保存 API 密钥到配置文件不是最安全的方法。

**问**: 如何防止 API 密钥泄露？  
**答**: 优先使用环境变量或.env 文件存储密钥，并确保这些文件已添加到.gitignore 中以避免上传到代码仓库。

**问**: 出现"No secrets files found"错误怎么办？  
**答**: 运行 `python quick_setup.py --auto` 自动创建必要的配置文件，或手动创建 `.streamlit/secrets.toml` 文件。

**问**: 如何快速体验新功能？  
**答**: 运行 `python demo_features.py` 查看功能演示，或直接启动 Web 应用体验完整功能。

## 许可证

JUNSHENGMA SONGFEN 爆杀肥尧
