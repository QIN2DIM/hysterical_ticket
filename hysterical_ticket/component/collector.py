from __future__ import annotations

import csv
import json
import logging
import sys
import time
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from pathlib import Path
from typing import Literal, List, Callable

import httpx
from bs4 import BeautifulSoup
from httpx import AsyncClient

logging.basicConfig(
    level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Branch(Enum):
    SSQ = Literal["ssq"]
    DLT = Literal["dlt"]


@dataclass
class Collector:
    branch: str

    _name: str = ""
    _latest_term: str = ""
    _container: List[List[str]] = field(default_factory=list)
    _container_head: List[str] = field(default_factory=list)
    _parser: Callable = None

    _client: AsyncClient = None

    @classmethod
    def from_branch(cls, branch: str, *args, **kwargs):
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
            self._parser = self._parse_dlt_data
        else:
            logging.error(f"Unknown branch type - branch={self.branch}")
            sys.exit(1)

    async def get_latest_term(self) -> str | None:
        if self._latest_term:
            return self._latest_term

        resp = await self._client.get("/history/history.shtml")

        soup = BeautifulSoup(resp.text, "html.parser")
        latest_term = soup.find("div", class_="wrap_datachart").find("input", id="end")["value"]

        self._latest_term = latest_term
        logging.info(f"get latest term - name={self._name} number={latest_term}")

        return latest_term

    def _parse_ssq_data(self, response: httpx.Response):
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

    def _parse_dlt_data(self, response: httpx.Response):
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

    async def get_history(self):
        """获取历史数据"""
        if self._container:
            logging.info(f"get history - name={self._name} length={len(self._container)}")
            return self._container

        params = {"start": 1, "end": await self.get_latest_term()}
        res = await self._client.get("/history/newinc/history.php", params=params)

        container = self._parser(res)

        logging.info(f"get history - name={self._name} size={len(container)}")

    def save_history(self, sp: Path):
        with open(sp, "w", encoding="utf8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self._container_head)
            writer.writerows(self._container)
        logging.info(f"save history - branch={self._name} path={str(sp)}")

        fn = f"{self._latest_term}.{self.branch}"
        metadata = {"version": self._latest_term}
        metadata = json.dumps(metadata, indent=4, sort_keys=False, ensure_ascii=True)
        sp.parent.joinpath(fn).write_text(metadata)
        logging.info(f"save latest term - branch={self._name} path={str(sp)}")


async def trace_history(output: Path, ext: str):
    if output.exists() and time.time() - output.stat().st_ctime < 43200:
        logging.info(f"load cache - task=collect ext={ext}")
        return

    branch = ext.replace(".", "")
    base_url = f"https://datachart.500.com/{branch}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79"
    }
    async with AsyncClient(headers=headers, base_url=base_url) as client:
        collector = Collector.from_branch(branch, _client=client)
        await collector.get_history()
        collector.save_history(output)
