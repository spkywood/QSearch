from fastapi import APIRouter


from .users import router as users_router
from .llms import router as llms_router
from .files import router as files_router
from .knowledges import router as knowledges_router
from .tts import router as tts_router

v1_router = APIRouter()

v1_router.include_router(users_router)          #, tags=["users"]
v1_router.include_router(llms_router)           #, tags=["llms"]
v1_router.include_router(files_router)          #, tags=["files"]
v1_router.include_router(knowledges_router)     #, tags=["knowledges"]
v1_router.include_router(tts_router, tags=["tts"])        #, tags=["tts"]
