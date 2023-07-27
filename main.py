# -*- coding: utf-8 -*-
# Time       : 2023/7/17 22:54
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import asyncio

from hysterical_ticket.ui import ChatPanel

if __name__ == "__main__":
    cp = ChatPanel()
    asyncio.run(cp.startup())
