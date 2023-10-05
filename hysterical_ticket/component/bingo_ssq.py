# -*- coding: utf-8 -*-
# Time       : 2023/10/5 22:53
# Author     : QIN2DIM
# GitHub     : https://github.com/QIN2DIM
# Description:
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class Level:
    first = 1
    second = 2
    third = 3
    fourth = 4
    fifth = 5
    sixth = 6
    none = 0

    @staticmethod
    def get_bonus(level: int):
        level2bonus = {0: 0, 6: 5, 5: 10, 4: 200, 3: 3000, 2: -1, 1: -1}
        return level2bonus[level]

    @staticmethod
    def get_zh_level(level: int):
        level2zh = {0: "无", 6: "六等奖", 5: "五等奖", 4: "四等奖", 3: "三等奖", 2: "二等奖", 1: "一等奖"}
        return level2zh[level]


def is_bingo(red: int, blue: int):
    assert 0 <= red <= 6
    assert 0 <= blue <= 1

    if blue == 0:
        if red in [0, 1, 2, 3]:
            return Level.none
        if red == 4:
            return Level.fifth
        if red == 5:
            return Level.fourth
        if red == 6:
            return Level.second
    if blue == 1:
        if red in [0, 1, 2]:
            return Level.sixth
        if red == 3:
            return Level.fifth
        if red == 4:
            return Level.fourth
        if red == 5:
            return Level.third
        if red == 6:
            return Level.first


def compare_nums(mc: List[str], bingo_nums: List[str]):
    red = 0
    blue = 0
    for num_red in mc[:-1]:
        if num_red in bingo_nums[:-1]:
            red += 1
    if mc[-1] == bingo_nums[-1]:
        blue += 1

    return red, blue


@dataclass
class SSQResult:
    red: int = field(default=int)
    blue: int = field(default=int)
    level: int = field(default=int)
    bonus: int = field(default=int)
    zh_level: str = field(default=str)
    term: str = field(default=str)


class SSQNumsChecker:
    def __init__(self, my_nums: List[List[str]]):
        self.my_nums = my_nums

    def get_results(self, bingo_nums: List[str]):
        for i, mc in enumerate(self.my_nums):
            red, blue = compare_nums(mc, bingo_nums)
            level = is_bingo(red, blue)
            yield mc, SSQResult(
                red=red,
                blue=blue,
                level=level,
                bonus=Level.get_bonus(level),
                zh_level=Level.get_zh_level(level),
            )

    def trace_results(self, cache_path: Path):
        text = cache_path.read_text(encoding="utf8")
        reader = csv.reader([k for k in text.split("\n")[1:] if k])

        for j, tn in enumerate(reader):
            term = tn[0]
            bingo_nums = tn[1:]
            for i, mc in enumerate(self.my_nums):
                red, blue = compare_nums(mc, bingo_nums)
                level = is_bingo(red, blue)
                yield mc, SSQResult(
                    red=red,
                    blue=blue,
                    level=level,
                    bonus=Level.get_bonus(level),
                    zh_level=Level.get_zh_level(level),
                    term=term,
                )
