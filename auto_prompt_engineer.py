import logging
from typing import List, Dict, Tuple, Optional, Any
import argparse
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoPromptEngineer:
    """
    Automatic Prompt Engineer (APE) system that generates optimal prompts
    based on user requirements and example input-output pairs.
    """
    
    def __init__(self, inference_model: Any, scoring_model: Any, resampling_model: Optional[Any] = None):
        """
        Initialize the APE system with the required models.
        
        Args:
            inference_model: Model used to execute tasks based on prompts
            scoring_model: Model used to evaluate prompt effectiveness
            resampling_model: Optional model for generating prompt variations
        """
        self.inference_model = inference_model
        self.scoring_model = scoring_model
        self.resampling_model = resampling_model
        self.demo_pairs = []
        self.best_prompt = None
        self.best_score = float('-inf')
        
    def set_demonstration_pairs(self, demo_pairs: List[Tuple[str, str]]):
        """Set the demonstration pairs for few-shot learning."""
        self.demo_pairs = demo_pairs
        
    def build_prompt(self, candidate_prompt: str, new_input: str) -> str:
        """
        Build a complete prompt by combining demonstration pairs,
        the candidate prompt, and the new input.
        
        Args:
            candidate_prompt: The prompt to be evaluated
            new_input: The input to process
            
        Returns:
            The complete formatted prompt text
        """
        demonstration_text = "# Demonstration Start\n"
        for inp, out in self.demo_pairs:
            demonstration_text += f"Input: {inp} → Output: {out}\n"
        demonstration_text += "# Demonstration End\n\n"
        
        prompt_text = demonstration_text + candidate_prompt + "\nInput: " + new_input
        return prompt_text
    
    def evaluate_prompt(self, candidate_prompt: str, eval_inputs: List[str], 
                        eval_references: List[str]) -> float:
        """
        Evaluate a candidate prompt by testing it on inputs and scoring the results.
        
        Args:
            candidate_prompt: The prompt to evaluate
            eval_inputs: List of test inputs
            eval_references: Corresponding expected outputs
            
        Returns:
            The average score across all test cases
        """
        if len(eval_inputs) != len(eval_references):
            raise ValueError("Number of eval_inputs must match eval_references")
        
        total_score = 0.0
        
        for i, test_input in enumerate(eval_inputs):
            # Build the complete prompt
            prompt_text = self.build_prompt(candidate_prompt, test_input)
            
            # Generate output using the inference model
            generated_output = self.inference_model.generate(prompt_text)
            
            # Score the output against the expected result
            score = self.scoring_model.score(generated_output, reference=eval_references[i])
            total_score += score
            
            logger.debug(f"Prompt: {candidate_prompt}")
            logger.debug(f"Input: {test_input}")
            logger.debug(f"Generated: {generated_output}")
            logger.debug(f"Expected: {eval_references[i]}")
            logger.debug(f"Score: {score}")
        
        avg_score = total_score / len(eval_inputs)
        return avg_score
    
    def generate_prompt_variations(self, base_prompt: str, num_variations: int = 5) -> List[str]:
        """
        Generate variations of a prompt using the resampling model.
        
        Args:
            base_prompt: The base prompt to create variations from
            num_variations: Number of variations to generate
            
        Returns:
            List of prompt variations
        """
        if not self.resampling_model:
            raise ValueError("Resampling model not set.")
        
        variation_instruction = (
            f"Create {num_variations} variations of the following prompt that maintain "
            f"the same semantic meaning but use different wording:\n\n{base_prompt}"
        )
        
        variations_text = self.resampling_model.generate(variation_instruction)
        
        # 简单分行解析，过滤空行，仅返回指定数量
        raw_lines = [line.strip() for line in variations_text.split("\n")]
        variations = [v for v in raw_lines if v]  # 去掉空字符串
        
        return variations[:num_variations]
    
    def find_optimal_prompt(self, candidate_prompts: List[str], eval_inputs: List[str], 
                           eval_references: List[str], iterations: int = 3, 
                           variations_per_iter: int = 3) -> Tuple[str, float]:
        """
        Find the optimal prompt through evaluation and resampling.
        
        Args:
            candidate_prompts: Initial list of candidate prompts
            eval_inputs: Test inputs for evaluation
            eval_references: Expected outputs for test inputs
            iterations: Number of optimization iterations
            variations_per_iter: Number of variations to generate per iteration
            
        Returns:
            The best prompt and its score
        """
        best_prompt = None
        best_score = float('-inf')
        
        # Evaluate initial candidates
        logger.info("Evaluating initial candidates...")
        for prompt in candidate_prompts:
            score = self.evaluate_prompt(prompt, eval_inputs, eval_references)
            logger.info(f"Prompt: '{prompt}' - Score: {score:.4f}")
            
            if score > best_score:
                best_prompt = prompt
                best_score = score
        
        # Iterative improvement through resampling
        if self.resampling_model:
            for i in range(iterations):
                logger.info(f"Optimization Iteration {i+1}/{iterations}")
                
                # Generate variations of the best prompt
                try:
                    variations = self.generate_prompt_variations(best_prompt, variations_per_iter)
                    logger.info(f"Generated {len(variations)} variations")
                    
                    # Evaluate variations
                    for var_prompt in variations:
                        score = self.evaluate_prompt(var_prompt, eval_inputs, eval_references)
                        logger.info(f"Variation: '{var_prompt}' - Score: {score:.4f}")
                        
                        if score > best_score:
                            best_prompt = var_prompt
                            best_score = score
                            logger.info(f"New best prompt found: '{best_prompt}' - Score: {best_score:.4f}")
                
                except Exception as e:
                    logger.error(f"Error in resampling: {e}")
                    break
        
        self.best_prompt = best_prompt
        self.best_score = best_score
        return best_prompt, best_score
    
    def generate_formatted_prompt(self, requirement: str) -> str:
        """
        Generate a formatted prompt based on user requirements.
        
        Args:
            requirement: The user's requirements
            
        Returns:
            A detailed, formatted prompt
        """
        # If we don't have a best prompt from optimization, use a default template
        if not self.best_prompt:
            instruction = (
                f"Based on the following requirement, create a detailed, well-formatted prompt "
                f"that will help a language model generate the desired output:\n\n{requirement}"
            )
            
            return self.inference_model.generate(instruction)
        
        # Otherwise, use our optimized prompt template with the requirement
        return self.best_prompt.replace("{requirement}", requirement)


