from fastapi import FastAPI, Depends
from typing import List, Any
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

class BaseResponse(BaseModel):
    code: int = Field(200, description="API status code")
    msg: str = Field("success", description="API status message")
    data: Any = Field(None, description="API data")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": None
            }
        }

async def document():
    return RedirectResponse(url="/docs")

class OAuthLogin(BaseModel):
    accessKey: str = Field(..., description="Access Key")
    secretKey: str = Field(..., description="Secret Key")

from demo.oauth import (
    authenticate, ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token, get_secret_key
)
from datetime import timedelta

async def oauth_login(item: OAuthLogin):
    secretKey = await authenticate(item.accessKey, item.secretKey)
    if not secretKey:
        return BaseResponse(
            code=401,
            msg="Invalid access key or secret key",
            data=None
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": item.accessKey}, expires_delta=access_token_expires
    )
    return BaseResponse(
        code=200,
        msg="success",
        data=access_token
    )


from demo.constants import hydrometric_rhourrt_list
async def hydrometric_rhourrt_listLatest(
    secretKey: str = Depends(get_secret_key)
):
    return BaseResponse(
        code=200,
        msg="success",
        data=hydrometric_rhourrt_list
    )

def mount_app_routes(app: FastAPI, run_mode: str = None) -> None:
    app.get("/",
        tags=["Document"],
        response_model=BaseResponse,
        summary="API 文档")(document)
    
    app.post("/oauth/login",
        tags=["OAuth"],
        response_model=BaseResponse,
        summary="OAuth 登录")(oauth_login)
    
    app.get("/hydrometric/rhourrt/listLatest",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库最新水情列表（水库GIS图、水库列表）")(hydrometric_rhourrt_listLatest)

def create_app(run_mode: str = None) -> FastAPI:
    app = FastAPI(
        title="Centn Demo API Server",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    mount_app_routes(app, run_mode=run_mode)
    return app

if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=14525, loop="uvloop", http="httptools")