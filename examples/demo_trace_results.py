# -*- coding: utf-8 -*-
# Time       : 2023/10/5 22:39
# Author     : QIN2DIM
# GitHub     : https://github.com/QIN2DIM
# Description: 双色球历史回测
import asyncio
from pathlib import Path

from hysterical_ticket.component.bingo_ssq import SSQNumsChecker
from hysterical_ticket.component.collector import trace_history

this_dir = Path(__file__).parent
tmp_dir = this_dir.joinpath("tmp_dir")
cache_path = tmp_dir.joinpath("双色球.csv")
ext = ".ssq"


async def main():
    tmp_dir.mkdir(exist_ok=True)

    await trace_history(cache_path, ext)

    nc = SSQNumsChecker(my_nums=my_nums)
    for mc, result in nc.trace_results(cache_path):
        if result.bonus and result.level < 6:
            print(
                f"💫 命中红球数: {result.red} 命中蓝球数: {result.blue} "
                f"- 中奖等级：{result.zh_level} 奖金：{result.bonus}￥ - {result.term}"
            )


if __name__ == "__main__":
    # [["06", "10", "17", "22", "25", "26", "09"]]
    my_nums = [["02", "08", "13", "19", "21", "30", "10"]]

    asyncio.run(main())
