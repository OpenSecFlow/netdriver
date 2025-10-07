#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import asyncio
import asyncssh


client_option = asyncssh.SSHClientConnectionOptions(
    known_hosts=None,
    username="demo",
    password="demo",
    connect_timeout=10,
    login_timeout=5,
    keepalive_interval=60,
    keepalive_count_max=4
)

async def run_client() -> None:
    async with asyncssh.connect("192.168.60.100",
                                username="demo", password="demo",
                                known_hosts=None) as conn:
        try:
            result = await conn.run('show interface brief')
            # await asyncio.sleep(10)
        except asyncssh.ProcessError as exc:
            print('remote command failed:', exc, file=sys.stderr)
        else:
            print(result.stdout, end='')
        # await asyncio.sleep(10)


async def run_client_with_session() -> None:
    # connection close after context manager exit
    async with asyncssh.connect("192.168.60.99", options=client_option) as conn:
        try:
            writer, reader, err = await conn.open_session()
            writer.write("\n")
            # writer.write_eof()
            print(await reader.readuntil(r"> $"))
            error = await err.read(1024)
            if error:
                print("error:", error)
            # close mannually
            # conn.close()
        except asyncssh.Error as exc:
            print("filed wit ssh:", exc, file=sys.stderr)
    print("connection closed")
    await asyncio.sleep(20)


async def read_timed(stream: asyncssh.SSHReader,
                     timeout: float = 0.5,
                     bufsize: int = 100)-> str:
    """Read data from a stream with a timeout."""
    ret = ''
    while True:
        try:
            ret += await asyncio.wait_for(stream.read(bufsize), timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            return ret


async def read_timed_with_delay(stream: asyncssh.SSHReader,
                                       timeout: float = 0.1,
                                       delay_time: int = 0.8,
                                       delay_count: int = 3,
                                       bufsize: int = 1024)-> str:
    """Read data from a stream with a timeout."""
    output = ''
    while delay_count > 0:
        try:
            await asyncio.sleep(delay_time)
            ret = await asyncio.wait_for(stream.read(bufsize), timeout)
            if not ret:
                return output
            output += ret
            delay_count -= 1
        except (asyncio.TimeoutError, asyncio.CancelledError):
            if delay_count > 0:
                delay_count -= 1
                continue

    return output


async def run_client_with_process() -> None:
    conn = await asyncssh.connect("192.168.60.99", options=client_option)
    proc = await conn.create_process(term_type="ansi")
    print("start to read")
    # welcome = await read_timed(proc.stdout)
    # welcome = await proc.stdout.readuntil(re.compile("> $"))
    welcome = await read_timed_with_delay(proc.stdout)
    print(welcome, end='')

    proc.close()
    conn.close()


try:
    # asyncio.run(run_client())
    # asyncio.run(run_client_with_session())
    asyncio.run(run_client_with_process())
except (OSError, asyncssh.Error) as exc:
    sys.exit('SSH connection failed: ' + str(exc))
