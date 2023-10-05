# -*- coding: utf-8 -*-
# Time       : 2023/7/24 22:43
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 双色球本期计算器
from hysterical_ticket.component.bingo_ssq import SSQNumsChecker


def main():
    nc = SSQNumsChecker(my_nums=my_nums)
    for mc, result in nc.get_results(bingo_nums):
        if result.bonus:
            print(
                f"💫 命中红球数: {result.red} 命中蓝球数: {result.blue} "
                f"- 中奖等级：{result.zh_level} 奖金：{result.bonus}￥ - {mc}"
            )
        else:
            print(f"🔀 命中红球数: {result.red} 命中蓝球数: {result.blue} - {mc}")


if __name__ == "__main__":
    # Copy from the response of LLMs
    my_nums = [
        ["01", "07", "12", "18", "23", "25", "03"],
        ["02", "08", "13", "19", "21", "30", "09"],
        ["04", "09", "15", "22", "24", "26", "11"],
        ["03", "10", "16", "20", "27", "29", "05"],
        ["06", "14", "17", "28", "31", "32", "13"],
    ]

    bingo_nums = ["07", "09", "15", "16", "17", "26", "09"]

    main()
