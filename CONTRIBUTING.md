# 贡献指南

感谢您考虑为AI提示工程师项目做出贡献！本文档提供了贡献代码、报告问题以及提交功能请求的指南。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
  - [报告问题](#报告问题)
  - [提交更改](#提交更改)
  - [代码审查过程](#代码审查过程)
- [开发指南](#开发指南)
  - [项目架构](#项目架构)
  - [开发环境设置](#开发环境设置)
  - [测试](#测试)
  - [代码风格](#代码风格)
- [API密钥安全注意事项](#api密钥安全注意事项)
- [资源](#资源)

## 行为准则

本项目遵循贡献者契约行为准则。参与即表示您同意遵守其条款。

## 如何贡献

### 报告问题

1. 使用GitHub Issues页面报告问题。
2. 使用提供的问题模板，填写所有必需的字段。
3. 请提供：
   - 清晰、描述性的标题
   - 重现问题的详细步骤
   - 您期望的行为
   - 实际发生的行为
   - 系统信息（操作系统、Python版本等）
   - 任何可能相关的日志或截图

### 提交更改

1. Fork仓库并创建您的特性分支：
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. 进行更改并提交您的代码：
   ```bash
   git commit -m '添加一些令人惊叹的功能'
   ```

3. 推送到分支：
   ```bash
   git push origin feature/amazing-feature
   ```

4. 提交Pull Request。

### 代码审查过程

所有提交都需要通过代码审查。审查者将关注：
- 代码质量
- 代码风格一致性
- 测试覆盖率
- 文档

## 开发指南

### 项目架构

AI提示工程师项目主要包含以下组件：

- `auto_prompt_engineer.py` - 核心提示工程逻辑
- `prompt_engineer.py` - 命令行界面
- `streamlit_app.py` - 图形用户界面
- `api_secrets.py` - API密钥管理
- 各种辅助模块和工具

### 开发环境设置

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/ai-prompt-engineer.git
   cd ai-prompt-engineer
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. 安装开发依赖：
   ```bash
   pip install -r requirements-dev.txt
   ```

4. 安装pre-commit钩子：
   ```bash
   pre-commit install
   ```

### 测试

运行测试套件：

```bash
pytest
```

为新功能添加测试。我们使用pytest进行单元测试和集成测试。

### 代码风格

我们遵循PEP 8风格指南。使用以下工具确保代码风格一致：

```bash
# 检查代码风格
flake8 .

# 自动格式化代码
black .
```

## API密钥安全注意事项

处理API密钥时请遵循以下安全最佳实践：

1. **永远不要**将实际API密钥提交到代码仓库。
2. **不要**在代码中硬编码API密钥。
3. **不要**在日志中打印API密钥。
4. **始终**使用环境变量或安全密钥存储机制。
5. 编写处理API密钥的代码时：
   - 使用`api_secrets.py`模块中的函数
   - 确保密钥只在内存中保留必要的时间
   - 考虑使用掩码技术显示部分隐藏的密钥（如`sk-***...abc`）

## 资源

- [Python风格指南](https://www.python.org/dev/peps/pep-0008/)
- [Streamlit文档](https://docs.streamlit.io/)
- [OpenAI API文档](https://platform.openai.com/docs/api-reference)
- [DeepSeek API文档](https://platform.deepseek.com/docs)

感谢您的贡献！ 