from base_augmenter import BaseAxisAugmenter
from typing import List
from together import Together
import ast


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

    def build_rephrasing_prompt(self,templete: str, k: int, prompt: str) -> \
            str:
        return templete.format(k=k, prompt=prompt)

    def augment(self,prompt:str) -> List[str]:
        prompt =self.build_rephrasing_prompt(talkative,self.k,prompt)
        current_prompt = [
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=current_prompt,
        )

        return ast.literal_eval(response.choices[0].message.content)


# if __name__ == '__main__':
#     para = Paraphrase(10)
#     print(para.augment("Describe a historical figure you admire"))
#
