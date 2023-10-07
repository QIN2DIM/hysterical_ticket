# -*- coding: utf-8 -*-
# Time       : 2023/7/18 1:30
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import secrets
from pathlib import Path

logo_path = Path("static/logo.ico").absolute()
main_path = Path("main.py").absolute()
name = "hysterical_ticket"
key = secrets.token_hex()


def compile1():
    os.system("black . -C -l 100")
    cmd = f"pyinstaller {main_path} -F -w --clean -y -n {name} --key={key}"
    if logo_path.exists():
        cmd += f" -i {logo_path}"
    os.system(cmd)
    print(f"--> 打包完成: {cmd}")


if __name__ == "__main__":
    compile1()
