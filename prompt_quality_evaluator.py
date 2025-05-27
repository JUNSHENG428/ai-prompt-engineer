"""
AI提示质量评估器
评估生成的提示词的质量，并提供改进建议
"""

import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class QualityMetric(Enum):
    """质量评估指标"""
    CLARITY = "clarity"           # 清晰度
    SPECIFICITY = "specificity"   # 具体性
    COMPLETENESS = "completeness" # 完整性
    STRUCTURE = "structure"       # 结构性
    ACTIONABILITY = "actionability" # 可操作性

@dataclass
class QualityScore:
    """质量评分"""
    metric: QualityMetric
    score: float  # 0-10分
    explanation: str
    suggestions: List[str]

@dataclass
class QualityReport:
    """质量评估报告"""
    overall_score: float
    scores: List[QualityScore]
    strengths: List[str]
    improvements: List[str]
    grade: str  # A+, A, B+, B, C+, C, D

class PromptQualityEvaluator:
    """提示质量评估器"""
    
    def __init__(self):
        self.clarity_keywords = [
            "明确", "清楚", "具体", "详细", "准确", 
            "clear", "specific", "detailed", "precise"
        ]
        self.structure_indicators = [
            "##", "###", "1.", "2.", "3.", "-", "*", 
            "步骤", "要求", "格式", "输出"
        ]
        self.action_words = [
            "创建", "生成", "分析", "设计", "实现", "优化",
            "create", "generate", "analyze", "design", "implement"
        ]
    
    def evaluate_prompt(self, prompt: str, requirement: str = "") -> QualityReport:
        """
        评估提示质量
        
        Args:
            prompt: 要评估的提示词
            requirement: 原始需求（可选）
            
        Returns:
            QualityReport: 质量评估报告
        """
        scores = []
        
        # 评估各项指标
        scores.append(self._evaluate_clarity(prompt))
        scores.append(self._evaluate_specificity(prompt))
        scores.append(self._evaluate_completeness(prompt, requirement))
        scores.append(self._evaluate_structure(prompt))
        scores.append(self._evaluate_actionability(prompt))
        
        # 计算总分
        overall_score = sum(score.score for score in scores) / len(scores)
        
        # 确定等级
        grade = self._calculate_grade(overall_score)
        
        # 生成优势和改进建议
        strengths = self._identify_strengths(scores)
        improvements = self._generate_improvements(scores)
        
        return QualityReport(
            overall_score=round(overall_score, 1),
            scores=scores,
            strengths=strengths,
            improvements=improvements,
            grade=grade
        )
    
    def _evaluate_clarity(self, prompt: str) -> QualityScore:
        """评估清晰度"""
        score = 5.0  # 基础分
        explanations = []
        suggestions = []
        
        # 检查长度适中
        word_count = len(prompt.split())
        if 50 <= word_count <= 500:
            score += 1.0
            explanations.append("长度适中，易于理解")
        elif word_count < 50:
            score -= 1.0
            explanations.append("过于简短，可能缺乏必要信息")
            suggestions.append("增加更多细节和上下文")
        else:
            score -= 0.5
            explanations.append("较长，但仍可接受")
            suggestions.append("考虑简化表达")
        
        # 检查明确的指令
        if any(word in prompt.lower() for word in ["请", "需要", "要求", "should", "must", "please"]):
            score += 1.0
            explanations.append("包含明确的指令词")
        else:
            score -= 1.0
            suggestions.append("使用更明确的指令词")
        
        # 检查专业术语的解释
        technical_terms = len(re.findall(r'[A-Z]{2,}|[a-z]+[A-Z][a-z]*', prompt))
        if technical_terms > 0:
            if "解释" in prompt or "说明" in prompt:
                score += 0.5
                explanations.append("对专业术语提供了解释")
            else:
                suggestions.append("为专业术语提供必要的解释")
        
        return QualityScore(
            metric=QualityMetric.CLARITY,
            score=min(10.0, max(0.0, score)),
            explanation="; ".join(explanations) if explanations else "清晰度有待提高",
            suggestions=suggestions
        )
    
    def _evaluate_specificity(self, prompt: str) -> QualityScore:
        """评估具体性"""
        score = 5.0
        explanations = []
        suggestions = []
        
        # 检查具体的数字和度量
        numbers = len(re.findall(r'\d+', prompt))
        if numbers >= 3:
            score += 1.5
            explanations.append("包含具体的数字和度量")
        elif numbers >= 1:
            score += 0.5
            explanations.append("包含一些具体数据")
        else:
            score -= 1.0
            suggestions.append("添加具体的数字、时间或度量标准")
        
        # 检查具体的示例
        if "例如" in prompt or "比如" in prompt or "example" in prompt.lower():
            score += 1.0
            explanations.append("提供了具体示例")
        else:
            suggestions.append("添加具体的示例来说明要求")
        
        # 检查格式要求
        format_words = ["格式", "结构", "模板", "format", "structure"]
        if any(word in prompt.lower() for word in format_words):
            score += 1.0
            explanations.append("明确了输出格式要求")
        else:
            suggestions.append("明确指定期望的输出格式")
        
        # 检查约束条件
        constraint_words = ["不要", "避免", "限制", "约束", "don't", "avoid", "constraint"]
        if any(word in prompt.lower() for word in constraint_words):
            score += 0.5
            explanations.append("包含了约束条件")
        
        return QualityScore(
            metric=QualityMetric.SPECIFICITY,
            score=min(10.0, max(0.0, score)),
            explanation="; ".join(explanations) if explanations else "需要更具体的要求",
            suggestions=suggestions
        )
    
    def _evaluate_completeness(self, prompt: str, requirement: str) -> QualityScore:
        """评估完整性"""
        score = 5.0
        explanations = []
        suggestions = []
        
        # 检查关键组件
        components = {
            "任务描述": ["任务", "目标", "task", "goal"],
            "输出要求": ["输出", "结果", "生成", "output", "result"],
            "质量标准": ["质量", "标准", "要求", "quality", "standard"],
            "上下文": ["背景", "上下文", "环境", "context", "background"]
        }
        
        present_components = []
        for component, keywords in components.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                present_components.append(component)
        
        completion_ratio = len(present_components) / len(components)
        score += completion_ratio * 3.0
        
        if completion_ratio >= 0.75:
            explanations.append("包含了大部分必要组件")
        elif completion_ratio >= 0.5:
            explanations.append("包含了基本组件")
        else:
            explanations.append("缺少重要组件")
            suggestions.append("添加缺失的组件：" + ", ".join(
                comp for comp in components.keys() if comp not in present_components
            ))
        
        # 检查是否回应了原始需求
        if requirement and len(requirement) > 10:
            requirement_words = set(requirement.lower().split())
            prompt_words = set(prompt.lower().split())
            overlap = len(requirement_words & prompt_words)
            overlap_ratio = overlap / len(requirement_words)
            
            if overlap_ratio >= 0.3:
                score += 1.0
                explanations.append("很好地回应了原始需求")
            elif overlap_ratio >= 0.1:
                score += 0.5
                explanations.append("部分回应了原始需求")
            else:
                suggestions.append("更好地呼应原始需求中的关键词")
        
        return QualityScore(
            metric=QualityMetric.COMPLETENESS,
            score=min(10.0, max(0.0, score)),
            explanation="; ".join(explanations) if explanations else "完整性需要改进",
            suggestions=suggestions
        )
    
    def _evaluate_structure(self, prompt: str) -> QualityScore:
        """评估结构性"""
        score = 5.0
        explanations = []
        suggestions = []
        
        # 检查标题和分段
        lines = prompt.split('\n')
        
        # 标题检查
        headers = len([line for line in lines if line.strip().startswith('#')])
        if headers >= 3:
            score += 2.0
            explanations.append("有良好的标题结构")
        elif headers >= 1:
            score += 1.0
            explanations.append("包含标题")
        else:
            suggestions.append("使用标题来组织内容结构")
        
        # 列表检查
        lists = len([line for line in lines if re.match(r'^\s*[-*\d.]\s', line.strip())])
        if lists >= 3:
            score += 1.5
            explanations.append("使用了列表来组织信息")
        elif lists >= 1:
            score += 0.5
            explanations.append("包含一些列表")
        else:
            suggestions.append("使用列表来更好地组织信息")
        
        # 段落检查
        paragraphs = len([line for line in lines if line.strip() and not line.startswith('#')])
        if paragraphs >= 3:
            score += 1.0
            explanations.append("内容分段合理")
        
        # 逻辑流程检查
        sequence_words = ["首先", "然后", "最后", "接下来", "first", "then", "finally", "next"]
        if any(word in prompt.lower() for word in sequence_words):
            score += 0.5
            explanations.append("有清晰的逻辑流程")
        else:
            suggestions.append("使用序列词来指示逻辑流程")
        
        return QualityScore(
            metric=QualityMetric.STRUCTURE,
            score=min(10.0, max(0.0, score)),
            explanation="; ".join(explanations) if explanations else "结构需要改进",
            suggestions=suggestions
        )
    
    def _evaluate_actionability(self, prompt: str) -> QualityScore:
        """评估可操作性"""
        score = 5.0
        explanations = []
        suggestions = []
        
        # 检查动作词
        action_count = sum(1 for word in self.action_words if word in prompt.lower())
        if action_count >= 3:
            score += 2.0
            explanations.append("包含明确的行动指示")
        elif action_count >= 1:
            score += 1.0
            explanations.append("包含一些行动词")
        else:
            suggestions.append("使用更多明确的动作词")
        
        # 检查步骤说明
        step_patterns = [r'步骤\s*\d+', r'\d+\.\s', r'第[一二三四五六七八九十\d]+步']
        steps = sum(len(re.findall(pattern, prompt)) for pattern in step_patterns)
        if steps >= 3:
            score += 1.5
            explanations.append("提供了详细的步骤指导")
        elif steps >= 1:
            score += 0.5
            explanations.append("包含一些步骤说明")
        else:
            suggestions.append("分解为具体的执行步骤")
        
        # 检查验收标准
        verification_words = ["检查", "验证", "确认", "测试", "check", "verify", "test"]
        if any(word in prompt.lower() for word in verification_words):
            score += 1.0
            explanations.append("包含验收或检查标准")
        else:
            suggestions.append("添加验收或质量检查标准")
        
        return QualityScore(
            metric=QualityMetric.ACTIONABILITY,
            score=min(10.0, max(0.0, score)),
            explanation="; ".join(explanations) if explanations else "可操作性需要提升",
            suggestions=suggestions
        )
    
    def _calculate_grade(self, overall_score: float) -> str:
        """计算等级"""
        if overall_score >= 9.0:
            return "A+"
        elif overall_score >= 8.5:
            return "A"
        elif overall_score >= 8.0:
            return "A-"
        elif overall_score >= 7.5:
            return "B+"
        elif overall_score >= 7.0:
            return "B"
        elif overall_score >= 6.5:
            return "B-"
        elif overall_score >= 6.0:
            return "C+"
        elif overall_score >= 5.5:
            return "C"
        elif overall_score >= 5.0:
            return "C-"
        else:
            return "D"
    
    def _identify_strengths(self, scores: List[QualityScore]) -> List[str]:
        """识别优势"""
        strengths = []
        for score in scores:
            if score.score >= 8.0:
                strengths.append(f"{score.metric.value}: {score.explanation}")
        return strengths
    
    def _generate_improvements(self, scores: List[QualityScore]) -> List[str]:
        """生成改进建议"""
        improvements = []
        for score in scores:
            if score.score < 7.0 and score.suggestions:
                improvements.extend(score.suggestions)
        return improvements[:5]  # 限制最多5个建议
    
    def generate_detailed_report(self, report: QualityReport) -> str:
        """生成详细的评估报告"""
        report_lines = [
            "# 提示质量评估报告",
            "",
            f"## 总体评分: {report.overall_score}/10 (等级: {report.grade})",
            ""
        ]
        
        # 各项指标详情
        report_lines.append("## 详细评分")
        for score in report.scores:
            metric_name = {
                "clarity": "清晰度",
                "specificity": "具体性", 
                "completeness": "完整性",
                "structure": "结构性",
                "actionability": "可操作性"
            }.get(score.metric.value, score.metric.value)
            
            report_lines.extend([
                f"### {metric_name}: {score.score}/10",
                f"{score.explanation}",
                ""
            ])
        
        # 优势
        if report.strengths:
            report_lines.extend([
                "## 优势",
                ""
            ])
            for strength in report.strengths:
                report_lines.append(f"✅ {strength}")
            report_lines.append("")
        
        # 改进建议
        if report.improvements:
            report_lines.extend([
                "## 改进建议",
                ""
            ])
            for i, improvement in enumerate(report.improvements, 1):
                report_lines.append(f"{i}. {improvement}")
        
        return "\n".join(report_lines)

# 使用示例
def main():
    evaluator = PromptQualityEvaluator()
    
    # 示例提示
    sample_prompt = """
    # 创建博客文章

    ## 任务描述
    为我们的技术博客创建一篇关于人工智能的文章。

    ## 要求
    1. 文章长度：1500-2000字
    2. 目标受众：技术初学者
    3. 包含3-5个具体示例
    4. 使用简单易懂的语言

    ## 输出格式
    - 标题
    - 引言段落
    - 3-4个主要章节
    - 结论
    """
    
    requirement = "写一篇关于人工智能的技术博客文章"
    report = evaluator.evaluate_prompt(sample_prompt, requirement)
    
    print(evaluator.generate_detailed_report(report))

if __name__ == "__main__":
    main() 