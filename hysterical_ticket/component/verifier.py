# -*- coding: utf-8 -*-
# Time       : 2023/7/24 19:01
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from dataclasses import dataclass, field
from typing import List


@dataclass
class Verifier:
    raw_container: str = None
    _sequence: List[List[str]] = field(default_factory=list)

    def __post_init__(self):
        self._sequence = self._sequence or []

    @classmethod
    def from_str(cls, raw_container: str):
        return cls(raw_container=raw_container)

    @classmethod
    def from_list(cls, raw_sequence: List[List[str]]):
        return cls(_sequence=raw_sequence)
