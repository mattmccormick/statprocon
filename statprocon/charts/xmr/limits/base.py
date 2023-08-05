from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Sequence


class Base(ABC):
    @abstractmethod
    def x_central_line(self) -> Sequence[Decimal]:
        pass

    @abstractmethod
    def upper_natural_process_limit(self) -> Sequence[Decimal]:
        pass

    @abstractmethod
    def lower_natural_process_limit(self) -> Sequence[Decimal]:
        pass
