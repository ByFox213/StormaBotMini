from typing import TypeVar, NewType

__all__ = ("T", "Nickname")

T = TypeVar('T')
Nickname = NewType('Nickname', str)
