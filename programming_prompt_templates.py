#!/usr/bin/env python3
"""
编程Prompt模板库
为AI编程提供常见场景的预设模板和最佳实践指导
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class ProgrammingTaskType(Enum):
    """编程任务类型"""
    CODE_GENERATION = "code_generation"          # 代码生成
    CODE_REVIEW = "code_review"                  # 代码审查
    BUG_FIXING = "bug_fixing"                    # Bug修复
    CODE_REFACTORING = "refactoring"             # 代码重构
    CODE_EXPLANATION = "code_explanation"         # 代码解释
    API_DESIGN = "api_design"                    # API设计
    DATABASE_DESIGN = "database_design"          # 数据库设计
    TESTING = "testing"                          # 测试编写
    DOCUMENTATION = "documentation"              # 文档编写
    OPTIMIZATION = "optimization"                # 性能优化
    ARCHITECTURE_DESIGN = "architecture_design"  # 架构设计
    DEPLOYMENT = "deployment"                    # 部署配置

class AITool(Enum):
    """AI编程工具"""
    CURSOR = "cursor"
    GITHUB_COPILOT = "github_copilot"
    CODEWHISPERER = "codewhisperer"
    TABNINE = "tabnine"
    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GENERAL = "general"

@dataclass
class PromptTemplate:
    """Prompt模板"""
    name: str
    description: str
    task_type: ProgrammingTaskType
    ai_tool: AITool
    template: str
    variables: List[str]  # 需要用户填充的变量
    tips: List[str]       # 使用技巧
    examples: List[str]   # 示例

class ProgrammingPromptTemplates:
    """编程Prompt模板管理器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, PromptTemplate]:
        """加载所有模板"""
        templates = {}
        
        # 代码生成模板
        templates["function_generation"] = PromptTemplate(
            name="函数生成",
            description="生成特定功能的函数",
            task_type=ProgrammingTaskType.CODE_GENERATION,
            ai_tool=AITool.GENERAL,
            template="""请帮我创建一个{language}函数，具体要求如下：

**功能描述**: {function_description}

**输入参数**: 
{input_parameters}

**返回值**: 
{return_value}

**具体要求**:
1. 函数名要清晰明确，遵循{language}命名规范
2. 添加详细的文档字符串和注释
3. 包含必要的错误处理和边界条件检查
4. 代码要简洁高效，易于理解和维护
5. 如果涉及复杂逻辑，请提供逐步实现思路

**额外约束**: {constraints}

请提供完整的函数实现，并解释关键部分的设计思路。""",
            variables=["language", "function_description", "input_parameters", "return_value", "constraints"],
            tips=[
                "详细描述函数的预期行为",
                "明确指定输入输出类型",
                "提及性能要求或特殊约束",
                "说明错误处理需求"
            ],
            examples=[
                "创建一个Python函数计算两个日期之间的工作日天数",
                "实现一个JavaScript函数验证邮箱地址格式"
            ]
        )
        
        # Cursor专用模板
        templates["cursor_feature_implementation"] = PromptTemplate(
            name="Cursor功能实现",
            description="在Cursor中实现新功能",
            task_type=ProgrammingTaskType.CODE_GENERATION,
            ai_tool=AITool.CURSOR,
            template="""我正在使用Cursor开发一个{project_type}项目，需要实现以下功能：

**项目背景**:
- 技术栈: {tech_stack}
- 项目结构: {project_structure}
- 当前代码位置: {current_location}

**功能需求**:
{feature_description}

**实现要求**:
1. 遵循项目现有的代码风格和架构模式
2. 创建或修改相关文件: {files_to_modify}
3. 确保与现有代码的兼容性
4. 添加适当的错误处理和日志记录
5. 包含必要的类型定义（如果使用TypeScript）

**集成要求**:
- 需要与现有的{existing_components}组件集成
- 考虑数据流和状态管理
- 确保UI/UX一致性

请提供完整的实现方案，包括文件结构建议和分步实现指导。""",
            variables=["project_type", "tech_stack", "project_structure", "current_location", 
                      "feature_description", "files_to_modify", "existing_components"],
            tips=[
                "明确说明项目的技术栈和架构",
                "指出需要修改或创建的具体文件",
                "提供现有代码的上下文",
                "说明与其他组件的集成要求"
            ],
            examples=[
                "在React项目中添加用户认证功能",
                "为Node.js API添加数据缓存层"
            ]
        )
        
        # 代码审查模板
        templates["code_review"] = PromptTemplate(
            name="代码审查",
            description="对代码进行全面审查",
            task_type=ProgrammingTaskType.CODE_REVIEW,
            ai_tool=AITool.GENERAL,
            template="""请对以下{language}代码进行全面的代码审查：

```{language}
{code_content}
```

**审查重点**:
1. **代码质量**: 可读性、可维护性、命名规范
2. **性能问题**: 算法效率、内存使用、潜在瓶颈
3. **安全性**: 输入验证、权限检查、敏感信息处理
4. **错误处理**: 异常捕获、边界条件、错误恢复
5. **最佳实践**: 是否遵循{language}的最佳实践和设计模式
6. **测试覆盖**: 是否容易测试，缺失的测试场景

**输出格式**:
- 总体评分 (1-10分)
- 优点列表
- 问题和建议 (按优先级排序)
- 具体的改进代码示例
- 推荐的重构建议

**上下文信息**: {context_info}""",
            variables=["language", "code_content", "context_info"],
            tips=[
                "提供完整的代码片段",
                "说明代码的使用场景和环境",
                "指出特别关注的方面",
                "提供相关的业务背景"
            ],
            examples=[
                "审查一个用户注册功能的实现",
                "检查数据处理算法的效率"
            ]
        )
        
        # Bug修复模板
        templates["bug_fixing"] = PromptTemplate(
            name="Bug修复",
            description="定位和修复代码中的Bug",
            task_type=ProgrammingTaskType.BUG_FIXING,
            ai_tool=AITool.GENERAL,
            template="""我遇到了一个{language}程序的Bug，需要帮助分析和修复：

**Bug描述**:
{bug_description}

**错误信息**:
```
{error_message}
```

**相关代码**:
```{language}
{code_snippet}
```

**复现步骤**:
1. {reproduction_steps}

**预期行为**: {expected_behavior}
**实际行为**: {actual_behavior}

**环境信息**:
- {language}版本: {version}
- 操作系统: {os}
- 相关依赖: {dependencies}

**请帮我**:
1. 分析Bug的根本原因
2. 提供详细的修复方案
3. 解释为什么会发生这个问题
4. 给出修复后的完整代码
5. 建议如何预防类似问题

**额外上下文**: {additional_context}""",
            variables=["language", "bug_description", "error_message", "code_snippet", 
                      "reproduction_steps", "expected_behavior", "actual_behavior", 
                      "version", "os", "dependencies", "additional_context"],
            tips=[
                "提供完整的错误信息和堆栈跟踪",
                "包含能重现问题的最小代码示例",
                "详细描述预期和实际行为的差异",
                "提供相关的环境和配置信息"
            ],
            examples=[
                "修复用户登录后重定向失败的问题",
                "解决数据库查询结果不正确的Bug"
            ]
        )
        
        # API设计模板
        templates["api_design"] = PromptTemplate(
            name="API设计",
            description="设计RESTful API或GraphQL API",
            task_type=ProgrammingTaskType.API_DESIGN,
            ai_tool=AITool.GENERAL,
            template="""请帮我设计一套{api_type} API，用于{business_domain}系统：

**业务需求**:
{business_requirements}

**核心实体**:
{entities}

**主要功能**:
{main_features}

**技术要求**:
- 框架: {framework}
- 数据库: {database}
- 认证方式: {authentication}
- 部署环境: {deployment}

**设计要求**:
1. 遵循{api_type}最佳实践
2. 合理的URL设计和HTTP方法使用
3. 统一的响应格式和错误处理
4. 适当的状态码使用
5. 考虑分页、过滤、排序等查询需求
6. 包含API文档规范

**性能和安全要求**:
- 预期QPS: {expected_qps}
- 响应时间要求: {response_time}
- 安全考虑: {security_requirements}

请提供：
1. 完整的API端点设计
2. 请求/响应数据结构
3. 错误码定义
4. 关键实现要点
5. API文档示例""",
            variables=["api_type", "business_domain", "business_requirements", "entities", 
                      "main_features", "framework", "database", "authentication", "deployment",
                      "expected_qps", "response_time", "security_requirements"],
            tips=[
                "明确业务领域和核心实体",
                "说明API的使用场景和用户",
                "提供性能和安全要求",
                "指定技术栈和约束条件"
            ],
            examples=[
                "设计电商系统的商品管理API",
                "创建用户管理和权限控制API"
            ]
        )
        
        # 测试编写模板
        templates["test_writing"] = PromptTemplate(
            name="测试编写",
            description="编写单元测试、集成测试等",
            task_type=ProgrammingTaskType.TESTING,
            ai_tool=AITool.GENERAL,
            template="""请为以下{language}代码编写全面的{test_type}测试：

**被测试代码**:
```{language}
{target_code}
```

**测试要求**:
1. 测试框架: {test_framework}
2. 覆盖率要求: {coverage_requirement}
3. 测试类型: {test_types}

**测试场景**:
- 正常情况测试: {normal_cases}
- 边界条件测试: {edge_cases}
- 异常情况测试: {error_cases}
- 性能测试要求: {performance_tests}

**Mock需求**:
{mock_requirements}

**测试数据**:
{test_data}

请提供：
1. 完整的测试代码
2. 测试用例说明
3. Mock对象设置
4. 断言验证逻辑
5. 测试运行指导
6. 测试报告解读

**特殊要求**: {special_requirements}""",
            variables=["language", "test_type", "target_code", "test_framework", 
                      "coverage_requirement", "test_types", "normal_cases", "edge_cases",
                      "error_cases", "performance_tests", "mock_requirements", 
                      "test_data", "special_requirements"],
            tips=[
                "提供被测代码的完整上下文",
                "明确测试类型和覆盖率要求",
                "说明需要Mock的外部依赖",
                "提供测试数据和预期结果"
            ],
            examples=[
                "为用户注册函数编写单元测试",
                "创建API端点的集成测试"
            ]
        )
        
        # GitHub Copilot优化模板
        templates["copilot_optimization"] = PromptTemplate(
            name="Copilot代码优化",
            description="配合GitHub Copilot进行代码优化",
            task_type=ProgrammingTaskType.OPTIMIZATION,
            ai_tool=AITool.GITHUB_COPILOT,
            template="""// 我需要优化以下{language}代码，请提供改进建议和重构方案

/* 当前代码背景:
 * 项目: {project_name}
 * 功能: {functionality}
 * 性能问题: {performance_issues}
 * 维护难点: {maintenance_issues}
 */

// TODO: 分析当前代码的问题
{current_code}

/* 优化目标:
 * 1. 性能优化: {performance_goals}
 * 2. 代码质量: {quality_goals}
 * 3. 可维护性: {maintainability_goals}
 * 4. 最佳实践: {best_practices}
 */

// TODO: 提供优化后的代码实现
// 要求:
// - 保持功能不变
// - 提高代码可读性
// - 优化算法复杂度
// - 减少重复代码
// - 添加适当注释

/* 请同时提供:
 * 1. 优化前后的性能对比
 * 2. 代码结构改进说明
 * 3. 潜在风险和注意事项
 * 4. 测试建议
 */""",
            variables=["language", "project_name", "functionality", "performance_issues",
                      "maintenance_issues", "current_code", "performance_goals", 
                      "quality_goals", "maintainability_goals", "best_practices"],
            tips=[
                "用注释形式提供上下文，便于Copilot理解",
                "使用TODO标记明确希望Copilot完成的任务",
                "在注释中说明优化目标和约束",
                "提供具体的性能指标和质量要求"
            ],
            examples=[
                "优化数据处理算法的性能",
                "重构复杂的业务逻辑代码"
            ]
        )
        
        return templates
    
    def get_template(self, template_id: str) -> PromptTemplate:
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def get_templates_by_task_type(self, task_type: ProgrammingTaskType) -> List[PromptTemplate]:
        """根据任务类型获取模板"""
        return [template for template in self.templates.values() 
                if template.task_type == task_type]
    
    def get_templates_by_ai_tool(self, ai_tool: AITool) -> List[PromptTemplate]:
        """根据AI工具获取模板"""
        return [template for template in self.templates.values() 
                if template.ai_tool == ai_tool or template.ai_tool == AITool.GENERAL]
    
    def list_all_templates(self) -> List[PromptTemplate]:
        """获取所有模板"""
        return list(self.templates.values())
    
    def generate_prompt(self, template_id: str, **kwargs) -> str:
        """基于模板生成prompt"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板 {template_id} 不存在")
        
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"缺少必需的变量: {missing_var}")
    
    def get_template_info(self, template_id: str) -> Dict[str, Any]:
        """获取模板信息"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        return {
            "name": template.name,
            "description": template.description,
            "task_type": template.task_type.value,
            "ai_tool": template.ai_tool.value,
            "variables": template.variables,
            "tips": template.tips,
            "examples": template.examples
        }

