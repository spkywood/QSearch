#! python3
# -*- encoding: utf-8 -*-
'''
@File    : tts.py
@Time    : 2024/07/31 08:53:20
@Author  : longfellow 
@Email   : longfellow.wang@gmail.com
@Version : 1.0
@Desc    : None
'''


import io
import wave
import os
import base64
import torch
import numpy as np
import uuid
from scipy.io import wavfile
from fastapi import APIRouter, Depends
from app.schemas.llm import AudioRequest
from zh_normalization import TextNormalizer


from settings import MODEL_PATH, WAVE_HOST, WAVE_PORT
from app.models.user import User
from logger import logger
from app.core.oauth import get_current_user
from app.core.response import BaseResponse
router = APIRouter()

import ChatTTS

logger.info("loading ChatTTS model...")

chat = ChatTTS.Chat()
text_normalizer = TextNormalizer()

chat.load_models(local_path=os.path.join(MODEL_PATH, "ChatTTS"))

# from app.runtime.online_model import OnlineModel
# from settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

# deepseek_model = OnlineModel(
#     api_key=DEEPSEEK_API_KEY, 
#     base_url=DEEPSEEK_BASE_URL,
#     model=DEEPSEEK_MODEL
# )

@router.post("/audio")
async def generate_audio(
    item: AudioRequest,
    user: User = Depends(get_current_user)
):
    torch.manual_seed(item.audio_seed)
    rand_spk = torch.randn(768)
    params_infer_code = {
        'spk_emb': rand_spk, 
        'temperature': item.temperature,
        'top_P': item.top_P,
        'top_K': item.top_K,
    }
    '''
    NSW (Non-Standard-Word) Normalization
    '''
    sents = text_normalizer.normalize(item.text)
    text = ''.join(sents)
    logger.info(f'NSW Normalization {text}')
    
    params_refine_text = {'prompt': '[oral_2][laugh_0][break_6]'}
    torch.manual_seed(item.text_seed)

    text = chat.infer(text, 
        skip_refine_text=False,
        refine_text_only=True,
        params_refine_text=params_refine_text,
        params_infer_code=params_infer_code
    )

    wav = chat.infer(text, 
        skip_refine_text=True, 
        params_refine_text=params_refine_text, 
        params_infer_code=params_infer_code
    )

    audio_data = np.array(wav[0]).flatten()

    TEMP_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "temp")
    wavname = f'{str(uuid.uuid4())}.wav' 
    wavfile.write(os.path.join(TEMP_PATH, wavname), 24000, audio_data)
    torch.cuda.empty_cache()

    return BaseResponse(
        code=200,
        message="success",
        data={
            "audio_file": f'http://{WAVE_HOST}:{WAVE_PORT}/waves/{wavname}',
            "text": text,
        },)