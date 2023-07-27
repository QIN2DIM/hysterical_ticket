# -*- coding: utf-8 -*-
# Time       : 2023/7/24 14:38
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

import asyncio
import inspect
import json
import logging
from contextlib import suppress
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import List

import httpx
from bs4 import BeautifulSoup
from httpx import AsyncClient


def from_dict_to_cls(cls, data):
    return cls(
        **{
            key: (data[key] if val.default == val.empty else data.get(key, val.default))
            for key, val in inspect.signature(cls).parameters.items()
        }
    )


@dataclass
class FnsContainer:
    red: List[str] = field(default_factory=list)
    blue: List[str] = field(default_factory=list)

    token = "fns"

    @classmethod
    def from_metadata(cls, sp: Path):
        metadata = {"red": [], "blue": []}
        try:
            metadata = json.loads(sp.read_text(encoding="utf8"))[FnsContainer.token]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return from_dict_to_cls(cls, metadata)

    def is_ready(self):
        return all(list(self.__dict__.values()))

    def as_metadata(self):
        md = {self.token: self.__dict__}
        md = json.dumps(md, indent=4, ensure_ascii=True, allow_nan=True)
        return md


@dataclass
class FilterNums:
    """双色球杀号"""

    next_term: str
    cache_dir: Path
    branch_ext: str

    fnc: FnsContainer
    _client: AsyncClient = None

    def __post_init__(self):
        if not self.branch_ext.startswith("."):
            self.branch_ext = f".{self.branch_ext}"
        self.output = self.cache_dir.joinpath(f"{self.next_term}{self.branch_ext}")
        self._url2res = {
            "https://cp.360.cn/shdd/shax": ["red"],  # red filter
            "https://cp.360.cn/shdd/shax?LotID=220051&ItemID=20344": ["blue"],  # blue filter
        }

    @classmethod
    def from_db(cls, sp: Path, **kwargs):
        """

        :param sp: [cache_dir]/[term][.branch_ext]
        :return:
        """
        cache_dir = sp.parent
        next_term, branch_ext = sp.name.split(".")
        fns_container = FnsContainer.from_metadata(sp)
        ins = cls(
            next_term=next_term,
            cache_dir=cache_dir,
            branch_ext=branch_ext,
            fnc=fns_container,
            **kwargs,
        )
        return ins

    async def fetch(self) -> FnsContainer:
        """
        获取下一期杀号
        filter_num: 预测在下一期中不会出现的号数，红蓝分开预测
        :return: self._container
        """

        def parse_result(res: httpx.Response):
            soup = BeautifulSoup(res.text, "html.parser")
            trs = soup.find("tbody").find_all("tr")
            with suppress(AttributeError, IndexError):
                term_text, nums_text = trs[-7].text.split(" ")
                filter_nums: List[str] = list(filter(None, nums_text.split("-")))
                filter_nums = sorted(list(set(filter_nums)))
                self._url2res[res.url].extend(filter_nums)
                self.fnc.__setattr__(self._url2res[res.url][0], filter_nums)

        if self.fnc.is_ready():
            logging.info(f"load cache - task=fns branch={self.branch_ext}")
            return self.fnc

        tasks = [self._client.get(url) for url in self._url2res]
        results = await asyncio.gather(*tasks)
        for result in results:
            parse_result(result)

        return self.fnc

    def save(self):
        metadata = self.fnc.as_metadata()
        self.output.write_text(metadata, encoding="utf8")


async def get_fns_container(fns_sp: Path) -> FnsContainer:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183",
        "Host": "cp.360.cn",
    }
    proxies = {"all://": None}

    # Extract filter nums of ssq from some
    async with AsyncClient(headers=headers, proxies=proxies) as client:
        fns = FilterNums.from_db(sp=fns_sp, _client=client)
        fns_container = await fns.fetch()
        fns.save()
    return fns_container
