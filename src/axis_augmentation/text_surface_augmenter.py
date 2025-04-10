# Non-semantic changes / structural changes (UNI TEXT)
import itertools
import random
import re

import numpy as np

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
                for j in range(random.randint(
                        TextSurfaceAugmenterConstants.MIN_WHITESPACE_COUNT,
                        TextSurfaceAugmenterConstants.MAX_WHITESPACE_COUNT)):
                    new_value += TextSurfaceAugmenterConstants.WHITE_SPACE_OPTIONS[random.randint(
                        TextSurfaceAugmenterConstants.MIN_WHITESPACE_INDEX,
                        TextSurfaceAugmenterConstants.MAX_WHITESPACE_INDEX)]
            else:
                new_value += word
        return new_value

    def add_white_spaces(self, inputs, max_outputs=TextSurfaceAugmenterConstants.DEFAULT_MAX_OUTPUTS):
        """
        Add white spaces to input text(s).

        Args:
            inputs: Either a single text string or a list of input texts to augment.
            max_outputs: Maximum number of augmented outputs per input.

        Returns:
            If inputs is a string: List of augmented texts.
            If inputs is a list: List of lists of augmented texts.
        """
        # Handle single text input
        if isinstance(inputs, str):
            augmented_input = []
            for i in range(max_outputs):
                augmented_text = self._add_white_spaces_to_single_text(inputs)
                augmented_input.append(augmented_text)
            return augmented_input

        # Handle list of texts
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

    def swap_characters(self, text, prob=TextSurfaceAugmenterConstants.DEFAULT_TYPO_PROB, seed=0,
                        max_outputs=TextSurfaceAugmenterConstants.DEFAULT_MAX_OUTPUTS):
        """
        Swaps characters in text, with probability prob for ang given pair.
        Ex: 'apple' -> 'aplpe'
        Arguments:
            text (string): text to transform
            prob (float): probability of any two characters swapping. Default: 0.05
            seed (int): random seed
            max_outputs: Maximum number of augmented outputs.
            (taken from the NL-Augmenter project)
        """
        results = []
        for _ in range(max_outputs):
            max_seed = 2 ** 32
            # seed with hash so each text of same length gets different treatment.
            np.random.seed((seed + sum([ord(c) for c in text])) % max_seed)
            # np.random.seed((seed) % max_seed).
            # number of possible characters to swap.
            num_pairs = len(text) - 1
            # if no pairs, do nothing
            if num_pairs < 1:
                return text
            # get indices to swap.
            indices_to_swap = np.argwhere(
                np.random.rand(num_pairs) < prob
            ).reshape(-1)
            # shuffle swapping order, may matter if there are adjacent swaps.
            np.random.shuffle(indices_to_swap)
            # convert to list.
            text = list(text)
            # swap.
            for index in indices_to_swap:
                text[index], text[index + 1] = text[index + 1], text[index]
            # convert to string.
            text = "".join(text)
            results.append(text)
        return results

if __name__ == "__main__":
    # Example usage
    augmenter = TextSurfaceAugmenter(n_augments=3)

    # Sample text for augmentation
    inputs = ["The quick brown fox jumps over the lazy dog.", "The rain in Spain stays mainly in the plain."]

    # Example usage
    augmented_texts = augmenter.add_white_spaces(inputs)
    print("Augmented Text:", augmented_texts)

    # Example usage of butter_finger
    butter_texts = augmenter.butter_finger(inputs[1], prob=0.2, max_outputs=3)
    print("Butter Text:", butter_texts)

    # Example usage of change_char_case
    char_case_texts = augmenter.change_char_case(inputs[0], prob=0.2, max_outputs=3)
    print("Change Char Case Text:", char_case_texts)

    # Example usage of swap_characters
    swap_texts = augmenter.swap_characters(inputs[1], prob=0.05, max_outputs=3)
    print("Swap Characters Text:", swap_texts)