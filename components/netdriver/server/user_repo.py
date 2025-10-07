#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

class UserRepo:

    async def auth(self, username: str, password: str) -> bool:
        """ Auth username and password """
        # for simulate long authentication process
        if username.startswith("longauth"):
            await asyncio.sleep(10)
        return True
