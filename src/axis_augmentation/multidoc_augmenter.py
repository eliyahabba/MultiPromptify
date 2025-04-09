from itertools import permutations
from math import factorial
from random import sample
from typing import List

from datasets import load_dataset


class multidoc_augmenter():
    """
    This augmenter is intended for multi-document tasks, and performs augmentation on the
    list of documents of each example in the dataset.
    """

    def add_random_contexts(self, docs: List[str], corpus: List[str],
                            n_new_docs: int = 3) -> List[str]:
        """
        Adds n_new_docs random contexts from the corpus to the end of the docs list.
        :param docs: a list of documents to augment
        :param corpus: a list of documents to sample from
        :param n_new_docs: the number of irrelevant documents to sample from the corpus
        :return: an augmented list of documents, where the original docs appear first,
        and n_new_docs irrelevant documents are added
        """
        irrelevant_docs = sample([doc for doc in corpus if doc not in docs], n_new_docs)
        augmented_docs = docs + irrelevant_docs
        return augmented_docs

    def permute_docs_order(self, docs: List[str], n_permutations: int = 3) -> list[tuple[str, ...]]:
        """
        Generates variations of the order of the documents in the list.
        :param docs: a list of documents to augment
        :param n_permutations: the number of permutations to generate
        :return: a list of min(n_permutations, len(docs)) tuples of docs, where each tuple is a permutation of the docs
        """
        # if example has one doc, no order augmentation is needed
        if len(docs) <= 1:
            return [tuple(docs)]

        # generate all permutations of the docs
        n_iterations = min(n_permutations, factorial(len(docs)))
        augments = sample(list(permutations(docs)), n_iterations)
        return augments


if __name__ == "__main__":  # Example usage
    # Load the dataset (this is clapnq, a multi-document dataset intended for RAG)
    ds = load_dataset("PrimeQA/clapnq")['validation']['passages']
    docs = [ds[i][0]['text'] for i in range(3)]  # example 3 documents
    corpus = [item[0]['text'] for item in ds]  # entire corpus

    # run the augmenter on the example documents
    augmenter = multidoc_augmenter()
    docs_extended = augmenter.add_random_contexts(docs, corpus, 2)
    docs_permutations = augmenter.permute_docs_order(docs_extended, 5)
