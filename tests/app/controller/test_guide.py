import json
import random

from app.schemas.llm import QAType
from app.controllers.guide import add_guide, query_guides

async def test_add_guide():
    # Test the add_guide function here
    guides = await query_guides()
    rag = [guide.content for guide in guides if guide.qa_type == QAType.RAG]
    tool = [guide.content for guide in guides if guide.qa_type == QAType.TOOL]

    rag_select = random.sample(rag, min(6, len(rag)))# if len(rag) > 4 else rag
    tool_select = random.sample(tool, min(4, len(tool)))# if len(tool) > 4 else tool

    # rag_select = random.sample(
    #     [guide.content for guide in guides if guide.qa_type == QAType.RAG], 
    #     min(4, len([guide.content for guide in guides if guide.qa_type == QAType.RAG])))
    # tool_select = random.sample(
    #     [guide.content for guide in guides if guide.qa_type == QAType.TOOL], 
    #     min(6, len([guide.content for guide in guides if guide.qa_type == QAType.TOOL])))


    print(
        json.dumps({
                "RAG": rag_select,
                "TOOL": tool_select
            }, 
            ensure_ascii=False,
            indent=4
        )
    )
    

if __name__ == "__main__":
    import asyncio

    import sys
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(test_add_guide())
