#! python3
# -*- encoding: utf-8 -*-
'''
@File    : api_v1_router.py
@Time    : 2024/06/12 09:50:15
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


from fastapi import FastAPI
from app.controller import (
    llms_controller,
    users_controller,
)


def mount_app_routers(app: FastAPI):
    app.include_router(users_controller.router, prefix='/api/v1', tags=['users'])
    app.include_router(llms_controller.router, prefix='/api/v1', tags=['llms'])