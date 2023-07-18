# -*- coding: utf-8 -*-
# Time       : 2023/7/17 22:54
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

import os
import shutil
import time
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import easygui
import pyperclip

from hysteria_ticket.collector import Collector

TEMPLATE_SSQ = """
这个文件包含了双色球的近期开奖结果，一期结果中由 6 个红球和 1 个蓝球数字组合而成。在这个文件中，第 1 列至第 8 列分别是：

[开奖期号，红球1，红球2，红球3，红球4，红球5，红球6，蓝球1]

最新期号：{latest_term}，下一期：{next_term}

任务：合理预测下一期的开奖结果，给出 5 个你认为最可能的答案。

要求：
1. 输出的答案以 $ 字符开始，以 $ 字符结束，一行一组，与你其他的文本内容分隔开，调整为容易被反序列化成 Python 对象的格式
2. 输出的答案不能出现在已给出的 CSV 附件中
3. 输出的答案要符合中国大陆双色球的游戏规则
"""

TEMPLATE_DLT = """
这个文件包含了大乐透的近期开奖结果，一期结果中由 5 个红球和 2 个蓝球数字组合而成。在这个文件中，第 1 列至第 8 列分别是：

[开奖期号，红球1，红球2，红球3，红球4，红球5，蓝球1，蓝球2]

最新期号：{latest_term}，下一期：{next_term}

任务：合理预测下一期的开奖结果，给出 5 个你认为最可能的答案。

要求：
1. 输出的答案以 $ 字符开始，以 $ 字符结束，一行一组，与你其他的文本内容分隔开，调整为容易被反序列化成 Python 对象的格式
2. 输出的答案不能出现在已给出的 CSV 附件中
3. 输出的答案要符合中国大陆大乐透的游戏规则
"""


class Toolkit:
    @staticmethod
    def reset_global_proxy():
        proxies = urllib.request.getproxies()
        os.environ["HTTPS_PROXY"] = proxies.get("https", "").replace("https", "http")

    @staticmethod
    def setup_ordered_list(order: List[str]):
        return [f"{i + 1}. {v}" for i, v in enumerate(order)]

    @staticmethod
    def trace_ssq_history(output: Path):
        if not output.exists() or output.stat().st_ctime - time.time() > 43200:
            c = Collector.from_branch("ssq")
            c.get_history()
            c.save_history(output)

    @staticmethod
    def trace_dlt_history(output: Path):
        if not output.exists() or output.stat().st_ctime - time.time() > 43200:
            c = Collector.from_branch("dlt")
            c.get_history()
            c.save_history(output)

    @staticmethod
    def clean(root: Path) -> float | None:
        """return sizeof root(MB)"""
        total = 0
        if root.exists():
            for f in root.glob("**/*"):
                total += f.stat().st_size
            shutil.rmtree(root)
        return total / 1024**2

    @staticmethod
    def get_term_format(cache: Path, ext: str) -> Tuple[int, int]:
        latest_term = 0
        for fn in os.listdir(cache):
            if fn.endswith(ext):
                latest_term = int(fn.split(ext)[0])
        return latest_term, latest_term + 1


@dataclass
class Home:
    TITLE = "Hysteria Ticket"
    DEFAULT_AGENT = "ClaudeAI"

    root = Path("~/Documents/Hysteria Ticket").expanduser()
    cache_dir = root.joinpath("cache")

    path_ssq = cache_dir.joinpath("双色球.csv")
    path_dlt = cache_dir.joinpath("大乐透.csv")

    def __post_init__(self):
        self.kit = Toolkit

        # 重置代理格式
        self.kit.reset_global_proxy()

        # 编排解决方案
        self.path2solution = {
            self.path_ssq: (self.kit.trace_ssq_history, TEMPLATE_SSQ, ".ssq"),
            self.path_dlt: (self.kit.trace_dlt_history, TEMPLATE_DLT, ".dlt"),
        }

    def menu_main(self):
        choices = ["抓取双色球开奖记录", "抓取大乐透开奖记录", "清理缓存", "退出"]
        choices = self.kit.setup_ordered_list(choices)
        return easygui.choicebox(title=self.TITLE, choices=choices)

    def menu_get_history(self, output: Path):
        _cache_dir = output.parent

        # 初始化抓取程序
        os.makedirs(_cache_dir, exist_ok=True)
        solution, text, ext = self.path2solution[output]
        solution(output)

        # 自动打开 Playground 和 缓存目录
        os.startfile(_cache_dir)
        webbrowser.open("https://claude.ai/chats")

        # 生成提示词模版
        latest_term, next_term = self.kit.get_term_format(_cache_dir, ext)
        text = text.format(latest_term=latest_term, next_term=next_term)

        # 自动复制提示词
        pyperclip.copy(text)
        easygui.textbox(
            msg=f"1. 将 `{output.name}` 上传到 {self.DEFAULT_AGENT}\n" f"2. 使用提示词开启对话（已自动复制到剪贴板）",
            title=self.TITLE,
            text=text,
        )

    def menu_clean(self):
        sizeof = self.kit.clean(root=self.root)
        if not sizeof:
            return easygui.msgbox(msg="缓存已清空", title=self.TITLE)
        return easygui.msgbox(msg=f"共清理 {sizeof:.02f}MB 缓存", title=self.TITLE)

    def startup(self):
        result = self.menu_main()

        if not result or "退出" in result:
            return
        elif "双色球" in result:
            self.menu_get_history(self.path_ssq)
        elif "大乐透" in result:
            self.menu_get_history(self.path_dlt)
        elif "清理缓存" in result:
            self.menu_clean()
            return self.startup()
