from base_augmenter import BaseAxisAugmenter

class Paraphrase(BaseAxisAugmenter):
    def __init__(self, k: int = 1):
        """
        Initialize the paraphrse augmenter.

        Args:
            k: number of paraphrase needed
        """
        self.k = k


    def augment(
        self, prompt: str, examples: List[str], shuffle: bool = False
    ) -> List[str]:
        """
        Generate variations of the prompt by adding few-shot examples.

        Args:
            prompt: The original question/prompt
            examples: List of example Q&A pairs
            shuffle: Whether to shuffle the examples or keep original order

        Returns:
            List of prompts with different few-shot configurations
        """
        if not examples:
            return [prompt]

    }
