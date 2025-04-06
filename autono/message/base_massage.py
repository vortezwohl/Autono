import abc


class BaseMessage:
    @abc.abstractmethod
    def to_dict(self): ...
