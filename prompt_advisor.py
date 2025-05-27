#!/usr/bin/env python3
"""
智能Prompt建议器
分析用户的编程需求，推荐最适合的模板和改进建议
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from programming_prompt_templates import (
    ProgrammingPromptTemplates, ProgrammingTaskType, AITool, get_programming_templates
)

@dataclass
class PromptAnalysis:
    """Prompt分析结果"""
    detected_task_type: ProgrammingTaskType
    confidence: float
    detected_language: str
    detected_ai_tool: AITool
    keywords: List[str]
    complexity_level: str  # simple, medium, complex
    missing_info: List[str]

@dataclass
class PromptRecommendation:
    """Prompt推荐"""
    template_id: str
    template_name: str
    relevance_score: float
    reasons: List[str]
    improvements: List[str]
    example_prompt: str

class PromptAdvisor:
    """智能Prompt建议器"""
    
    def __init__(self):
        self.templates = get_programming_templates()
        self.task_keywords = self._load_task_keywords()
        self.language_keywords = self._load_language_keywords()
        self.ai_tool_keywords = self._load_ai_tool_keywords()
        self.quality_patterns = self._load_quality_patterns()
    
    def _load_task_keywords(self) -> Dict[ProgrammingTaskType, List[str]]:
        """加载任务类型关键词"""
        return {
            ProgrammingTaskType.CODE_GENERATION: [
                "创建", "生成", "编写", "实现", "开发", "构建", "制作",
                "function", "class", "module", "component", "写一个", "做一个"
            ],
            ProgrammingTaskType.CODE_REVIEW: [
                "审查", "检查", "评估", "分析", "review", "check", "evaluate",
                "看看", "帮我看", "有什么问题", "质量如何", "优化建议"
            ],
            ProgrammingTaskType.BUG_FIXING: [
                "修复", "解决", "bug", "error", "错误", "问题", "调试", "debug",
                "不工作", "失败", "异常", "报错", "崩溃"
            ],
            ProgrammingTaskType.CODE_REFACTORING: [
                "重构", "优化", "改进", "重写", "refactor", "improve", "optimize",
                "重新组织", "清理", "简化", "性能"
            ],
            ProgrammingTaskType.CODE_EXPLANATION: [
                "解释", "说明", "理解", "explain", "understand", "what does",
                "这个代码", "怎么工作", "原理", "逻辑"
            ],
            ProgrammingTaskType.API_DESIGN: [
                "api", "接口", "endpoint", "rest", "graphql", "服务",
                "设计接口", "api设计", "后端接口"
            ],
            ProgrammingTaskType.TESTING: [
                "测试", "test", "单元测试", "集成测试", "测试用例",
                "unittest", "pytest", "jest", "测试覆盖"
            ],
            ProgrammingTaskType.DOCUMENTATION: [
                "文档", "注释", "说明", "documentation", "comment", "readme",
                "使用说明", "api文档"
            ],
            ProgrammingTaskType.OPTIMIZATION: [
                "优化", "性能", "速度", "效率", "optimize", "performance",
                "加快", "改善", "提升"
            ]
        }
    
    def _load_language_keywords(self) -> Dict[str, List[str]]:
        """加载编程语言关键词"""
        return {
            "Python": ["python", "py", "django", "flask", "pandas", "numpy", "pip"],
            "JavaScript": ["javascript", "js", "node", "react", "vue", "angular", "npm"],
            "TypeScript": ["typescript", "ts", "tsx"],
            "Java": ["java", "spring", "maven", "gradle"],
            "C++": ["c++", "cpp", "c plus plus"],
            "C#": ["c#", "csharp", "dotnet", ".net"],
            "Go": ["go", "golang"],
            "Rust": ["rust", "cargo"],
            "PHP": ["php", "laravel", "composer"],
            "Ruby": ["ruby", "rails", "gem"],
            "Swift": ["swift", "ios", "xcode"],
            "Kotlin": ["kotlin", "android"],
            "SQL": ["sql", "mysql", "postgresql", "sqlite", "数据库查询"]
        }
    
    def _load_ai_tool_keywords(self) -> Dict[AITool, List[str]]:
        """加载AI工具关键词"""
        return {
            AITool.CURSOR: ["cursor", "cursor ai", "cursor编辑器"],
            AITool.GITHUB_COPILOT: ["copilot", "github copilot", "副驾驶"],
            AITool.CODEWHISPERER: ["codewhisperer", "aws codewhisperer"],
            AITool.TABNINE: ["tabnine"],
            AITool.CHATGPT: ["chatgpt", "gpt", "openai"],
            AITool.CLAUDE: ["claude", "anthropic"]
        }
    
    def _load_quality_patterns(self) -> Dict[str, List[str]]:
        """加载质量检查模式"""
        return {
            "missing_context": [
                "没有提供具体的编程语言",
                "缺少项目背景信息",
                "没有说明预期的输入输出",
                "缺少技术栈信息",
                "没有指明具体的AI工具"
            ],
            "vague_requirements": [
                "需求描述过于模糊",
                "没有具体的功能要求",
                "缺少边界条件说明",
                "性能要求不明确"
            ],
            "good_practices": [
                "包含具体的编程语言",
                "提供了清晰的功能描述",
                "包含了输入输出说明",
                "有具体的技术要求"
            ]
        }
    
    def analyze_user_input(self, user_input: str) -> PromptAnalysis:
        """分析用户输入"""
        user_input_lower = user_input.lower()
        
        # 检测任务类型
        task_type, task_confidence = self._detect_task_type(user_input_lower)
        
        # 检测编程语言
        language = self._detect_language(user_input_lower)
        
        # 检测AI工具
        ai_tool = self._detect_ai_tool(user_input_lower)
        
        # 提取关键词
        keywords = self._extract_keywords(user_input_lower)
        
        # 评估复杂度
        complexity = self._assess_complexity(user_input)
        
        # 识别缺失信息
        missing_info = self._identify_missing_info(user_input_lower, task_type)
        
        return PromptAnalysis(
            detected_task_type=task_type,
            confidence=task_confidence,
            detected_language=language,
            detected_ai_tool=ai_tool,
            keywords=keywords,
            complexity_level=complexity,
            missing_info=missing_info
        )
    
    def _detect_task_type(self, text: str) -> Tuple[ProgrammingTaskType, float]:
        """检测任务类型"""
        scores = {}
        
        for task_type, keywords in self.task_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            scores[task_type] = score
        
        if not scores or max(scores.values()) == 0:
            return ProgrammingTaskType.CODE_GENERATION, 0.3
        
        best_task = max(scores, key=scores.get)
        confidence = min(scores[best_task] / len(self.task_keywords[best_task]), 1.0)
        
        return best_task, confidence
    
    def _detect_language(self, text: str) -> str:
        """检测编程语言"""
        for language, keywords in self.language_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return language
        return "通用"
    
    def _detect_ai_tool(self, text: str) -> AITool:
        """检测AI工具"""
        for tool, keywords in self.ai_tool_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return tool
        return AITool.GENERAL
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取逻辑
        words = re.findall(r'\b\w+\b', text)
        programming_words = []
        
        for word in words:
            if len(word) > 3 and word in ['function', 'class', 'api', 'test', 'database', 'algorithm']:
                programming_words.append(word)
        
        return programming_words[:10]  # 返回前10个关键词
    
    def _assess_complexity(self, text: str) -> str:
        """评估复杂度"""
        length = len(text)
        technical_terms = len(re.findall(r'\b(api|database|algorithm|architecture|microservice|optimization)\b', text.lower()))
        
        if length < 50 and technical_terms == 0:
            return "simple"
        elif length < 200 and technical_terms <= 2:
            return "medium"
        else:
            return "complex"
    
    def _identify_missing_info(self, text: str, task_type: ProgrammingTaskType) -> List[str]:
        """识别缺失信息"""
        missing = []
        
        # 检查是否缺少编程语言
        if not self._detect_language(text):
            missing.append("编程语言")
        
        # 根据任务类型检查特定信息
        if task_type == ProgrammingTaskType.CODE_GENERATION:
            if "输入" not in text and "参数" not in text:
                missing.append("输入参数说明")
            if "返回" not in text and "输出" not in text:
                missing.append("返回值说明")
        
        elif task_type == ProgrammingTaskType.BUG_FIXING:
            if "错误" not in text and "error" not in text:
                missing.append("错误信息")
            if "步骤" not in text:
                missing.append("复现步骤")
        
        elif task_type == ProgrammingTaskType.API_DESIGN:
            if "数据库" not in text and "database" not in text:
                missing.append("数据库信息")
            if "认证" not in text and "auth" not in text:
                missing.append("认证方式")
        
        return missing
    
    def recommend_template(self, analysis: PromptAnalysis) -> List[PromptRecommendation]:
        """推荐模板"""
        recommendations = []
        
        # 获取匹配的模板
        task_templates = self.templates.get_templates_by_task_type(analysis.detected_task_type)
        tool_templates = self.templates.get_templates_by_ai_tool(analysis.detected_ai_tool)
        
        # 合并并去重
        candidate_templates = {t.name: t for t in task_templates + tool_templates}.values()
        
        for template in candidate_templates:
            score = self._calculate_relevance_score(template, analysis)
            reasons = self._generate_reasons(template, analysis)
            improvements = self._suggest_improvements(analysis)
            
            # 生成示例prompt (简化版)
            example_prompt = self._generate_example_prompt(template, analysis)
            
            recommendation = PromptRecommendation(
                template_id=list(self.templates.templates.keys())[
                    list(self.templates.templates.values()).index(template)
                ],
                template_name=template.name,
                relevance_score=score,
                reasons=reasons,
                improvements=improvements,
                example_prompt=example_prompt
            )
            
            recommendations.append(recommendation)
        
        # 按相关性排序
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:3]  # 返回前3个推荐
    
    def _calculate_relevance_score(self, template, analysis: PromptAnalysis) -> float:
        """计算相关性得分"""
        score = 0.0
        
        # 任务类型匹配
        if template.task_type == analysis.detected_task_type:
            score += 0.4
        
        # AI工具匹配
        if template.ai_tool == analysis.detected_ai_tool or template.ai_tool == AITool.GENERAL:
            score += 0.3
        
        # 复杂度匹配
        if analysis.complexity_level == "complex" and "详细" in template.description:
            score += 0.2
        elif analysis.complexity_level == "simple" and "简单" in template.description:
            score += 0.2
        
        # 置信度影响
        score *= (0.5 + analysis.confidence * 0.5)
        
        return min(score, 1.0)
    
    def _generate_reasons(self, template, analysis: PromptAnalysis) -> List[str]:
        """生成推荐理由"""
        reasons = []
        
        if template.task_type == analysis.detected_task_type:
            reasons.append(f"匹配您的任务类型：{analysis.detected_task_type.value}")
        
        if template.ai_tool == analysis.detected_ai_tool:
            reasons.append(f"专门针对{analysis.detected_ai_tool.value}优化")
        
        if analysis.detected_language != "通用":
            reasons.append(f"支持{analysis.detected_language}编程语言")
        
        if analysis.complexity_level == "complex":
            reasons.append("提供详细的实现指导")
        
        return reasons
    
    def _suggest_improvements(self, analysis: PromptAnalysis) -> List[str]:
        """建议改进"""
        improvements = []
        
        for missing in analysis.missing_info:
            improvements.append(f"建议添加：{missing}")
        
        if analysis.confidence < 0.5:
            improvements.append("建议更明确地描述您的需求")
        
        if analysis.complexity_level == "simple":
            improvements.append("可以添加更多具体要求来获得更精确的结果")
        
        if not analysis.keywords:
            improvements.append("添加更多技术关键词有助于获得更准确的建议")
        
        return improvements
    
    def _generate_example_prompt(self, template, analysis: PromptAnalysis) -> str:
        """生成示例prompt（简化版）"""
        try:
            # 基于分析结果生成示例参数
            example_vars = {}
            for var in template.variables:
                if "language" in var:
                    example_vars[var] = analysis.detected_language
                elif "description" in var:
                    example_vars[var] = "示例功能描述"
                elif "code" in var:
                    example_vars[var] = "// 示例代码"
                else:
                    example_vars[var] = f"示例{var}"
            
            # 尝试生成示例
            example = template.template.format(**example_vars)
            return example[:300] + "..."  # 截取前300字符
        except:
            return template.template[:300] + "..."
    
    def analyze_and_recommend(self, user_input: str) -> Dict[str, Any]:
        """分析并推荐（主要接口）"""
        analysis = self.analyze_user_input(user_input)
        recommendations = self.recommend_template(analysis)
        
        return {
            "analysis": {
                "task_type": analysis.detected_task_type.value,
                "confidence": analysis.confidence,
                "language": analysis.detected_language,
                "ai_tool": analysis.detected_ai_tool.value,
                "complexity": analysis.complexity_level,
                "keywords": analysis.keywords,
                "missing_info": analysis.missing_info
            },
            "recommendations": [
                {
                    "template_id": rec.template_id,
                    "template_name": rec.template_name,
                    "relevance_score": rec.relevance_score,
                    "reasons": rec.reasons,
                    "improvements": rec.improvements,
                    "example_prompt": rec.example_prompt
                }
                for rec in recommendations
            ],
            "tips": self._generate_general_tips(analysis)
        }
    
    def _generate_general_tips(self, analysis: PromptAnalysis) -> List[str]:
        """生成通用建议"""
        tips = []
        
        if analysis.detected_ai_tool == AITool.CURSOR:
            tips.append("💡 在Cursor中，提供项目上下文和文件结构信息能获得更好的结果")
        
        if analysis.detected_ai_tool == AITool.GITHUB_COPILOT:
            tips.append("💡 使用注释形式描述需求，Copilot能更好地理解您的意图")
        
        if analysis.complexity_level == "complex":
            tips.append("💡 对于复杂任务，建议分步骤描述，每个步骤都要清晰明确")
        
        if analysis.detected_language != "通用":
            tips.append(f"💡 明确指定{analysis.detected_language}的版本和相关框架信息")
        
        tips.append("💡 提供具体的输入输出示例能显著提高AI的理解准确性")
        tips.append("💡 说明代码的使用场景和约束条件")
        
        return tips

def main():
    """演示功能"""
    advisor = PromptAdvisor()
    
    print("🤖 智能Prompt建议器")
    print("=" * 50)
    
    # 测试示例
    test_inputs = [
        "我想用Python创建一个函数来计算斐波那契数列",
        "帮我在Cursor中实现一个React登录组件",
        "这段JavaScript代码有bug，用户点击按钮没有反应",
        "设计一个RESTful API用于用户管理系统",
        "写单元测试给这个Python函数"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n📝 测试示例 {i}: {user_input}")
        print("-" * 40)
        
        result = advisor.analyze_and_recommend(user_input)
        
        print(f"🔍 分析结果:")
        analysis = result["analysis"]
        print(f"  任务类型: {analysis['task_type']} (置信度: {analysis['confidence']:.2f})")
        print(f"  编程语言: {analysis['language']}")
        print(f"  AI工具: {analysis['ai_tool']}")
        print(f"  复杂度: {analysis['complexity']}")
        
        if analysis["missing_info"]:
            print(f"  缺失信息: {', '.join(analysis['missing_info'])}")
        
        print(f"\n📋 推荐模板:")
        for j, rec in enumerate(result["recommendations"][:2], 1):
            print(f"  {j}. {rec['template_name']} (相关性: {rec['relevance_score']:.2f})")
            if rec["reasons"]:
                print(f"     理由: {rec['reasons'][0]}")
        
        if result["tips"]:
            print(f"\n💡 使用建议: {result['tips'][0]}")

if __name__ == "__main__":
    main() 