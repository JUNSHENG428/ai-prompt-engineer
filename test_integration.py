#!/usr/bin/env python3
"""
集成测试脚本
测试编程模板和智能建议器的功能
"""

import sys
import traceback

def test_programming_templates():
    """测试编程模板功能"""
    print("🧑‍💻 测试编程模板功能...")
    
    try:
        from programming_prompt_templates import get_programming_templates, list_task_types, list_ai_tools
        
        # 初始化模板管理器
        templates = get_programming_templates()
        print(f"✅ 成功加载 {len(templates.list_all_templates())} 个模板")
        
        # 测试任务类型列表
        task_types = list_task_types()
        print(f"✅ 支持 {len(task_types)} 种任务类型: {', '.join(task_types[:3])}...")
        
        # 测试AI工具列表
        ai_tools = list_ai_tools()
        print(f"✅ 支持 {len(ai_tools)} 种AI工具: {', '.join(ai_tools[:3])}...")
        
        # 测试模板生成
        template_id = "function_generation"
        test_vars = {
            "language": "Python",
            "function_description": "计算两个数的最大公约数",
            "input_parameters": "a (int), b (int)",
            "return_value": "int - 最大公约数",
            "constraints": "输入必须为正整数"
        }
        
        prompt = templates.generate_prompt(template_id, **test_vars)
        print(f"✅ 成功生成模板Prompt (长度: {len(prompt)} 字符)")
        
        return True
        
    except Exception as e:
        print(f"❌ 编程模板测试失败: {e}")
        traceback.print_exc()
        return False

def test_prompt_advisor():
    """测试智能建议器功能"""
    print("\n🤖 测试智能建议器功能...")
    
    try:
        from prompt_advisor import PromptAdvisor
        
        # 初始化建议器
        advisor = PromptAdvisor()
        print("✅ 成功初始化智能建议器")
        
        # 测试需求分析
        test_input = "我想用Python创建一个函数来处理CSV文件数据"
        result = advisor.analyze_and_recommend(test_input)
        
        analysis = result["analysis"]
        print(f"✅ 需求分析完成:")
        print(f"   - 任务类型: {analysis['task_type']} (置信度: {analysis['confidence']:.2f})")
        print(f"   - 编程语言: {analysis['language']}")
        print(f"   - AI工具: {analysis['ai_tool']}")
        print(f"   - 复杂度: {analysis['complexity']}")
        
        recommendations = result["recommendations"]
        print(f"✅ 获得 {len(recommendations)} 个模板推荐")
        
        if recommendations:
            best_rec = recommendations[0]
            print(f"   - 最佳推荐: {best_rec['template_name']} (相关性: {best_rec['relevance_score']:.2f})")
        
        tips = result["tips"]
        print(f"✅ 获得 {len(tips)} 条使用建议")
        
        return True
        
    except Exception as e:
        print(f"❌ 智能建议器测试失败: {e}")
        traceback.print_exc()
        return False

def test_streamlit_integration():
    """测试Streamlit集成"""
    print("\n📱 测试Streamlit集成...")
    
    try:
        # 检查核心模块导入
        from programming_prompt_templates import get_programming_templates
        from prompt_advisor import PromptAdvisor
        
        print("✅ 核心模块导入成功")
        
        # 测试模板管理器初始化
        templates = get_programming_templates()
        print(f"✅ 模板管理器初始化成功 ({len(templates.list_all_templates())} 个模板)")
        
        # 测试建议器初始化
        advisor = PromptAdvisor()
        print("✅ 智能建议器初始化成功")
        
        # 尝试导入Streamlit（可选）
        try:
            import streamlit as st
            print("✅ Streamlit模块可用")
        except ImportError:
            print("⚠️ Streamlit模块未安装（这不影响核心功能）")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始集成测试...")
    print("=" * 50)
    
    tests = [
        test_programming_templates,
        test_prompt_advisor,
        test_streamlit_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！新功能集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 