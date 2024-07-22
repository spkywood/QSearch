# from app.runtime.local_model import LocalModel

# chatglm = LocalModel(
#     model_name='THUDM/chatglm3-6b',
# )

from tools.register import tools

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer
from settings import MODEL_PATH

def torch_gc():
    try:
        import torch
        if torch.cuda.is_available():
            # with torch.cuda.device(DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        elif torch.backends.mps.is_available():
            try:
                from torch.mps import empty_cache
                empty_cache()
            except Exception as e:
                pass
    except Exception:
        pass

model_name = 'THUDM/glm-4-9b-chat'

model_path = os.path.join(MODEL_PATH, model_name)

tokenizer = AutoTokenizer.from_pretrained(
    model_path, 
    trust_remote_code=True
)

llm_model = AutoModelForCausalLM.from_pretrained(
    model_path, 
    trust_remote_code=True).to(torch.bfloat16).cuda()
llm_model.eval()


class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = llm_model.config.eos_token_id
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
            
        return False

if __name__ == "__main__":
    model_inputs = tokenizer.apply_chat_template(
        messages=[
            {"role": "user", "content": "小浪底水库在哪里？"},
        ],
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt",
    ).to(llm_model.device)

    streamer = TextIteratorStreamer(
        tokenizer=tokenizer,
        timeout=60,
        skip_prompt=True,
        skip_special_tokens=True
    )

    stop = StopOnTokens()

    generate_kwargs = {
        "input_ids": model_inputs,
        "streamer": streamer,
        "max_new_tokens": 2048,
        "do_sample": True,
        "top_p": 0.7,
        "temperature": 1,
        "stopping_criteria": StoppingCriteriaList([stop]),
        "repetition_penalty": 1.2,
        "eos_token_id": llm_model.config.eos_token_id,
    }

    resp = llm_model.generate(**generate_kwargs)

    print(resp)

# resp = llm_model.chat(
#     tokenizer,
#     "小浪底水库在哪里？",
#     history=[],
#     max_length=2048,  # 如果未提供最大长度，默认使用2048
#     top_p=0.7,  # 如果未提供top_p参数，默认使用0.7
#     temperature=1,  # 如果未提供温度参数，默认使用0.95
#     tools=tools,
# )

# print(resp)
# torch_gc()