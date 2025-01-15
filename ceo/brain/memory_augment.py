import abc
import copy
from collections import OrderedDict


class MemoryAugment:
    def __init__(self, memory: OrderedDict | None = None):
        self._memory: OrderedDict | None = None
        if memory is not None:
            self._memory = copy.deepcopy(memory)

    @property
    def memory(self) -> OrderedDict | None:
        if self._memory is not None:
            return copy.deepcopy(self._memory)
        return None

    @abc.abstractmethod
    def bring_in_memory(self, memory: OrderedDict): ...
