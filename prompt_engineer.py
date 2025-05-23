import argparse
import json
import os
import requests
from typing import Dict, Any, List, Optional
import logging
import sys

# 导入API密钥管理模块
try:
    from api_secrets import get_api_key, prompt_for_api_key
except ImportError:
    print("警告: 未找到API密钥管理模块 (api_secrets.py)，将使用基本方法获取API密钥")
    get_api_key = lambda provider: os.environ.get(f"{provider.upper()}_API_KEY")
    prompt_for_api_key = lambda provider: None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class PromptEngineer:
    """
    A simplified Prompt Engineer that generates well-formatted, detailed prompts
    based on user requirements by leveraging language model APIs.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-3.5-turbo", 
                 api_provider: str = "openai"):
        """
        Initialize the Prompt Engineer.
        
        Args:
            api_key: API key for the language model service
            model_name: Name of the model to use
            api_provider: Provider of the API service ('openai' or 'deepseek')
        """
        # 如果未传入API密钥，尝试自动获取
        if not api_key:
            api_key = get_api_key(api_provider)
            
            # 如果仍然未找到，提示用户输入
            if not api_key:
                api_key = prompt_for_api_key(api_provider)
                
        self.api_key = api_key
        self.model_name = model_name
        self.api_provider = api_provider.lower()
        
        # Set the appropriate base URL based on the provider
        if self.api_provider == "openai":
            self.base_url = "https://api.openai.com/v1/chat/completions"
        elif self.api_provider == "deepseek":
            self.base_url = "https://api.deepseek.com/v1/chat/completions"
        elif self.api_provider == "claude":
            self.base_url = "https://api.anthropic.com/v1/messages"
        else:
            raise ValueError(f"Unsupported API provider: {api_provider}. Use 'openai', 'deepseek', or 'claude'.")
        
        if not self.api_key:
            logger.warning("No API key provided. Using mock responses for demonstration.")
    
    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Call the language model API with the provided messages.
        
        Args:
            messages: List of message dictionaries in the format expected by the API
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response
        """
        if not self.api_key:
            # Mock response for demonstration when no API key is available
            return self._generate_mock_response(messages[-1]["content"])

        system_prompt_content = None
        processed_messages = []

        # Separate system prompt for Claude, keep messages for others
        if self.api_provider == "claude":
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt_content = msg["content"]
                else:
                    processed_messages.append(msg)
        else:
            processed_messages = messages

        if self.api_provider == "claude":
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model_name,
                "messages": processed_messages, # Should only contain user/assistant messages
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if system_prompt_content:
                data["system"] = system_prompt_content
        else: # OpenAI and Deepseek
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model_name,
                "messages": processed_messages, # Contains system prompt for these providers
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Extract content based on API provider's response format
            if self.api_provider == "openai" or self.api_provider == "deepseek":
                return result["choices"][0]["message"]["content"]
            elif self.api_provider == "claude":
                # Claude's response structure
                if result.get("content") and isinstance(result["content"], list) and len(result["content"]) > 0:
                    return result["content"][0]["text"]
                else:
                    logger.error(f"Unexpected Claude API response format: {result}")
                    return "Error: Could not parse Claude API response."
            
        except Exception as e:
            logger.error(f"API call failed: {e}. Response: {response.text if 'response' in locals() else 'No response object'}")
            # Fall back to mock response in case of error
            return self._generate_mock_response(messages[-1]["content"])
    
    def _generate_mock_response(self, user_requirement: str) -> str:
        """Generate a mock response for demonstration purposes."""
        return f"""# Expert Prompt Format

## Task Description
I need to create content that addresses the following requirement:
{user_requirement}

## Output Format
The response should be:
- Well-structured with clear headings and sections
- Comprehensive in covering all aspects of the topic
- Written in a professional but accessible tone
- Include examples where appropriate

## Specific Requirements
- Begin with a concise overview of the topic
- Explore the main concepts in detail
- Address potential challenges or controversies
- Conclude with practical implications or applications

## Additional Context
This content will be used for educational purposes, so accuracy and clarity are essential."""
    
    def generate_formatted_prompt(self, requirement: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a well-formatted prompt based on user requirements.
        
        Args:
            requirement: The user's requirement
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            A detailed, formatted prompt
        """
        # Define the system prompt that describes the task
        system_prompt = """You are an expert prompt engineer. Your task is to create detailed, 
well-formatted prompts that help language models produce high-quality outputs.

When given a user requirement, generate a detailed prompt that:
1. Clearly structures the expected output with sections and formatting
2. Provides specific instructions about style, tone, and depth
3. Includes any necessary context or constraints
4. Anticipates potential misunderstandings and clarifies them

Your prompts should be comprehensive yet concise, and formatted in a way that makes them easy to read and follow."""
        
        # Define the user prompt that includes the requirement
        user_prompt = f"""Please create a detailed, well-formatted prompt based on the following requirement:

USER REQUIREMENT: {requirement}

The prompt should help a language model understand exactly what kind of response is needed,
including format, style, depth, and any other relevant details."""
        
        # Create the messages list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API and return the response
        return self._call_api(messages, temperature, max_tokens)
    
    def generate_expert_panel_prompt(self, requirement: str, num_experts: int = 3, 
                                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a prompt that simulates a panel of experts discussing a topic.
        
        Args:
            requirement: The user's requirement
            num_experts: Number of experts to include in the panel
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            A detailed prompt with expert panel format
        """
        # Define the system prompt for expert panel simulation
        system_prompt = f"""You are an expert prompt engineer specializing in creating 'expert panel' prompts.
These prompts simulate {num_experts} experts with different perspectives discussing a topic in depth.

When designing an expert panel prompt, you should:
1. Create {num_experts} distinct expert personas with relevant backgrounds
2. Structure the discussion as a step-by-step exploration of the topic
3. Have experts build on each other's insights and occasionally disagree
4. Conclude with practical takeaways or a synthesis of the discussion"""
        
        # Define the user prompt that includes the requirement
        user_prompt = f"""Please create a detailed 'expert panel' prompt based on the following requirement:

USER REQUIREMENT: {requirement}

The prompt should simulate {num_experts} experts discussing this topic in depth, following a structured format:
- Introduction of the experts and the topic
- Step-by-step exploration of the main aspects
- Discussion of pros, cons, and nuances
- Conclusion with practical takeaways

Make sure each expert has a distinct perspective and expertise relevant to the topic."""
        
        # Create the messages list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API and return the response
        return self._call_api(messages, temperature, max_tokens)
    
    def generate_prompt_with_examples(self, requirement: str, examples: List[Dict[str, str]], 
                                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a prompt that includes examples for few-shot learning.
        
        Args:
            requirement: The user's requirement
            examples: List of example dictionaries with 'input' and 'output' keys
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            A detailed prompt with examples
        """
        # Format the examples
        examples_text = "# Examples for reference:\n"
        for i, example in enumerate(examples):
            examples_text += f"\nExample {i+1}:\nInput: {example['input']}\nOutput: {example['output']}\n"
        
        # Define the system prompt
        system_prompt = """You are an expert prompt engineer specializing in few-shot learning prompts.
Your task is to create prompts that include examples to help language models understand patterns."""
        
        # Define the user prompt that includes the requirement and examples
        user_prompt = f"""Please create a detailed prompt based on the following requirement and examples:

USER REQUIREMENT: {requirement}

{examples_text}

The prompt should:
1. Use the examples to illustrate the expected pattern or format
2. Provide clear instructions on how to apply this pattern to new inputs
3. Include any additional context or constraints that would help"""
        
        # Create the messages list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call the API and return the response
        return self._call_api(messages, temperature, max_tokens)


def main():
    """Main function to demonstrate the Prompt Engineer."""
    parser = argparse.ArgumentParser(description='AI Prompt Engineer')
    parser.add_argument('requirement', type=str, nargs='?', help='User requirement for generating a prompt')
    parser.add_argument('--format', type=str, choices=['standard', 'expert-panel', 'examples'], 
                        default='standard', help='Format of the prompt to generate')
    parser.add_argument('--examples', type=str, help='Path to JSON file with examples for few-shot learning')
    parser.add_argument('--api-key', type=str, help='API key for the language model service')
    parser.add_argument('--model', type=str, default='deepseek-chat', 
                        help='Model name to use (e.g., gpt-3.5-turbo, deepseek-chat, claude-3-opus-20240229)')
    parser.add_argument('--api-provider', type=str, choices=['openai', 'deepseek', 'claude'], 
                       default='deepseek', help='API provider to use (openai, deepseek, or claude)')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature (0.0-1.0) for generation')
    parser.add_argument('--max-tokens', type=int, default=1000, help='Maximum tokens to generate')
    args = parser.parse_args()
    
    # Initialize the Prompt Engineer
    prompt_engineer = PromptEngineer(
        api_key=args.api_key, 
        model_name=args.model,
        api_provider=args.api_provider
    )
    
    if args.requirement:
        # Generate the prompt based on the specified format
        if args.format == 'standard':
            prompt = prompt_engineer.generate_formatted_prompt(
                args.requirement, 
                temperature=args.temperature, 
                max_tokens=args.max_tokens
            )
        elif args.format == 'expert-panel':
            prompt = prompt_engineer.generate_expert_panel_prompt(
                args.requirement, 
                temperature=args.temperature, 
                max_tokens=args.max_tokens
            )
        elif args.format == 'examples':
            # Load examples from JSON file if provided
            examples = []
            if args.examples:
                try:
                    with open(args.examples, 'r', encoding="utf-8") as f:
                        examples = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load examples: {e}")
                    examples = [
                        {"input": "Write a poem about nature", "output": "The trees sway gently..."},
                        {"input": "Explain quantum physics", "output": "Quantum physics studies..."}
                    ]
            else:
                # Default examples if no file is provided
                examples = [
                    {"input": "Write a poem about nature", "output": "The trees sway gently..."},
                    {"input": "Explain quantum physics", "output": "Quantum physics studies..."}
                ]
            prompt = prompt_engineer.generate_prompt_with_examples(
                args.requirement, 
                examples, 
                temperature=args.temperature, 
                max_tokens=args.max_tokens
            )
        
        print("\n=== Generated Prompt ===\n")
        print(prompt)
    else:
        print("Please provide a requirement to generate a prompt.")
        parser.print_help()


if __name__ == "__main__":
    main() 