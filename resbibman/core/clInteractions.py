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
    def __init__(self, prompt: str, choices: List[str], title: str = "Prompt"):
        self.prompt = prompt
        self.choices = choices
        self.title = title
        self._choice = "unknown"

    @abstractproperty
    def choice(self):
        """
        Get the choice after self.show
        """
        ...

    @abstractmethod
    def show(self):
        """
        show the prompt
        """
        ...


class ChoicePromptCLI(ChoicePromptAbstract):
    def __init__(self, prompt: str, choices: List[str] = ["Yes", "No"], title: str = "Prompt"):
        super().__init__(prompt, choices, title)
    def show(self):
        while True:
            input_ = input(self.prompt + "({})".format("/".join(self.choices)))
            if input_ in self.choices:
                self._choice = input_
                break
    @property
    def choice(self):
        return self._choice
