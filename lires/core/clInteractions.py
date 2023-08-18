"""
Some command line interactions classes
"""
from abc import ABC, abstractmethod, abstractproperty
from typing import List

class ChoicePromptAbstract(ABC):
    """
    Prompt user to make choices
    Define apis and should be inherited when used in GUI
    """
    def __init__(self):
        self._choice = "unknown"

    @abstractproperty
    def choice(self):
        """
        Get the choice after self.show
        """
        ...

    @abstractmethod
    def show(self, prompt: str, choices: List[str], title: str = "Prompt"):
        """
        show the prompt
        """
        ...


class ChoicePromptCLI(ChoicePromptAbstract):
    def __init__(self):
        super().__init__()

    def show(self, prompt: str, choices: List[str], title: str = "Prompt"):
        while True:
            input_ = input(prompt + "({}): ".format("/".join(choices)))
            if input_ in choices:
                self._choice = input_
                break
    @property
    def choice(self):
        return self._choice
