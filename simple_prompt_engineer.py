#!/usr/bin/env python
import json
import os
import sys
from prompt_engineer import PromptEngineer

def load_config():
    """Load configuration from config.json if available"""
    config = {}
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            print(f"配置已从 {config_file} 加载")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    return config

def load_examples(examples_file):
    """Load examples from a JSON file"""
    examples = []
    if examples_file and os.path.exists(examples_file):
        try:
            with open(examples_file, "r", encoding="utf-8") as f:
                examples = json.load(f)
            print(f"已加载 {len(examples)} 个示例")
        except Exception as e:
            print(f"加载示例文件失败: {e}")
            examples = [
                {"input": "写一首关于自然的诗", "output": "树木轻轻摇曳..."},
                {"input": "解释量子物理", "output": "量子物理是研究..."}
            ]
    else:
        examples = [
            {"input": "写一首关于自然的诗", "output": "树木轻轻摇曳..."},
            {"input": "解释量子物理", "output": "量子物理是研究..."}
        ]
    return examples

def main():
    # Load configuration
    config = load_config()
    
    # Get API key from config or environment
    api_key = config.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
    api_provider = config.get("api_provider", "deepseek")
    model = config.get("model", "deepseek-chat")
    
    # Get user input interactively
    print("\n===== 智能提示工程师 =====")
    print("输入 'exit' 或 'quit' 退出程序\n")
    
    while True:
        # Get requirement
        requirement = input("请输入您的需求: ").strip()
        if requirement.lower() in ["exit", "quit", "q"]:
            break
        
        if not requirement:
            print("需求不能为空，请重新输入。")
            continue
        
        # Get format
        format_options = {
            "1": "standard",
            "2": "expert-panel",
            "3": "examples"
        }
        print("\n选择提示格式:")
        print("1. 标准")
        print("2. 专家讨论")
        print("3. 带示例")
        
        format_choice = input("请输入选择 (1/2/3) [默认: 1]: ").strip() or "1"
        if format_choice not in format_options:
            format_choice = "1"
            
        prompt_format = format_options[format_choice]
        
        # Check if API key is available
        if not api_key:
            api_key = input("请输入API密钥: ").strip()
            if not api_key:
                print("错误: 没有提供API密钥")
                continue
        
        # Initialize the prompt engineer
        try:
            print(f"\n使用 {api_provider} 的 {model} 模型生成提示...")
            prompt_engineer = PromptEngineer(
                api_key=api_key,
                model_name=model,
                api_provider=api_provider
            )
            
            # Generate prompt based on selected format
            if prompt_format == "standard":
                prompt = prompt_engineer.generate_formatted_prompt(requirement)
            elif prompt_format == "expert-panel":
                prompt = prompt_engineer.generate_expert_panel_prompt(requirement)
            elif prompt_format == "examples":
                examples_file = input("示例文件路径 (留空使用默认示例): ").strip()
                examples = load_examples(examples_file)
                prompt = prompt_engineer.generate_prompt_with_examples(requirement, examples)
            
            # Display the result
            print("\n===== 生成的提示 =====\n")
            print(prompt)
            print("\n" + "=" * 30)
            
            # Ask if user wants to save the result
            save_choice = input("\n是否保存结果? (y/n): ").strip().lower()
            if save_choice == "y":
                file_path = input("保存文件路径 [默认: prompt_output.txt]: ").strip() or "prompt_output.txt"
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(prompt)
                    print(f"结果已保存到 {file_path}")
                except Exception as e:
                    print(f"保存文件失败: {e}")
            
            print("\n" + "-" * 50 + "\n")
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main() 