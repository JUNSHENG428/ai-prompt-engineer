import argparse
import json
import os
import requests
from typing import Dict, Any, List, Optional
import logging
import sys

# 导入API密钥管理模块
try:
    from secure_api_manager import get_api_key
    SECURE_API_AVAILABLE = True
except ImportError:
    try:
        from api_secrets import get_api_key
        SECURE_API_AVAILABLE = False
    except ImportError:
        print("警告: 未找到API密钥管理模块，将使用基本方法获取API密钥")
        get_api_key = lambda provider: os.environ.get(f"{provider.upper()}_API_KEY")
        SECURE_API_AVAILABLE = False

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
                 api_provider: str = "openai", use_mock: bool = False):
        """
        Initialize the Prompt Engineer.
        
        Args:
            api_key: API key for the language model service
            model_name: Name of the model to use
            api_provider: Provider of the API service ('openai' or 'deepseek')
            use_mock: Force use mock responses (for testing/demo)
        """
        self.model_name = model_name
        self.api_provider = api_provider.lower()
        self.use_mock = use_mock
        
        # 如果强制使用模拟模式，直接跳过API密钥获取
        if use_mock:
            self.api_key = None
            logger.info("Using mock mode for demonstration")
        else:
            # 如果未传入API密钥，尝试自动获取
            if not api_key:
                try:
                    api_key = get_api_key(api_provider)
                except Exception as e:
                    logger.debug(f"Failed to get API key: {e}")
                    api_key = None
            
            self.api_key = api_key
                
        # Set the appropriate base URL based on the provider
        if self.api_provider == "openai":
            self.base_url = "https://api.openai.com/v1/chat/completions"
        elif self.api_provider == "deepseek":
            self.base_url = "https://api.deepseek.com/v1/chat/completions"
        else:
            raise ValueError(f"Unsupported API provider: {api_provider}. Use 'openai' or 'deepseek'.")
        
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
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Both OpenAI and Deepseek use similar request formats
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Extract content based on API provider's response format
            if self.api_provider == "openai":
                return result["choices"][0]["message"]["content"]
            elif self.api_provider == "deepseek":
                return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"API call failed: {e}")
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

    def generate_coding_prompt(self, requirement: str, programming_language: str = "Python", 
                              coding_task_type: str = "general", temperature: float = 0.3, 
                              max_tokens: int = 1500) -> str:
        """
        Generate a specialized prompt for coding tasks, optimized for AI programming tools like Cursor.
        
        Args:
            requirement: The coding requirement
            programming_language: Programming language to use
            coding_task_type: Type of coding task (general, debug, refactor, review, test)
            temperature: Controls randomness (lower for coding tasks)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            A detailed coding prompt optimized for AI tools
        """
        # Define task-specific instructions
        task_instructions = {
            "general": "Create clean, well-documented code that follows best practices",
            "debug": "Analyze the code for bugs, provide fixes, and explain the issues",
            "refactor": "Improve code structure, readability, and performance while maintaining functionality",
            "review": "Conduct a thorough code review with suggestions for improvement",
            "test": "Write comprehensive unit tests and explain the testing strategy",
            "optimize": "Optimize code for better performance and efficiency",
            "document": "Add detailed documentation and comments to existing code"
        }
        
        system_prompt = f"""You are an expert software engineer and coding assistant specialized in {programming_language}. 
Your task is to create detailed, actionable coding prompts that help AI programming tools like Cursor, GitHub Copilot, 
and other code assistants generate high-quality code.

When creating coding prompts, ensure they:
1. Specify the exact programming language and version if relevant
2. Include clear requirements and constraints
3. Mention best practices and coding standards
4. Specify the expected output format (function, class, module, etc.)
5. Include error handling and edge case considerations
6. Mention testing requirements when appropriate"""

        user_prompt = f"""Create a detailed coding prompt for the following requirement:

CODING REQUIREMENT: {requirement}
PROGRAMMING LANGUAGE: {programming_language}
TASK TYPE: {coding_task_type}

The prompt should be optimized for AI coding assistants and include:
- Clear, specific instructions
- Expected code structure and organization
- Best practices for {programming_language}
- {task_instructions.get(coding_task_type, "Complete the requested functionality")}
- Error handling considerations
- Code documentation requirements

Make the prompt actionable and specific enough for an AI to generate production-ready code."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_api(messages, temperature, max_tokens)

    def generate_cursor_optimized_prompt(self, requirement: str, context: str = "", 
                                       file_types: List[str] = None, temperature: float = 0.3, 
                                       max_tokens: int = 1500) -> str:
        """
        Generate a prompt specifically optimized for Cursor AI editor.
        
        Args:
            requirement: The development requirement
            context: Additional context about the project
            file_types: List of file types that will be worked with
            temperature: Controls randomness
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            A Cursor-optimized prompt
        """
        if file_types is None:
            file_types = ["Python", "JavaScript", "TypeScript"]
            
        system_prompt = """You are an expert prompt engineer specializing in creating prompts for Cursor AI editor.
Cursor is an AI-powered code editor that can understand project context, generate code, and assist with development tasks.

