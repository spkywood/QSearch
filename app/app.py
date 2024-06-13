#! python3
# -*- encoding: utf-8 -*-
'''
@File    : app.py
@Time    : 2024/06/12 09:43:53
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from setting import VERSION
from app.router import mount_app_routers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app(run_mode: str = None) -> FastAPI:
    app = FastAPI(
        title="Cornfeild API Server",
        version=VERSION
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    mount_app_routers(app)

    return app
