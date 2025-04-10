from typing import Dict, List, Any
import pandas as pd
import random

from src.axis_augmentation.base_augmenter import BaseAxisAugmenter
from src.utils.constants import FewShotConstants


class FewShotAugmenter(BaseAxisAugmenter):
    """
    This augmenter handles few-shot examples for question answering tasks.
    It selects examples from a dataset to provide context for each question.
    """

    def __init__(self, num_examples: int = 1, n_augments: int = 3):
        """
        Initialize the few-shot augmenter.
        
        Args:
            num_examples: Number of examples to include for each question
            n_augments: Number of variations to generate (used for consistency with other augmenters)
        """
        super().__init__(n_augments=n_augments)
        self.num_examples = num_examples
        self.dataset = None

    def get_name(self):
        return "Few-Shot Examples"

    def set_dataset(self, dataset: pd.DataFrame):
        """
        Set the dataset to use for few-shot examples.
        
        Args:
            dataset: DataFrame with 'input' and 'output' columns
        """
        if "input" not in dataset.columns or "output" not in dataset.columns:
            raise ValueError("Dataset must contain columns - 'input', 'output'")
        self.dataset = dataset

    def augment(self, prompt: str, identification_data: Dict[str, Any] = None) -> List[str]:
        """
        Generate few-shot variations of the prompt.
        
        Args:
            prompt: The original prompt text
            identification_data: Optional data containing a dataset to use
            
        Returns:
            List of variations with few-shot examples
        """
        # If no dataset is provided, try to use identification_data or return original prompt
        dataset = self.dataset
        if dataset is None and identification_data and "dataset" in identification_data:
            dataset = identification_data["dataset"]
        
        if dataset is None:
            return [prompt]
        
        variations = []
        used_variations = set()
        attempts = 0
        # We'll allow more attempts than n_augments, in case we get duplicates
        while len(variations) < self.n_augments and attempts < self.n_augments * 2:
            # Get random examples for this variation
            # We pass None for random_state so each sample can differ
            examples = self._get_examples_for_question(prompt, dataset, random_state=None)
            formatted = self.format_examples(examples)
            # Only add if it's new
            if formatted not in used_variations:
                variations.append(formatted)
                used_variations.add(formatted)
            attempts += 1
        
        return variations[:self.n_augments]

    def augment_all_questions(self, df) -> Dict[str, List[str]]:
        """
        Process all questions in the dataframe and return few-shot examples for each.
        
        Args:
            df: DataFrame with 'input' and 'output' columns
            
        Returns:
            Dictionary where keys are input questions and values are lists of
            few-shot example strings
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

    def _get_examples_for_question(self, question: str, df, random_state=None) -> List[str]:
        """
        Get few-shot examples for a specific question, but now skipping the question itself.
        """
        result = []
        temp_df = df.copy()

        # Filter out the current question
        temp_df = temp_df[temp_df["input"] != question]

        if len(temp_df) == 0:
            return []

        # Only change the sampling logic:
        num_examples = min(self.num_examples, len(temp_df))
        temp_df = temp_df.sample(
            n=num_examples,
            random_state=random_state,
            replace=False  # ensure no sampling with replacement
        )

        # Use these examples as before
        for i in range(num_examples):
            example_input = temp_df.iloc[i]["input"]
            example_output = temp_df.iloc[i]["output"]
            result.append(FewShotConstants.EXAMPLE_FORMAT.format(example_input, example_output))

        return result

    def format_examples(self, examples: List[str]) -> str:
        """
        Format the few-shot examples into a string.
        
        Args:
            examples: list of formatted example strings
            
        Returns:
            formatted string of examples
        """
        return FewShotConstants.EXAMPLE_SEPARATOR.join(examples)

    def create_few_shot_prompt(self, test_question: str, example_pairs: List[tuple]) -> str:
        """
        Create a few-shot prompt with provided examples and a test question.
        
        Args:
            test_question: The question to answer (will be placed at the end)
            example_pairs: List of (question, answer) tuples to use as examples
            
        Returns:
            A formatted few-shot prompt string
        """
        examples = []
        
        # Add the provided examples
        for question, answer in example_pairs:
            examples.append(FewShotConstants.EXAMPLE_FORMAT.format(question, answer))
        
        # Add the test question
        examples.append(FewShotConstants.QUESTION_FORMAT.format(test_question))
        
        # Format and return the prompt
        return self.format_examples(examples)

    def augment_with_examples(self, test_question: str, example_pool: List[tuple]) -> List[str]:
        """
        Create multiple few-shot prompt variations by sampling different examples
        and varying their order.
        
        Args:
            test_question: The question to answer (will be placed at the end)
            example_pool: List of (question, answer) tuples to sample from
            
        Returns:
            List of formatted few-shot prompt variations
        """
        if len(example_pool) < self.num_examples:
            # Not enough examples to sample from
            return [self.create_few_shot_prompt(test_question, example_pool)]
        
        variations = []
        
        # Create n_augments variations
        for _ in range(self.n_augments):
            # Sample examples
            sampled_examples = random.sample(example_pool, min(self.num_examples, len(example_pool)))
            
            # Optionally shuffle the order (50% chance)
            if random.random() > 0.5:
                random.shuffle(sampled_examples)
            
            # Create the prompt
            prompt = self.create_few_shot_prompt(test_question, sampled_examples)
            variations.append(prompt)
        
        # Remove duplicates while preserving order
        unique_variations = []
        for var in variations:
            if var not in unique_variations:
                unique_variations.append(var)
        
        return unique_variations


if __name__ == "__main__":
    # Load sample data
    print("Creating sample data...")
    sample_data = pd.DataFrame({
        "input": [
            "What is the capital of France?",
            "What is the largest planet in our solar system?",
            "Who wrote Romeo and Juliet?",
            "What is the boiling point of water?",
            "What is the chemical symbol for gold?"
        ],
        "output": [
            "Paris",
            "Jupiter",
            "William Shakespeare",
            "100 degrees Celsius",
            "Au"
        ]
    })
    print(f"Created sample data with {len(sample_data)} examples")

    # Create augmenter and generate examples
    augmenter = FewShotAugmenter(num_examples=2, n_augments=3)
    augmenter.set_dataset(sample_data)
    
    # Test the augment method
    test_question = "What is the tallest mountain in the world?"
    variations = augmenter.augment(test_question)
    
    print(f"\nOriginal question: {test_question}")
    print(f"\nGenerated {len(variations)} variations:")
    for i, variation in enumerate(variations):
        print(f"\nVariation {i+1}:")
        print(variation)
    
    # Test augment with identification_data
    print("\n\nTesting augment with identification_data:")
    # Create a new augmenter without setting dataset
    id_augmenter = FewShotAugmenter(num_examples=2, n_augments=2)
    
    # Create identification_data with dataset
    identification_data = {
        "dataset": pd.DataFrame({
            "input": [
                "What is the deepest ocean?",
                "Who discovered electricity?",
                "What is the smallest planet?",
                "What is the capital of Japan?"
            ],
            "output": [
                "Pacific Ocean (Mariana Trench)",
                "Benjamin Franklin",
                "Mercury",
                "Tokyo"
            ]
        })
    }
    
    # Test augment with identification_data
    test_q = "What is the speed of sound?"
    id_variations = id_augmenter.augment(test_q, identification_data)
    
    print(f"Original question: {test_q}")
    print(f"Generated {len(id_variations)} variations using identification_data:")
    for i, variation in enumerate(id_variations):
        print(f"\nVariation {i+1}:")
        print(variation)
    
    # Test augment_all_questions
    all_examples = augmenter.augment_all_questions(sample_data)
    
    print("\n\nFew-shot examples for all questions:")
    for question, examples in all_examples.items():
        print(f"\nQuestion: {question}")
        print("Few-shot format:")
        print(augmenter.format_examples(examples))
        print("-" * 50)

    # Test create_few_shot_prompt
    print("\n\nTesting create_few_shot_prompt:")
    example_pairs = [
        ("What is the capital of Italy?", "Rome"),
        ("What is the largest ocean?", "Pacific Ocean"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci")
    ]
    test_q = "What is the speed of light?"

    few_shot_prompt = augmenter.create_few_shot_prompt(test_q, example_pairs)
    print(few_shot_prompt)

    # Test augment_with_examples
    print("\n\nTesting augment_with_examples:")
    example_pool = [
        ("What is the capital of Italy?", "Rome"),
        ("What is the largest ocean?", "Pacific Ocean"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
        ("What is the chemical symbol for water?", "H2O"),
        ("What is the tallest building in the world?", "Burj Khalifa"),
        ("Who wrote 'Pride and Prejudice'?", "Jane Austen")
    ]
    test_q = "What is the speed of light?"

    # Create an augmenter with 2 examples per prompt and 3 variations
    sampling_augmenter = FewShotAugmenter(num_examples=2, n_augments=3)
    few_shot_variations = sampling_augmenter.augment_with_examples(test_q, example_pool)

    print(f"Generated {len(few_shot_variations)} variations:")
    for i, variation in enumerate(few_shot_variations):
        print(f"\nVariation {i+1}:")
        print(variation)
        print("-" * 50)
