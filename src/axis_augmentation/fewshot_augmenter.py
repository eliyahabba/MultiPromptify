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

    def augment_all_questions(self, df) -> Dict[str, List[str]]:
        """
        Process all questions in the dataframe and return few-shot examples for each.
        :param df: DataFrame with 'input' and 'output' columns
        :return: Dictionary where keys are input questions and values are lists of
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

    def _get_examples_for_question(self, question: str, df) -> List[str]:
        """
        Get few-shot examples for a specific question.
        :param question: the input question to find examples for
        :param df: DataFrame containing all examples
        :return: a list of formatted example strings
        """
        result = []
        temp_df = df.copy()

        # Filter out current question
        temp_df = temp_df[temp_df["input"] != question]

        if len(temp_df) == 0:
            return [f"Input: {question}\nOutput:"]

        num_examples = min(self.num_examples, len(temp_df))
        temp_df = temp_df.sample(n=num_examples, random_state=42)

        # Add examples to the result list as formatted strings
        for i in range(num_examples):
            example_input = temp_df.iloc[i]["input"]
            example_output = temp_df.iloc[i]["output"]
            result.append(f"Input: {example_input}\nOutput: {example_output}")

        # Add the question as the last item
        result.append(f"Input: {question}\nOutput:")

        return result

    def format_examples(self, examples: List[str]) -> str:
        """
        Format the few-shot examples into a string.
        :param examples: list of formatted example strings
        :return: formatted string of examples
        """
        return "\n\n".join(examples)


if __name__ == "__main__":
    # Load data from Hugging Face
    print("Loading data from Hugging Face...")
    dataset = load_dataset("squad_v2", split="validation[:20]")

    # Convert to input/output format
    hf_data = {
        "input": [item["question"] for item in dataset],
        "output": [
            (
                item["answers"]["text"][0]
                if item["answers"]["text"]
                else "No answer available"
            )
            for item in dataset
        ],
    }
    df = pd.DataFrame(hf_data)
    print(f"Loaded {len(df)} examples")

    # Create augmenter and generate examples
    augmenter = FewShotAugmenter(num_examples=2)
    all_examples = augmenter.augment_all_questions(df)

    # Show a sample of augmented data
    sample_question = list(all_examples.keys())[0]
    print(f"\nQuestion: {sample_question}")
    print("\nFew-shot examples:")
    for example in all_examples[sample_question]:
        print(example)

    # Show formatted example
    print("\nFormatted example:")
    print(augmenter.format_examples(all_examples[sample_question]))
