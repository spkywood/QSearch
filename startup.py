#! python3
# -*- encoding: utf-8 -*-
'''
@File    :   startup.py
@Time    :   2024/06/11 13:57:53
@Author  :   wangxh 
@Version :   1.0
@Email   :   longfellow.wang@gmail.com
'''


from fastapi import FastAPI
from settings import VERSION
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.lifespan import lifespan

def mount_app_routers(app: FastAPI):
    app.include_router(api_router, prefix="/api")

def create_app(run_mode: str = None) -> FastAPI:
    app = FastAPI(
        title="CentnGPT API Server",
        version=VERSION,
        lifespan=lifespan,
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


if __name__ == '__main__':
    import uvicorn
    app = create_app()
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=8000,
        loop="uvloop",
        http="httptools"
    )
    