# 便捷函数
def get_programming_templates() -> ProgrammingPromptTemplates:
    """获取编程模板管理器实例"""
    return ProgrammingPromptTemplates()

def list_task_types() -> List[str]:
    """列出所有任务类型"""
    return [task.value for task in ProgrammingTaskType]

def list_ai_tools() -> List[str]:
    """列出所有AI工具"""
    return [tool.value for tool in AITool]

def main():
    """演示功能"""
    templates = get_programming_templates()
    
    print("📚 编程Prompt模板库")
    print("=" * 50)
    
    # 列出所有模板
    print("\n可用模板:")
    for i, template in enumerate(templates.list_all_templates(), 1):
        print(f"{i}. {template.name} ({template.task_type.value}) - {template.description}")
    
    # 演示模板使用
    print("\n" + "=" * 50)
    print("📝 模板使用示例:")
    
    template_id = "function_generation"
    template_info = templates.get_template_info(template_id)
    
    print(f"\n模板: {template_info['name']}")
    print(f"描述: {template_info['description']}")
    print(f"需要的变量: {', '.join(template_info['variables'])}")
    print(f"使用技巧: {template_info['tips'][0]}")
    
    # 生成示例prompt
    try:
        example_prompt = templates.generate_prompt(
            template_id,
            language="Python",
            function_description="计算两个日期之间的工作日天数",
            input_parameters="start_date (datetime), end_date (datetime)",
            return_value="int - 工作日天数",
            constraints="排除周末和指定的节假日"
        )
        print(f"\n生成的Prompt预览:")
        print("-" * 30)
        print(example_prompt[:200] + "...")
    except ValueError as e:
        print(f"生成示例失败: {e}")

if __name__ == "__main__":
    main() 