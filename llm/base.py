from abc import ABC, abstractmethod
from typing import Any


class BaseInput:
    """Base class for input data to the chain"""
    pass  # This can be extended with specific input attributes as needed


class BaseChain(ABC):
    """Base class for all chains"""

    @abstractmethod
    def invoke(self, inputs: BaseInput, **kwargs) -> Any:
        """Invoke the chain with given inputs

        Args:
            inputs: Input data for the chain
            **kwargs: Additional keyword arguments

        Returns:
            Chain execution result
        """
        pass

    @abstractmethod
    def get_prompt(self, inputs: BaseInput, **kwargs) -> str:
        """Get the prompt string for the given inputs

        Args:
            inputs: Input data for the chain
            **kwargs: Additional keyword arguments

        Returns:
            Formatted prompt string
        """
        pass