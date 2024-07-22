#! python3
# -*- encoding: utf-8 -*-
'''
@File    : local_model.py
@Time    : 2024/06/13 11:04:18
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''



import os
import time
import torch
from pathlib import Path
from typing import Union, List, Dict, Optional, Any
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer
)

from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM

from settings import MODEL_PATH


class StopOnTokens(StoppingCriteria):
    def __init__(self, stop_ids):
        self.stop_ids = stop_ids

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop_id in self.stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False

class LocalModel:
    def __init__(self, 
                 model_name: str = 'THUDM/glm-4-9b-chat',
                 use_fp16: bool = False,
                 device: Union[str, int] = None
    ) -> None:
        self.model_path = os.path.join(MODEL_PATH, model_name)
        self.model, self.tokenizer = self.load_model_and_tokenizer(self.model_path)

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        return Path(path).expanduser().resolve()

    def load_model_and_tokenizer(
        self, model_dir: Union[str, Path], trust_remote_code: bool = True
    ) -> tuple[Union[PreTrainedModel, PeftModelForCausalLM], Union[PreTrainedTokenizer, PreTrainedTokenizerFast]]:
        model_dir = self._resolve_path(model_dir)
        if (model_dir / 'adapter_config.json').exists():
            model = AutoPeftModelForCausalLM.from_pretrained(
                model_dir, trust_remote_code=trust_remote_code, device_map='auto'
            )
            tokenizer_dir = model.peft_config['default'].base_model_name_or_path
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_dir, trust_remote_code=trust_remote_code, device_map='auto'
            )
            tokenizer_dir = model_dir
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_dir, trust_remote_code=trust_remote_code, use_fast=False
        )
        return model, tokenizer
    
    def invoke(self,
        messages: Union[str, List[Dict[str, str]]],
        tools : Optional[object] = None,
        top_p: float = 0.7,
        temperature: float = 0.7,
        max_tokens = 2048,
    ):
        messages[0].update({"tools": tools})
        streamer = TextIteratorStreamer(
            self.tokenizer, 
            timeout=60, 
            skip_prompt=True, 
            skip_special_tokens=True
        )

        stop = StopOnTokens(stop_ids=self.model.config.eos_token_id)

        model_inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt"
        ).to(next(self.model.parameters()).device)
        
        generate_kwargs = {
            "input_ids": model_inputs,
            "streamer": streamer,
            "max_new_tokens": max_tokens,
            "do_sample": True,
            "top_p": top_p,
            "temperature": temperature,
            "stopping_criteria": StoppingCriteriaList([stop]),
            "repetition_penalty": 1.2,
            "eos_token_id": self.model.config.eos_token_id,
        }

        self.model.generate(**generate_kwargs)

        for new_token in streamer:
            if new_token:
                yield new_token
                time.sleep(0.02)
    

if __name__ == '__main__':
    glm4_9b = LocalModel()
    from tools.register import tools
    messages = [
        {"role": "user", "content": "小浪底水库在哪里"}
    ]

    resp = glm4_9b.invoke(messages, tools=tools)

    for r in resp:
        print(r)