import os
import re
import json
from redis import Redis
from celery import Celery
from FlagEmbedding import FlagReranker

from settings import REDIS_HOST, REDIS_PORT, MODEL_PATH

redis_clinet = Redis(host=REDIS_HOST, port=REDIS_PORT)

celery_app = Celery(
    'celery_app', 
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2'
)

celery_app.conf.update(
    # task_serializer='json', 
    # accept_content=['json'], 
    # result_serializer='json'
    broker_connection_retry_on_startup=True
)

reranker = FlagReranker(f'{MODEL_PATH}/BAAI/bge-reranker-large', use_fp16=False)

@celery_app.task(name='highlight_content')
def highlight_content(user_name: str, quuid: str, answer: str):
    answers = [tmp for tmp in re.split('(?<=[。！？])', answer) if tmp.strip()]
    print('answers', answers)
    contexts = redis_clinet.hget(f'question:{user_name}', quuid)
    contexts = json.loads(contexts)
    if contexts is None:
        return ''
    for context in contexts:
        '''
        {
            "file_id" : context['file_id'],
            "file_name" : context['file_name'],
            "chunk" : context['chunk'],
            "file_url" : context['file_url'],
            "highlight" : ['', '', ...],
        }
        '''
        highlight = []
        print()
        backgrounds = re.split('(?<=[。！？])', context['chunk'])
        for answer in answers:
            sentence_pairs = [(answer, background) for background in backgrounds]
            all_scores = reranker.compute_score(sentence_pairs, normalize=True)
            sorted_scores, sorted_indices = zip(*sorted(zip(all_scores, range(len(all_scores))), reverse=True))
            highlight.append(backgrounds[sorted_indices[0]].replace('\n', ''))

        
        context.update(highlight=highlight)

    # contexts = redis_clinet.hget(f'question:{user_name}', quuid)
    redis_clinet.hset(f'question:{user_name}', quuid, json.dumps(contexts, indent=4, ensure_ascii=False))
