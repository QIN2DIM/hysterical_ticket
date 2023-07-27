# -*- coding: utf-8 -*-
# Time       : 2023/7/17 22:54
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

import logging
import os
import shutil
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import easygui
import pyperclip

from hysterical_ticket.component.collector import trace_history
from hysterical_ticket.component.fns import get_fns_container
from hysterical_ticket.component.prompts import TEMPLATE_DLT
from hysterical_ticket.component.prompts import TEMPLATE_SSQ


class Toolkit:
    @staticmethod
    def reset_global_proxy():
        proxies = urllib.request.getproxies()
        os.environ["HTTPS_PROXY"] = proxies.get("https", "").replace("https", "http")

    @staticmethod
    def setup_ordered_list(order: List[str]):
        return [f"{i + 1}. {v}" for i, v in enumerate(order)]

    @staticmethod
    async def trace_history(output: Path, ext: str):
        return await trace_history(output, ext)

    @staticmethod
    def clean(root: Path, do: bool | None = True) -> float | None:
        """return sizeof root(MB)"""
        total = 0
        if root.exists():
            for f in root.glob("**/*"):
                total += f.stat().st_size
            if do:
                shutil.rmtree(root)
        return total / 1024**2

    @staticmethod
    def get_term_format(cache: Path, ext: str) -> Tuple[int, int]:
        latest_term = 0
        for fn in os.listdir(cache):
            if fn.endswith(ext):
                latest_term = int(fn.split(ext)[0])
        return latest_term, latest_term + 1

    @staticmethod
    async def gen_ignored_text(fns_sp: Path) -> str:
        template = ""
        try:
            container = await get_fns_container(fns_sp)
            template = f"红球不能出现如下列表中的数字：\n{container.red}\n蓝球不能出现如下列表中的数字：\n{container.blue}\n"
        except KeyError as err:
            logging.error(err)
        return template


@dataclass
class ChatPanel:
    TITLE = "Hysteria Ticket"

    # XLangAI https://chat.xlang.ai
    DEFAULT_AGENT = "ClaudeAI"

    root = Path("~/Documents/Hysteria Ticket").expanduser()
    cache_dir = root.joinpath("cache")
    history_dir = root.joinpath("history")

    path_ssq = history_dir.joinpath("双色球.csv")
    path_dlt = history_dir.joinpath("大乐透.csv")

    def __post_init__(self):
        self.kit = Toolkit

        # 重置代理格式
        self.kit.reset_global_proxy()

        # 编排解决方案
        self.path2solution = {
            self.path_ssq: (TEMPLATE_SSQ, ".ssq"),
            self.path_dlt: (TEMPLATE_DLT, ".dlt"),
        }

    def menu_main(self):
        choices = ["抓取双色球开奖记录", "抓取大乐透开奖记录", "清理缓存", "关于", "退出"]
        choices = self.kit.setup_ordered_list(choices)
        return easygui.choicebox(title=self.TITLE, choices=choices)

    async def menu_get_history(self, output: Path):
        # 初始化抓取程序
        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        text, ext = self.path2solution[output]

        # 启动 playground
        webbrowser.open("https://claude.ai/chats")

        # 执行抓取程序
        await self.kit.trace_history(output, ext)

        # 自动打开 Playground 和 数据目录
        os.startfile(self.history_dir)

        # 生成提示词模版
        latest_term, next_term = self.kit.get_term_format(self.history_dir, ext)

        # 插入杀号模版
        ignored_text = ""
        if ext.endswith("ssq"):
            fns_sp = self.cache_dir.joinpath(f"{next_term}{ext}")
            ignored_text = await self.kit.gen_ignored_text(fns_sp)

        text = text.format(latest_term=latest_term, next_term=next_term, ignored_text=ignored_text)

        # 自动复制提示词
        pyperclip.copy(text)
        easygui.textbox(
            msg=f"1. 将 `{output.name}` 上传到 {self.DEFAULT_AGENT}\n" f"2. 使用提示词开启对话（已自动复制到剪贴板）",
            title=self.TITLE,
            text=text,
        )

    def menu_validate(self):
        return

    def menu_clean(self):
        sizeof = self.kit.clean(root=self.root)
        if not sizeof:
            return easygui.msgbox(msg="缓存已清空", title=self.TITLE)
        return easygui.msgbox(msg=f"共清理 {sizeof:.02f}MB 缓存", title=self.TITLE)

    def menu_about(self):
        metadata = {
            "default_agent": self.DEFAULT_AGENT,
            "project_dir": self.root.__str__(),
            "cache_size": f"{self.kit.clean(root=self.root, do=False):.2f}MB",
        }
        return easygui.msgbox(
            msg="\n\n".join([f"{i} = {metadata[i]}" for i in metadata]), title=self.TITLE
        )

    async def startup(self):
        result = self.menu_main()

        if not result or "退出" in result:
            return

        if "双色球" in result:
            await self.menu_get_history(self.path_ssq)
        elif "大乐透" in result:
            await self.menu_get_history(self.path_dlt)
        elif "结果校验" in result:
            self.menu_validate()
            return await self.startup()
        elif "清理缓存" in result:
            self.menu_clean()
            return await self.startup()
        elif "关于" in result:
            self.menu_about()
            return await self.startup()
