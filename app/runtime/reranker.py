#! python3
# -*- encoding: utf-8 -*-
'''
@File    : reranker.py
@Time    : 2024/06/13 11:02:44
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import torch
import numpy as np
from tqdm import tqdm
from typing import Union, List, Tuple
from app.runtime.local_model import LocalModel

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Reranker(LocalModel):
    def __init__(self, model_path: str = None, use_fp16: bool = False, device: str | int = None) -> None:
        super().__init__(model_path, use_fp16, device)

    @torch.no_grad()
    def compute_score(self, 
                      sentence_pairs: Union[List[Tuple[str, str]], Tuple[str, str]], 
                      batch_size: int = 256,
                      max_length: int = 512, 
                      normalize: bool = False
                      ) -> List[float]:
        if self.num_gpus > 0:
            batch_size = batch_size * self.num_gpus

        assert isinstance(sentence_pairs, list)
        if isinstance(sentence_pairs[0], str):
            sentence_pairs = [sentence_pairs]

        all_scores = []
        for start_index in tqdm(range(0, len(sentence_pairs), batch_size), desc="Compute Scores",
                                disable=len(sentence_pairs) < 128):
            sentences_batch = sentence_pairs[start_index:start_index + batch_size]
            inputs = self.tokenizer(
                sentences_batch,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=max_length,
            ).to(self.device)

            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
            all_scores.extend(scores.cpu().numpy().tolist())

        if normalize:
            all_scores = [sigmoid(score) for score in all_scores]

        if len(all_scores) == 1:
            return all_scores[0]
        return all_scores