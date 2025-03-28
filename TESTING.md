# 测试指南

本文档提供了AI提示工程师项目的测试策略和指南，帮助开发人员确保代码质量和功能正确性。

## 目录

- [测试架构](#测试架构)
- [单元测试](#单元测试)
- [集成测试](#集成测试)
- [UI测试](#ui测试)
- [性能测试](#性能测试)
- [安全测试](#安全测试)
- [模拟API响应](#模拟api响应)
- [测试数据](#测试数据)
- [持续集成](#持续集成)
- [故障排除](#故障排除)

## 测试架构

项目使用以下测试框架和工具：

- **pytest**: 主要测试框架
- **unittest.mock**: 用于模拟外部依赖
- **pytest-cov**: 测试覆盖率报告
- **streamlit-test**: Streamlit应用测试
- **locust**: 性能测试

## 单元测试

单元测试位于`tests/unit`目录，专注于测试单个函数和类的行为。

### 运行单元测试

```bash
# 运行所有单元测试
pytest tests/unit

# 运行特定模块的测试
pytest tests/unit/test_api_secrets.py

# 运行特定测试
pytest tests/unit/test_api_secrets.py::test_get_api_key
```

### 编写单元测试

示例单元测试：

```python
# tests/unit/test_api_secrets.py
import pytest
from unittest.mock import patch, mock_open
from api_secrets import get_api_key, save_api_key

def test_get_api_key_from_env():
    with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
        assert get_api_key('deepseek') == 'test-key'

def test_get_api_key_from_file():
    mock_data = '{"api_key": "file-key", "api_provider": "deepseek"}'
    with patch('builtins.open', mock_open(read_data=mock_data)):
        with patch('os.path.exists', return_value=True):
            with patch.dict('os.environ', {}, clear=True):
                assert get_api_key('deepseek') == 'file-key'

def test_save_api_key():
    with patch('builtins.open', mock_open()) as mock_file:
        save_api_key('test-key', 'deepseek')
        mock_file.assert_called_once()
```

### 测试覆盖率

生成并查看测试覆盖率报告：

```bash
pytest --cov=. tests/
pytest --cov=. --cov-report=html tests/
```

## 集成测试

集成测试位于`tests/integration`目录，测试多个组件的交互。

### 运行集成测试

```bash
# 运行所有集成测试
pytest tests/integration

# 运行特定集成测试
pytest tests/integration/test_prompt_generation.py
```

### 编写集成测试

示例集成测试：

```python
# tests/integration/test_prompt_generation.py
import pytest
from auto_prompt_engineer import PromptEngineer
from prompt_engineer import generate_prompt

@pytest.fixture
def engineer():
    return PromptEngineer(api_provider='mock', temperature=0.7)

def test_end_to_end_generation(engineer):
    requirement = "创建一个健身应用的需求文档"
    result = generate_prompt(requirement, engineer, format="technical")
    assert len(result) > 0
    assert "功能需求" in result
```

## UI测试

UI测试位于`tests/ui`目录，测试Streamlit应用的功能。

### 运行UI测试

```bash
# 运行所有UI测试
pytest tests/ui

# 运行特定UI测试
pytest tests/ui/test_streamlit_app.py
```

### 编写UI测试

示例UI测试：

```python
# tests/ui/test_streamlit_app.py
import pytest
from streamlit.testing.v1 import AppTest

def test_app_loads():
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    assert not at.exception

def test_api_settings_sidebar():
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    
    # 测试API密钥输入组件存在
    api_key_input = at.sidebar.text_input[0]
    assert "API Key" in api_key_input.label
    
    # 测试API提供商选择组件存在
    provider_select = at.sidebar.selectbox[0]
    assert "API Provider" in provider_select.label
```

## 性能测试

使用Locust进行性能测试，测试脚本位于`tests/performance`目录。

### 运行性能测试

1. 启动API模拟服务器（位于`tests/performance/mock_api_server.py`）

```bash
python tests/performance/mock_api_server.py
```

2. 启动Locust

```bash
cd tests/performance
locust -f locustfile.py
```

3. 在Web浏览器中访问http://localhost:8089设置和查看测试

## 安全测试

安全测试位于`tests/security`目录，专注于测试API密钥管理和数据安全。

### 运行安全测试

```bash
pytest tests/security
```

### API密钥安全测试

示例安全测试：

```python
# tests/security/test_api_key_security.py
import pytest
import tempfile
import os
from api_secrets import save_api_key, mask_api_key

def test_api_key_not_stored_in_plaintext():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        try:
            # 保存API密钥
            save_api_key("test-api-key", "deepseek", file_path=tmp.name)
            
            # 验证文件中不包含明文API密钥
            with open(tmp.name, 'r') as f:
                content = f.read()
                assert "test-api-key" not in content
        finally:
            os.unlink(tmp.name)

def test_api_key_masking():
    # 测试API密钥掩码功能
    masked = mask_api_key("sk-abcdefghijklmnopqrstuvwxyz")
    assert masked == "sk-abc...xyz"
    assert len(masked) < 20
```

## 模拟API响应

使用`unittest.mock`和自定义模拟来模拟API响应：

```python
# tests/mocks/api_mock.py
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)
        
    def json(self):
        return self.json_data

def mock_openai_response(*args, **kwargs):
    return MockResponse({
        "choices": [
            {
                "message": {
                    "content": "这是一个测试提示: 编写一个健身应用的需求文档。"
                }
            }
        ]
    })

def mock_deepseek_response(*args, **kwargs):
    return MockResponse({
        "choices": [
            {
                "message": {
                    "content": "这是一个测试提示: 编写一个健身应用的需求文档。"
                }
            }
        ]
    })
```

使用模拟响应：

```python
# 在测试中使用模拟
@patch('requests.post', side_effect=mock_openai_response)
def test_api_call(mock_post):
    engineer = PromptEngineer(api_provider='openai')
    result = engineer.generate_prompt("测试需求")
    assert "测试提示" in result
    mock_post.assert_called_once()
```

## 测试数据

测试数据位于`tests/data`目录，包括：

- 示例用户需求
- 预期的提示输出
- 模拟API响应

示例测试数据文件：

```json
// tests/data/sample_requirements.json
{
  "requirements": [
    {
      "input": "健身应用需求文档",
      "expected_format": "technical",
      "expected_keywords": ["功能需求", "用户界面", "数据存储"]
    },
    {
      "input": "智能家居产品营销文案",
      "expected_format": "marketing",
      "expected_keywords": ["便捷", "创新", "智能"]
    }
  ]
}
```

## 持续集成

项目使用GitHub Actions进行持续集成，配置文件位于`.github/workflows/tests.yml`。

CI流程包括：
1. 运行所有单元测试
2. 运行集成测试
3. 检查测试覆盖率
4. 进行静态代码分析
5. 检查依赖安全性

## 故障排除

### 常见问题

1. **测试期间的API密钥问题**

   解决方案：使用环境变量设置测试API密钥：
   ```bash
   export DEEPSEEK_API_KEY="test-key"
   export OPENAI_API_KEY="test-key"
   ```
   
   或者在pytest中使用mock：
   ```python
   @pytest.fixture(autouse=True)
   def mock_env_vars():
       with patch.dict('os.environ', {
           'DEEPSEEK_API_KEY': 'test-key',
           'OPENAI_API_KEY': 'test-key'
       }):
           yield
   ```

2. **模拟外部API调用**

   解决方案：使用requests-mock库：
   ```bash
   pip install requests-mock
   ```
   
   ```python
   import requests_mock
   
   def test_api_call():
       with requests_mock.Mocker() as m:
           m.post('https://api.deepseek.com/v1/chat/completions', json={
               "choices": [{"message": {"content": "测试响应"}}]
           })
           # 进行API调用测试
   ```

3. **提高测试覆盖率**

   解决方案：使用pytest-cov识别未覆盖的代码路径：
   ```bash
   pytest --cov=. --cov-report=term-missing tests/
   ```

---

*最后更新: 2023年12月* 