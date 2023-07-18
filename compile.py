# -*- coding: utf-8 -*-
# Time       : 2023/7/18 1:30
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import secrets
from pathlib import Path

logo = Path("static/logo.ico").absolute()
pymain = Path("main.py").absolute()
name = "hysteria_ticket"
key = secrets.token_hex()


def compile1():
    # pip install pyinstaller tinyaes
    # pyinstaller -F -w --clean -y -i [logo] -n [name] --key [secret]
    cmd = f"pyinstaller {pymain} -F -w --clean -y -i {logo} -n {name} --key={key}"
    os.system(cmd)
    print(f"--> 打包完成: {cmd}")


if __name__ == '__main__':
    compile1()
