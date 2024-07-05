#! python3
# -*- encoding: utf-8 -*-
'''
@File    : run_async.py
@Time    : 2024/06/15 16:46:53
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from anyio import Semaphore
from typing import TypeVar, Callable
from typing_extensions import ParamSpec
from starlette.concurrency import run_in_threadpool

from settings import MAX_CONCURRENT_THREADS

MAX_THREADS_GUARD = Semaphore(MAX_CONCURRENT_THREADS)

T = TypeVar("T")
P = ParamSpec("P")

async def run_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    async with MAX_THREADS_GUARD:
        return await run_in_threadpool(func, *args, **kwargs)
