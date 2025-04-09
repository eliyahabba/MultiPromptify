from base_augmenter import BaseAxisAugmenter
from typing import List


#moran's simplest templates only adding {k times and the return style
simple_template = (
    "Please rephrase the following prompt {k} times. "
    "Return the results as a Python list of strings.\n\n"
    "'''{prompt}'''"
)

#moran's gpt3.5 templates, changes to general LLM and {k} times and the
# return style
llm_templates = (
    "Rephrase the following prompt to work better for an LLM. "
    "Generate {k} different versions and return them as a Python list of strings.\n"
    "'''{prompt}'''"
)

Talkative = (
    "Can you help me write a prompt to an LLM for the following task description? The prompt should be general.\n"
    "Generate {k} different versions and return them as a Python list of strings.\n"
    "'''{prompt}'''"
)




class Paraphrase(BaseAxisAugmenter):
    def __init__(self, k: int = 1):
        """
        Initialize the paraphrse augmenter.

        Args:
            k: number of paraphrase needed
        """
        self.k = k


    def augment(self,prompt:str) -> List[str]:
        pass


if __name__ == '__main__':
    print(template)