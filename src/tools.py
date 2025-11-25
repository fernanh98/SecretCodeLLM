from typing import List, Dict, Tuple, Any
from langchain_core.tools import tool

@tool
def indicate_secret_code(
        word: str, 
        number: int, 
        justification: str, 
        words_related: List[str]
    ) -> Dict[str, str | int | List[str]]:
    """
    Used to indicate the captain´s secret code, its justification and the words related to that secret code.

    Args:
        word (str): Word of the secret code
        number (int) Number of words related to the secret code
        justification (str): Justification to the chosen secret code with its corresponding words to which that secret code 
        makes reference. Should be a reasoning justificating the chosen secret code.
        words_relates (List[str]): Words to which the secret code is meant to make reference to

    Returns:
    A python list containing the complete secret code
    """
    return {"word": word, "number": number, "justification": justification, "words_related": words_related}

@tool
def choose_words(words: List[str], justification: str) -> Dict[str, List[str] | str]:
    """
    Used to indicate the words chosen by the guesser player

    Args:
        words (List[str]): Words chosen
        justification (str): Justification to why the chosen words are the ones the secret code is refering to. Should be a 
        reasoning justificating the chosen words.

    Returns:
    A python list containing the chosen words
    """
    return {"words": words, "justification": justification}