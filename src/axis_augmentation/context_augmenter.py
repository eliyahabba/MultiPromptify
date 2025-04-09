import random
from typing import List, Dict, Any
import requests
import json

from src.axis_augmentation.base_augmenter import BaseAxisAugmenter


class ContextAugmenter(BaseAxisAugmenter):
    """
    Augmenter that adds irrelevant context before or after the main prompt.
    This doesn't change the meaning of the task but makes the prompt longer.
    """

    def __init__(self, n_augments=3, api_key=None):
        """
        Initialize the context augmenter.

        Args:
            n_augments: Number of variations to generate
            api_key: API key for the language model service (if needed)
        """
        super().__init__(n_augments=n_augments)
        self.api_key = api_key
        
    def get_name(self):
        return "Context Variations"

    def augment(self, prompt: str, identification_data: Dict[str, Any] = None) -> List[str]:
        """
        Generate variations of the prompt by adding irrelevant context.

        Args:
            prompt: The original prompt text
            identification_data: Data from the identifier (not used in this augmenter)

        Returns:
            List of variations with added context
        """
        variations = [prompt]  # Start with the original prompt
        
        # Generate n_augments-1 variations (since we already have the original)
        for _ in range(self.n_augments - 1):
            # Randomly decide whether to add context before, after, or both
            variation_type = random.choice(["before", "after", "both"])
            
            # Generate the variation
            new_variation = self._generate_variation(prompt, variation_type)
            if new_variation and new_variation != prompt:
                variations.append(new_variation)
        
        return variations

    def _generate_variation(self, prompt: str, variation_type: str) -> str:
        """
        Generate a single variation by adding context.

        Args:
            prompt: The original prompt
            variation_type: Where to add context ("before", "after", or "both")

        Returns:
            A new variation of the prompt
        """
        # Create a meta-prompt to ask the language model to add irrelevant context
        meta_prompt = self._create_meta_prompt(prompt, variation_type)
        
        # Call language model to generate the variation
        try:
            result = self._call_language_model(meta_prompt)
            # Check if the result is valid (not empty and not the same as the original prompt and the original prompt is in the result)
            if result and result != prompt and prompt in result:
                return result
            else:
                return prompt
        except Exception as e:
            return prompt

    def _create_meta_prompt(self, prompt: str, variation_type: str) -> str:
        """
        Create a meta-prompt to ask the language model to add context.

        Args:
            prompt: The original prompt
            variation_type: Where to add context

        Returns:
            A meta-prompt for the language model
        """
        if variation_type == "before":
            return f"""
            Your task is to add irrelevant context BEFORE the following prompt.
            The added context should NOT change the meaning or expected answer of the original prompt.
            The context should be coherent but not directly related to the task.
            
            Original prompt:
            "{prompt}"
            
            Return ONLY the modified prompt with added context before it. Do not include any explanations.
            """
        elif variation_type == "after":
            return f"""
            Your task is to add irrelevant context AFTER the following prompt.
            The added context should NOT change the meaning or expected answer of the original prompt.
            The context should be coherent but not directly related to the task.
            
            Original prompt:
            "{prompt}"
            
            Return ONLY the modified prompt with added context after it. Do not include any explanations.
            """
        else:  # both
            return f"""
            Your task is to add irrelevant context BOTH BEFORE AND AFTER the following prompt.
            The added context should NOT change the meaning or expected answer of the original prompt.
            The context should be coherent but not directly related to the task.
            
            Original prompt:
            "{prompt}"
            
            Return ONLY the modified prompt with added context before and after it. Do not include any explanations.
            """

    def _call_language_model(self, meta_prompt: str) -> str:
        """
        Call a language model API to generate the variation.
        
        This is a placeholder - you'll need to implement the actual API call
        based on which language model service you're using.
        
        Args:
            meta_prompt: The prompt to send to the language model
            
        Returns:
            The generated text
        """
        # This is a placeholder implementation
        # Replace with actual API call to your preferred language model
        
        # Example using a hypothetical API:
        # response = requests.post(
        #     "https://api.languagemodel.com/generate",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     json={"prompt": meta_prompt, "max_tokens": 500}
        # )
        # return response.json()["choices"][0]["text"].strip()
        
        # For now, return a simple modification to show the concept
        return meta_prompt  # Replace with actual implementation

