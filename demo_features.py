#!/usr/bin/env python3
"""
功能演示脚本
展示AI提示工程师的新功能：编程模板和智能建议器
"""

import time
from programming_prompt_templates import get_programming_templates, list_task_types, list_ai_tools
from prompt_advisor import PromptAdvisor

def demo_programming_templates():
    """演示编程模板功能"""
    print("🧑‍💻 编程模板库演示")
    print("=" * 50)
    
    # 初始化模板管理器
    templates = get_programming_templates()
    
    print(f"📚 已加载 {len(templates.list_all_templates())} 个编程模板")
    print(f"🎯 支持 {len(list_task_types())} 种任务类型")
    print(f"🤖 支持 {len(list_ai_tools())} 种AI工具")
    
    print("\n📋 可用模板列表:")
    for i, template in enumerate(templates.list_all_templates(), 1):
        print(f"  {i}. {template.name} - {template.description}")
    
    print("\n✨ 演示：生成函数创建模板")
    print("-" * 30)
    
    # 演示函数生成模板
    template_vars = {
        "language": "Python",
        "function_description": "计算斐波那契数列的第n项",
        "input_parameters": "n (int) - 要计算的项数",
        "return_value": "int - 斐波那契数列的第n项",
        "constraints": "n必须为非负整数，n=0返回0，n=1返回1"
    }
    
    prompt = templates.generate_prompt("function_generation", **template_vars)
    print("生成的Prompt:")
    print("```")
    print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
    print("```")
    
    return True

def demo_prompt_advisor():
    """演示智能建议器功能"""
    print("\n🤖 智能建议器演示")
    print("=" * 50)
    
    # 初始化建议器
    advisor = PromptAdvisor()
    
    # 测试用例
    test_cases = [
        "我想用Python创建一个函数来处理CSV文件数据，需要读取、清洗和分析数据",
        "帮我在Cursor中实现一个React登录组件，包含用户名密码验证",
        "这段JavaScript代码有bug，用户点击按钮没有反应，需要调试",
        "设计一个RESTful API用于电商系统的用户管理",
        "为我的Python函数编写单元测试，确保覆盖所有边界条件"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}:")
        print(f"输入: {test_input}")
        print("-" * 40)
        
        try:
            result = advisor.analyze_and_recommend(test_input)
            analysis = result["analysis"]
            
            print(f"🔍 分析结果:")
            print(f"  任务类型: {analysis['task_type']} (置信度: {analysis['confidence']:.1%})")
            print(f"  编程语言: {analysis['language']}")
            print(f"  AI工具: {analysis['ai_tool']}")
            print(f"  复杂度: {analysis['complexity']}")
            
            if analysis["keywords"]:
                print(f"  关键词: {', '.join(analysis['keywords'])}")
            
            if analysis["missing_info"]:
                print(f"  缺失信息: {', '.join(analysis['missing_info'])}")
            
            recommendations = result["recommendations"]
            if recommendations:
                best_rec = recommendations[0]
                print(f"📋 最佳推荐: {best_rec['template_name']} (相关性: {best_rec['relevance_score']:.1%})")
                if best_rec["reasons"]:
                    print(f"  推荐理由: {best_rec['reasons'][0]}")
            
            tips = result["tips"]
            if tips:
                print(f"💡 使用建议: {tips[0]}")
                
        except Exception as e:
            print(f"❌ 分析失败: {e}")
        
        if i < len(test_cases):
            time.sleep(1)  # 短暂暂停，便于阅读

def demo_integration():
    """演示集成功能"""
    print("\n🔗 集成功能演示")
    print("=" * 50)
    
    print("📱 Streamlit Web应用功能:")
    print("  ✅ 编程模板标签页 - 交互式模板选择和生成")
    print("  ✅ 智能建议标签页 - 需求分析和模板推荐")
    print("  ✅ 质量评估标签页 - 提示词质量评估")
    print("  ✅ 历史记录管理 - 保存和复用生成的提示")
    
    print("\n🔧 命令行工具:")
    print("  ✅ programming_prompt_templates.py - 模板管理")
    print("  ✅ prompt_advisor.py - 智能分析")
    print("  ✅ quick_setup.py - 快速配置")
    print("  ✅ test_integration.py - 功能测试")
    
    print("\n🛡️ 安全功能:")
    print("  ✅ secure_api_manager.py - 加密API密钥管理")
    print("  ✅ security_scanner.py - 安全扫描")
    print("  ✅ Git钩子 - 防止敏感信息泄露")
    
    print("\n🚀 启动Web应用:")
    print("  streamlit run streamlit_app.py")
    print("  然后访问: http://localhost:8501")

def main():
    """主演示函数"""
    print("🎉 AI提示工程师 2.0 - 功能演示")
    print("=" * 60)
    print("专为AI编程工具优化的智能提示词生成器")
    print("=" * 60)
    
    try:
        # 演示编程模板
        demo_programming_templates()
        
        # 演示智能建议器
        demo_prompt_advisor()
        
        # 演示集成功能
        demo_integration()
        
        print("\n" + "=" * 60)
        print("🎊 演示完成！")
        print("💡 提示：运行 'streamlit run streamlit_app.py' 体验完整功能")
        print("📚 查看 README.md 了解详细使用说明")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        print("请确保所有依赖已正确安装")

if __name__ == "__main__":
    main() 