class DummyModel:
    """A dummy model implementation for demonstration purposes."""
    
    def generate(self, prompt: str) -> str:
        """
        Simulates generating text from a prompt.
        In a real implementation, this would call an actual LLM API.
        """
        print(f"[DUMMY MODEL] Generating from prompt: {prompt[:50]}...")
        return f"This is a generated response for: {prompt[:20]}..."
    
    def score(self, generated: str, reference: str) -> float:
        """
        Simulates scoring a generated output against a reference.
        In a real implementation, this would use actual metrics.
        """
        print(f"[DUMMY MODEL] Scoring: {generated[:20]}... against {reference[:20]}...")
        return random.random()


def main():
    """Main function to demonstrate the APE system."""
    parser = argparse.ArgumentParser(description='Automatic Prompt Engineer')
    parser.add_argument('requirement', type=str, nargs='?', help='User requirement for generating a prompt')
    args = parser.parse_args()
    
    # Initialize models (in a real implementation, these would be actual LLMs)
    inference_model = DummyModel()
    scoring_model = DummyModel()
    resampling_model = DummyModel()
    
    # Initialize the APE system
    ape = AutoPromptEngineer(inference_model, scoring_model, resampling_model)
    
    # Example demonstration pairs
    demo_pairs = [
        ("Create a poem about stars", "Stars shine bright in the night sky..."),
        ("Explain quantum physics", "Quantum physics is the study of matter and energy at the smallest scales...")
    ]
    ape.set_demonstration_pairs(demo_pairs)
    
    if args.requirement:
        # Generate a prompt based on user requirement
        formatted_prompt = ape.generate_formatted_prompt(args.requirement)
        print("\n=== Generated Prompt ===\n")
        print(formatted_prompt)
    else:
        # Demonstrate optimization process with example prompts
        candidate_prompts = [
            "Create a detailed response addressing the following: {requirement}",
            "Please provide a comprehensive answer to: {requirement}",
            "Generate a well-structured response to this query: {requirement}"
        ]
        
        eval_inputs = ["How does climate change affect biodiversity?", "What are the ethical implications of AI?"]
        eval_references = [
            "Climate change affects biodiversity by altering habitats...",
            "The ethical implications of AI include concerns about privacy..."
        ]
        
        best_prompt, best_score = ape.find_optimal_prompt(
            candidate_prompts, eval_inputs, eval_references
        )
        
        print("\n=== Optimization Results ===\n")
        print(f"Best Prompt: {best_prompt}")
        print(f"Score: {best_score:.4f}")
        
        # Example of generating a prompt with the optimized template
        example_req = "Explain how neural networks work"
        formatted_prompt = ape.generate_formatted_prompt(example_req)
        
        print("\n=== Example Generated Prompt ===\n")
        print(formatted_prompt)


if __name__ == "__main__":
    main()
