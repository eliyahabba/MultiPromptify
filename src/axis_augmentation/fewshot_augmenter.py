from typing import Dict, List

import pandas as pd
from base_augmenter import BaseAxisAugmenter


class FewShotAugmenter(BaseAxisAugmenter):
    """
    Augmenter that handles few-shot examples for all questions in a dataframe.
    Controls the number and order of examples for each question.
    """

    def __init__(self, num_examples: int = 1):
        self.num_examples = num_examples

    def augment_all_questions(self, df) -> Dict[str, List[List[str]]]:
        """
        Process all questions in the dataframe and return few-shot examples for each.

        Args:
            df: DataFrame with 'input' and 'output' columns

        Returns:
            Dictionary where keys are input questions and values are lists of
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
        """Get few-shot examples for a specific question"""
        result = []
        temp_df = df.copy()

        # Filter out curr question
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
        # TODO: Check format
        result.append([question, ""])
        return result
