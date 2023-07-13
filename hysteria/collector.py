from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal, List, Callable

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests import Response

from settings import project


class Branch(Enum):
    SSQ = Literal["ssq"]
    DLT = Literal["dlt"]


@dataclass(slots=True)
class Collector:
    branch: Literal[Branch.SSQ, Branch.DLT]

    _name: str = ""
    _latest_term: str = ""
    _container: List[List[str]] = field(default_factory=list)
    _container_head: List[str] = field(default_factory=list)
    _sp: Path = field(default_factory=Path)
    _parser: Callable = None

    @classmethod
    def from_branch(cls, branch, *args, **kwargs):
        return cls(branch=branch, *args, **kwargs)

    def __post_init__(self):
        self._container = []
        self._container_head = []

        if self.branch in [Branch.SSQ, "ssq"]:
            self._name = "双色球"
            self._container_head = [
                "term",
                "red_1",
                "red_2",
                "red_3",
                "red_4",
                "red_5",
                "red_6",
                "blue_1",
            ]
            self._sp = project.path_ssq
            self._parser = self._parse_ssq_data
        elif self.branch in [Branch.DLT, "dlt"]:
            self._name = "大乐透"
            self._container_head = [
                "term",
                "red_1",
                "red_2",
                "red_3",
                "red_4",
                "red_5",
                "blue_1",
                "blue_2",
            ]
            self._sp = project.path_dlt
            self._parser = self._parse_dlt_data
        else:
            logger.critical("Unknown branch type", branch=self.branch)
            sys.exit(1)

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return f"https://datachart.500.com/{self.branch}/history/newinc/history.php"

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79"
        }

    def get_latest_term(self) -> str | None:
        if self._latest_term:
            return self._latest_term

        api = f"https://datachart.500.com/{self.branch}/history/history.shtml"
        resp = requests.get(api, headers=self.headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        latest_term = soup.find("div", class_="wrap_datachart").find("input", id="end")["value"]
        self._latest_term = latest_term
        logger.info("get latest term", name=self._name, number=latest_term)

        return latest_term

    def _parse_ssq_data(self, response: Response):
        soup = BeautifulSoup(response.text, "html.parser")
        trs = soup.find("tbody", attrs={"id": "tdata"}).find_all("tr")

        # 8列数据：期数ID, 红球6个, 蓝球1个
        container = []
        for tr in trs:
            temp_ = [tr.find_all("td")[0].get_text().strip()]
            temp_.extend([tr.find_all("td")[i].get_text().strip() for i in range(1, 7)])
            temp_.append(tr.find_all("td")[7].get_text().strip())
            container.append(temp_)
        self._container = container
        return container

    def _parse_dlt_data(self, response: Response):
        soup = BeautifulSoup(response.text, "html.parser")
        trs = soup.find("tbody", attrs={"id": "tdata"}).find_all("tr")

        # 8列数据：期数ID, 红球5个, 蓝球2个
        container = []
        for tr in trs:
            temp_ = [tr.find_all("td")[0].get_text().strip()]
            temp_.extend([tr.find_all("td")[i].get_text().strip() for i in range(1, 6)])
            temp_.extend([tr.find_all("td")[i].get_text().strip() for i in range(6, 8)])
            container.append(temp_)
        self._container = container
        return container

    def get_history(self):
        """获取历史数据"""
        if self._container:
            logger.info("get history", name=self._name, length=len(self._container))
            return self._container

        params = {"start": 1, "end": self.get_latest_term()}
        resp = requests.get(self.url, params=params, headers=self.headers)
        container = self._parser(response=resp)
        logger.info("get history", name=self._name, size=len(container))

    def save_history(self):
        with open(self._sp, "w", encoding="utf8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self._container_head)
            writer.writerows(self._container)
        logger.success("save history", branch=self._name, path=str(self._sp))


def _trace_history(*, branch, output: Path = None, **kwargs):
    c = Collector.from_branch(branch=branch, _sp=output, **kwargs)
    c.get_history()
    c.save_history()


def trace_ssq_history():
    return _trace_history(branch="ssq")


def trace_dlt_history():
    return _trace_history(branch="dlt")
