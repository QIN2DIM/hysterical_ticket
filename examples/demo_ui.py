# -*- coding: utf-8 -*-
# Time       : 2023/10/5 23:39
# Author     : QIN2DIM
# GitHub     : https://github.com/QIN2DIM
# Description:
import asyncio

from hysterical_ticket.ui import ChatPanel

if __name__ == "__main__":
    cp = ChatPanel()
    asyncio.run(cp.startup())
