import random
from typing import Dict, List

import pandas as pd
from datasets import load_dataset

from base_augmenter import BaseAxisAugmenter


class FewShotAugmenter(BaseAxisAugmenter):
    """
    This augmenter handles few-shot examples for question answering tasks.
    It selects examples from a dataset to provide context for each question.
    """

    def __init__(self, num_examples: int = 1):
        """
        Initialize the few-shot augmenter.
        :param num_examples: number of examples to include for each question
        """
        self.num_examples = num_examples

    def augment_all_questions(self, df) -> Dict[str, List[List[str]]]:
        """
        Process all questions in the dataframe and return few-shot examples for each.
        :param df: DataFrame with 'input' and 'output' columns
        :return: Dictionary where keys are input questions and values are lists of
                few-shot examples (each as [input, output])
        """
        if "input" not in df.columns or "output" not in df.columns:
            raise ValueError("Dataframe must contain columns - 'input', 'output'")
            
        result = {}
        
        # Process each question in the dataframe
        for _, row in df.iterrows():
            question = row["input"]
            examples = self._get_examples_for_question(question, df)
            result[question] = examples
            
        return result
    
    def _get_examples_for_question(self, question: str, df) -> List[List[str]]:
        """
        Get few-shot examples for a specific question.
        :param question: the input question to find examples for
        :param df: DataFrame containing all examples
        :return: a list of examples in [input, output] format
        """
        result = []
        temp_df = df.copy()
        
        # Filter out current question
        temp_df = temp_df[temp_df["input"] != question]
        
        if len(temp_df) == 0:
            return [[question, ""]]
            
        num_examples = min(self.num_examples, len(temp_df))
        temp_df = temp_df.sample(n=num_examples, random_state=42)
        
        # Add examples to the result list
        for i in range(num_examples):
            example_input = temp_df.iloc[i]["input"]
            example_output = temp_df.iloc[i]["output"]
            result.append([example_input, example_output])
            
        # Add the question as the last item
        result.append([question, ""])
        
        return result

    def format_examples(self, examples: List[List[str]], format_type: str = "simple") -> str:
        """
        Format the few-shot examples into a string.
        :param examples: list of examples in [input, output] format
        :param format_type: the format to use ('simple', 'numbered', or 'markdown')
        :return: formatted string of examples
        """
        if format_type == "simple":
            formatted = ""
            for i, example in enumerate(examples):
                if i < len(examples) - 1:  # Not the last example (which is the question)
                    formatted += f"Input: {example[0]}\nOutput: {example[1]}\n\n"
                else:
                    formatted += f"Input: {example[0]}\nOutput:"
            return formatted
        
        elif format_type == "numbered":
            formatted = ""
            for i, example in enumerate(examples):
                if i < len(examples) - 1:  # Not the last example
                    formatted += f"Example {i+1}:\nInput: {example[0]}\nOutput: {example[1]}\n\n"
                else:
                    formatted += f"Question:\nInput: {example[0]}\nOutput:"
            return formatted
            
        elif format_type == "markdown":
            formatted = ""
            for i, example in enumerate(examples):
                if i < len(examples) - 1:  # Not the last example
                    formatted += f"### Example {i+1}\n**Input:** {example[0]}\n**Output:** {example[1]}\n\n"
                else:
                    formatted += f"### Your Task\n**Input:** {example[0]}\n**Output:**"
            return formatted
        
        else:
            raise ValueError(f"Invalid format_type: {format_type}. Choose from: ['simple', 'numbered', 'markdown']")


if __name__ == "__main__":  # Example usage
    # Option 1: Create a sample dataframe
    data = {
        "input": [
            "What is the capital of France?",
            "What is the capital of Germany?",
            "What is the capital of Italy?",
            "What is the capital of Spain?",
            "What is the capital of Japan?",
        ],
        "output": [
            "The capital of France is Paris.",
            "The capital of Germany is Berlin.",
            "The capital of Italy is Rome.",
            "The capital of Spain is Madrid.",
            "The capital of Japan is Tokyo.",
        ],
    }
    df = pd.DataFrame(data)
    
    # Option 2: Load from Hugging Face dataset
    try:
        # Load a QA dataset (here using squad_v2 as an example)
        dataset = load_dataset("squad_v2", split="validation[:10]")
        
        # Convert to the required format with input and output columns
        hf_data = {
            "input": [item["question"] for item in dataset],
            "output": [item["answers"]["text"][0] if item["answers"]["text"] else "No answer available" 
                      for item in dataset]
        }
        hf_df = pd.DataFrame(hf_data)
        
        print(f"Loaded {len(hf_df)} examples from Hugging Face dataset")
        # Use HF dataset for examples
        df = hf_df
    except Exception as e:
        print(f"Could not load HF dataset: {e}")
        print("Using sample dataframe instead")
    
    # Create an instance of FewShotAugmenter
    augmenter = FewShotAugmenter(num_examples=2)
    
    # Generate few-shot examples for all questions
    all_examples = augmenter.augment_all_questions(df)
    
    # Print a sample result and show formatted examples
    print("\nFew-shot examples for a sample question:")
    print("-" * 50)
    
    sample_question = list(all_examples.keys())[0]
    examples = all_examples[sample_question]
    
    print(f"Examples for: {sample_question}")
    for example in examples:
        print(example)
    
    print("\nFormatted examples (simple):")
    print("-" * 50)
    print(augmenter.format_examples(examples, "simple"))
    
    print("\nFormatted examples (markdown):")
    print("-" * 50)
    print(augmenter.format_examples(examples, "markdown"))
    
    print(f"\nTotal questions processed: {len(all_examples)}")
