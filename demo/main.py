import os
import json
from fastapi import FastAPI, Depends, HTTPException
from typing import List, Any
from datetime import timedelta
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware


from demo.constants import hydrometric_rhourrt_list
from demo.oauth import (
    authenticate, ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token, get_secret_key
)

BASE_PATH = '/home/wangxh/workspace/QSearch/demo/data'

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

class OAuthLogin(BaseModel):
    accessKey: str = Field(..., description="Access Key")
    secretKey: str = Field(..., description="Secret Key")

app = FastAPI(
    title="Centn Demo API Server",
    version="0.1.0"
)


@app.post("/oauth/login",
        tags=["OAuth"],
        response_model=BaseResponse,
        summary="OAuth 登录")
async def oauth_login(item: OAuthLogin):
    secretKey = await authenticate(item.accessKey, item.secretKey)
    if not secretKey:
        return HTTPException(
            status_code=401,
            detail="Incorrect username or password",
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

@app.get("/hydrometric/rhourrt/listLatest",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库最新水情列表（水库GIS图、水库列表）")
async def hydrometric_rhourrt_listLatest(
    secretKey: str = Depends(get_secret_key)
) -> BaseResponse:
    
    return BaseResponse(
        code=200,
        msg="success",
        data=hydrometric_rhourrt_list
    )

@app.get("/project/resv/get",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库基础信息（水库简介、水库特征）")
async def get_project_resv(
    resname: str,
    secretKey: str = Depends(get_secret_key)   
) -> BaseResponse:
    file = os.path.join(BASE_PATH, '水库基础信息', f'{resname}.json')
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseResponse(
            code=200,
            msg="success",
            data=data
        )
    else:
        return BaseResponse(
            code=404,
            msg="",
            data=None
        )


@app.get("/project/resvzv/list",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库库容曲线")
async def get_project_resv_list(
    resname: str,
    # secretKey: str = Depends(get_secret_key)   
) -> BaseResponse:
    file = os.path.join(BASE_PATH, '水库库容曲线', f'{resname}.json')
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseResponse(
            code=200,
            msg="success",
            data=data
        )
    else:
        return BaseResponse(
            code=404,
            msg="",
            data=None
        )
    
@app.get("/hydrometric/resv/selectResMaxInfo",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库历年特征")
async def get_resv_selectResMaxInfo(
    resname: str,
    # secretKey: str = Depends(get_secret_key)   
) -> BaseResponse:
    file = os.path.join(BASE_PATH, '水库历年特征', f'{resname}.json')
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseResponse(
            code=200,
            msg="success",
            data=data
        )
    else:
        return BaseResponse(
            code=404,
            msg="",
            data=None
        )

@app.get("/hydrometric/rhourrt/list",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库实时水情")
async def get_rhourrt_list(
    resname: str,
    startDate: str,
    endDate: str,
    # secretKey: str = Depends(get_secret_key)   
) -> BaseResponse:
    file = os.path.join(BASE_PATH, '水库实时水情', f'{resname}.json')
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseResponse(
            code=200,
            msg="success",
            data=data
        )
    else:
        return BaseResponse(
            code=404,
            msg="",
            data=None
        )
    

@app.get("/hydrometric/rdayrt/list",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="水库历史水情")
async def get_rdayrt_list(
    resname: str,
    startDate: str,
    endDate: str,
    # secretKey: str = Depends(get_secret_key)   
) -> BaseResponse:
    file = os.path.join(BASE_PATH, '水库历史水情', f'{resname}.json')
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseResponse(
            code=200,
            msg="success",
            data=data
        )
    else:
        return BaseResponse(
            code=404,
            msg="",
            data=None
        )
    
@app.get("/project/resv/getByName",
        tags=["Hydrometric"],
        response_model=BaseResponse,
        summary="根据水库名查询水库信息")
async def get_rdayrt_list(
    ennm: str,
    # secretKey: str = Depends(get_secret_key)   
) -> BaseResponse:
    file = os.path.join(BASE_PATH, '水库信息', f'{ennm}.json')
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseResponse(
            code=200,
            msg="success",
            data=data
        )
    else:
        return BaseResponse(
            code=404,
            msg="",
            data=None
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=14525, loop="uvloop", http="httptools")