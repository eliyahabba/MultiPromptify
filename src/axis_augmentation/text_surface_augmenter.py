# Non-semantic changes / structural changes (UNI TEXT)
import itertools
import random
import re
from typing import List, Dict, Any

from src.axis_augmentation.base_augmenter import BaseAxisAugmenter
from src.utils.constants import TextSurfaceAugmenterConstants


class TextSurfaceAugmenter(BaseAxisAugmenter):
    """
    Augmenter that creates variations of prompts using non-LLM techniques.
    This includes simple transformations like adding typos, changing capitalization, etc.
    """

    def __init__(self, n_augments=3):
        """
        Initialize the non-LLM augmenter.

        Args:
            n_augments: Number of variations to generate
        """
        super().__init__(n_augments=n_augments)

    def get_name(self):
        return "Non-LLM Variations"

    def augment(self, prompt: str, identification_data: Dict[str, Any] = None) -> List[str]:
        """
        Generate variations of the prompt using non-LLM techniques.

        Args:
            prompt: The original prompt text
            identification_data: Data from the identifier (not used in this augmenter)

        Returns:
            List of variations with non-LLM transformations
        """
        variations = [prompt]  # Start with the original prompt

        # Generate n_augments-1 variations (since we already have the original)
        for _ in range(self.n_augments - 1):
            # Randomly choose a transformation technique
            technique = random.choice(TextSurfaceAugmenterConstants.TRANSFORMATION_TECHNIQUES)

            # Apply the chosen transformation
            new_variation = self._apply_transformation(prompt, technique)
            if new_variation and new_variation != prompt:
                variations.append(new_variation)

        return variations[:self.n_augments]

    def _apply_transformation(self, text: str, technique: str) -> str:
        """
        Apply a specific transformation technique to the text.

        Args:
            text: The original text
            technique: The transformation technique to apply

        Returns:
            The transformed text
        """
        if technique == "typos":
            return self._add_typos(text)
        elif technique == "capitalization":
            return self._change_capitalization(text)
        elif technique == "punctuation":
            return self._modify_punctuation(text)
        elif technique == "spacing":
            return self._modify_spacing(text)
        else:
            return text

    def _add_typos(self, text: str) -> str:
        """
        Add random typos to the text using the butter_finger method.

        Args:
            text: The original text

        Returns:
            Text with typos
        """
        result = self.butter_finger(text, prob=TextSurfaceAugmenterConstants.DEFAULT_TYPO_PROB, max_outputs=1)
        return result[0] if result else text

    def _change_capitalization(self, text: str) -> str:
        """
        Change the capitalization of some characters in the text.

        Args:
            text: The original text

        Returns:
            Text with modified capitalization
        """
        result = self.change_char_case(text, prob=TextSurfaceAugmenterConstants.DEFAULT_CASE_CHANGE_PROB, max_outputs=1)
        return result[0] if result else text

    def _modify_punctuation(self, text: str) -> str:
        """
        Modify punctuation in the text.

        Args:
            text: The original text

        Returns:
            Text with modified punctuation
        """
        # Simple implementation: replace periods with exclamation marks
        return text.replace('.', '!', 1) if '.' in text else text

    def _modify_spacing(self, text: str) -> str:
        """
        Modify spacing in the text using the add_white_spaces method.

        Args:
            text: The original text

        Returns:
            Text with modified spacing
        """
        result = self.add_white_spaces([text], max_outputs=1)
        return result[0][0] if result and result[0] else text

    def _add_white_spaces_to_single_text(self, value):
        """
        Add white spaces to the input text.

        Args:
            value: The input text to augment.

        Returns:
            Augmented text with added white spaces.
        """
        words = re.split(r"(\s+)", value)
        new_value = ""

        for word in words:
            if word.isspace():
                for j in range(random.randint(1, 3)):
                    new_value += TextSurfaceAugmenterConstants.WHITE_SPACE_OPTIONS[random.randint(0, 2)]
            else:
                new_value += word
        return new_value

    def add_white_spaces(self, inputs, max_outputs=TextSurfaceAugmenterConstants.DEFAULT_MAX_OUTPUTS):
        """
        Add white spaces to a list of input texts.

        Args:
            inputs: List of input texts to augment.
            max_outputs: Maximum number of augmented outputs per input.

        Returns:
            List of lists of augmented texts.
        """
        augmented_texts = []
        for input_text in inputs:
            augmented_input = []
            for i in range(max_outputs):
                # Apply augmentation
                cur_augmented_texts = self._add_white_spaces_to_single_text(input_text)
                augmented_input.append(cur_augmented_texts)
            augmented_texts.append(augmented_input)
        return augmented_texts

    def butter_finger(self, text, prob=TextSurfaceAugmenterConstants.DEFAULT_TYPO_PROB, keyboard="querty", seed=0,
                      max_outputs=TextSurfaceAugmenterConstants.DEFAULT_MAX_OUTPUTS):
        """
        Introduce typos in the text by simulating butter fingers on a keyboard.

        Args:
            text: Input text to augment.
            prob: Probability of introducing a typo for each character.
            keyboard: Keyboard layout to use.
            seed: Random seed for reproducibility.
            max_outputs: Maximum number of augmented outputs.

        Returns:
            List of texts with typos.
        """
        random.seed(seed)
        key_approx = TextSurfaceAugmenterConstants.QUERTY_KEYBOARD if keyboard == "querty" else {}

        if not key_approx:
            print("Keyboard not supported.")
            return [text]

        prob_of_typo = int(prob * 100)
        perturbed_texts = []
        for _ in itertools.repeat(None, max_outputs):
            butter_text = ""
            for letter in text:
                lcletter = letter.lower()
                if lcletter not in key_approx.keys():
                    new_letter = lcletter
                else:
                    if random.choice(range(0, 100)) <= prob_of_typo:
                        new_letter = random.choice(key_approx[lcletter])
                    else:
                        new_letter = lcletter
                # go back to original case
                if not lcletter == letter:
                    new_letter = new_letter.upper()
                butter_text += new_letter
            perturbed_texts.append(butter_text)
        return perturbed_texts

    def change_char_case(self, text, prob=TextSurfaceAugmenterConstants.DEFAULT_CASE_CHANGE_PROB, seed=0,
                         max_outputs=TextSurfaceAugmenterConstants.DEFAULT_MAX_OUTPUTS):
        """
        Change the case of characters in the text.

        Args:
            text: Input text to augment.
            prob: Probability of changing the case of each character.
            seed: Random seed for reproducibility.
            max_outputs: Maximum number of augmented outputs.

        Returns:
            List of texts with modified character cases.
        """
        random.seed(seed)
        results = []
        for _ in range(max_outputs):
            result = []
            for c in text:
                if c.isupper() and random.random() < prob:
                    result.append(c.lower())
                elif c.islower() and random.random() < prob:
                    result.append(c.upper())
                else:
                    result.append(c)
            result = "".join(result)
            results.append(result)
        return results


if __name__ == "__main__":
    # Example usage
    augmenter = TextSurfaceAugmenter(n_augments=3)
    original_prompt = "Please describe the process of photosynthesis in plants."
    variations = augmenter.augment(original_prompt)

    print(f"Original prompt: {original_prompt}")
    print("\nNon-LLM variations:")
    for i, variation in enumerate(variations):
        print(f"{i + 1}. {variation}")
    
    # Example usage of add_white_spaces
    inputs = ["This is a test sentence.", "Another example for augmentation."]
    augmented_texts = augmenter.add_white_spaces(inputs)
    print("Augmented Text:", augmented_texts)

    # Example usage of butter_finger
    butter_texts = augmenter.butter_finger(inputs[1], prob=0.2, max_outputs=3)
    print("Butter Text:", butter_texts)

    # Example usage of change_char_case
    char_case_texts = augmenter.change_char_case(inputs[0], prob=0.2, max_outputs=3)
    print("Change Char Case Text:", char_case_texts)