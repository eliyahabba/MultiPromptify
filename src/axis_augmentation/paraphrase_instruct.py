from base_augmenter import BaseAxisAugmenter
from typing import List
from together import Together


model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
client = Together()



#moran's gpt3.5 templates, changes to general LLM and {k} times and the
# return style
llm_templates = (
    "Rephrase the follbuild_rephrasing_promptowing prompt, providing {k} alternative versions that are better suited for an LLM while preserving the original meaning. Output only a Python list of strings with the alternatives. Do not include any explanation or additional text. \n"
    "Prompt: '''{prompt}'''"
)

#moran's begining but adding specifications, restriction on the output and
# the word "creative"
talkative = (
    "Can you help me write a prompt to an LLM for the following task "
    "description? Providing {k} creative versions while preserving the "
    "original meaning. \nOutput only a Python list of strings with the "
    "alternatives. Do not include any explanation or additional text. \n"
    "Prompt: '''{prompt}'''"
)
prompt_bank =[llm_templates, talkative]





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


def trying_func(k=5):
    def build_rephrasing_prompt(templete: str, k: int, prompt: str) -> str:
        return templete.format(k=k, prompt=prompt)

    print(build_rephrasing_prompt(talkative,k,"Given a query word and two other words, determine which of the two words is a homophone of the query word."))
    prompts =
if __name__ == '__main__':
    trying_func(5)