When creating Cursor-optimized prompts, include:
1. Clear project context and file structure understanding
2. Specific instructions about which files to modify or create
3. Code style and architecture preferences
4. Integration requirements with existing codebase
5. Testing and documentation expectations
6. Step-by-step implementation guidance"""

        context_section = f"PROJECT CONTEXT: {context}" if context else "PROJECT CONTEXT: Not specified"
        file_types_section = f"RELEVANT FILE TYPES: {', '.join(file_types)}"

        user_prompt = f"""Create a Cursor AI editor optimized prompt for the following requirement:

DEVELOPMENT REQUIREMENT: {requirement}
{context_section}
{file_types_section}

The prompt should help Cursor understand:
- What files need to be created or modified
- How the new code integrates with existing project structure
- Specific implementation details and patterns to follow
- Code quality and testing requirements
- Documentation and comments needed

Format the prompt to be clear and actionable for Cursor's AI capabilities."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_api(messages, temperature, max_tokens)

    def generate_architecture_prompt(self, requirement: str, system_type: str = "web_application",
                                   technologies: List[str] = None, temperature: float = 0.5,
                                   max_tokens: int = 2000) -> str:
        """
        Generate a prompt for system architecture and design tasks.
        
        Args:
            requirement: The architecture requirement
            system_type: Type of system (web_application, microservice, mobile_app, etc.)
            technologies: List of preferred technologies
            temperature: Controls randomness
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            An architecture-focused prompt
        """
        if technologies is None:
            technologies = ["React", "Node.js", "PostgreSQL", "Docker"]
            
        system_prompt = """You are a senior software architect and system design expert. 
Your task is to create comprehensive prompts for designing software systems and architectures.

When creating architecture prompts, include:
1. System requirements and constraints
2. Scalability and performance considerations
3. Technology stack recommendations
4. Security and compliance requirements
5. Deployment and infrastructure considerations
6. Monitoring and maintenance strategies"""

        tech_stack_section = f"PREFERRED TECHNOLOGIES: {', '.join(technologies)}"

        user_prompt = f"""Create a comprehensive system architecture prompt for:

ARCHITECTURE REQUIREMENT: {requirement}
SYSTEM TYPE: {system_type}
{tech_stack_section}

The prompt should guide the creation of:
- High-level system architecture diagram
- Component breakdown and responsibilities
- Data flow and API design
- Database schema design
- Security considerations
- Deployment strategy
- Scalability plan
- Monitoring and logging approach

Make the prompt detailed enough for creating production-ready architecture documentation."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call_api(messages, temperature, max_tokens)


def main():
    """Main function to demonstrate the Prompt Engineer."""
    parser = argparse.ArgumentParser(description='AI Prompt Engineer - Enhanced for Programming Tasks')
    parser.add_argument('requirement', type=str, nargs='?', help='User requirement for generating a prompt')
    parser.add_argument('--format', type=str, 
                        choices=['standard', 'expert-panel', 'examples', 'coding', 'cursor', 'architecture'], 
                        default='standard', help='Format of the prompt to generate')
    parser.add_argument('--examples', type=str, help='Path to JSON file with examples for few-shot learning')
    parser.add_argument('--api-key', type=str, help='API key for the language model service')
    parser.add_argument('--model', type=str, default='deepseek-chat', help='Model name to use')
    parser.add_argument('--api-provider', type=str, choices=['openai', 'deepseek'], 
                       default='deepseek', help='API provider to use (openai or deepseek)')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature (0.0-1.0) for generation')
    parser.add_argument('--max-tokens', type=int, default=1000, help='Maximum tokens to generate')
    
    # 新增编程相关参数
    parser.add_argument('--programming-language', type=str, default='Python', 
                       help='Programming language for coding prompts')
    parser.add_argument('--coding-task-type', type=str, 
                       choices=['general', 'debug', 'refactor', 'review', 'test', 'optimize', 'document'],
                       default='general', help='Type of coding task')
    parser.add_argument('--project-context', type=str, default='', 
                       help='Project context for Cursor-optimized prompts')
    parser.add_argument('--file-types', type=str, nargs='*', 
                       default=['Python', 'JavaScript', 'TypeScript'],
                       help='File types for Cursor prompts')
    parser.add_argument('--system-type', type=str, default='web_application',
                       help='System type for architecture prompts')
    parser.add_argument('--technologies', type=str, nargs='*',
                       default=['React', 'Node.js', 'PostgreSQL', 'Docker'],
                       help='Technologies for architecture prompts')
    
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
        elif args.format == 'coding':
            prompt = prompt_engineer.generate_coding_prompt(
                args.requirement,
                programming_language=args.programming_language,
                coding_task_type=args.coding_task_type,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )
        elif args.format == 'cursor':
            prompt = prompt_engineer.generate_cursor_optimized_prompt(
                args.requirement,
                context=args.project_context,
                file_types=args.file_types,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )
        elif args.format == 'architecture':
            prompt = prompt_engineer.generate_architecture_prompt(
                args.requirement,
                system_type=args.system_type,
                technologies=args.technologies,
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