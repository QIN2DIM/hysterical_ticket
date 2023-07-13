from dataclasses import dataclass
from os.path import dirname
from pathlib import Path

from utils import init_log


@dataclass(slots=True)
class Project:
    root = Path(dirname(__file__))
    database = root.joinpath("database")

    path_ssq = database.joinpath("ssq.csv")
    path_dlt = database.joinpath("dlt.csv")

    logs = root.joinpath("logs")

    def __post_init__(self):
        self.database.mkdir(exist_ok=True)


project = Project()
init_log(
    error=project.logs.joinpath("error.log"),
    runtime=project.logs.joinpath("runtime.log"),
    serialize=project.logs.joinpath("serialize.log"),
)
