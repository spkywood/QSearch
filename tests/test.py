import json
from db.redis_client import redis

uuids = [
"1e9caba5-9a01-5d35-9761-da766f75dd55",
"ed6916e4-045e-5bf9-999e-c58ce6237dd8",
"31478500-a923-55e4-9304-f712c6632601",
"378ac585-a851-5af3-8cce-57e4eb4fe9c5",
"d7065216-b266-578c-8026-668823299630",
"5646526e-e847-5586-89ba-aab36ef20796",
"41152237-531c-5b1a-b454-f90f59fb33d5",
"06458ffd-acb7-553d-b14f-24832ef6b612",
"cdd65cba-4313-547c-a346-a9f45351d8a4",
"c820ddca-fab2-506a-b42f-89766b857f08",
"c563e07c-d5f3-5069-868e-c917db633f20",
"339d8657-1c8a-54d3-9374-8e6ece29324f",
"e77d8389-3650-5d4b-bcee-44cbc050fb3d",
"0f3e16ad-efba-56ff-979c-e1511c755a5c",
"11cc327a-8dff-5d7c-8fcf-86563e11a393",
"4f9420f1-b565-51a5-8ad0-7e8489143b8b",
"fdc35723-6558-5e7f-9c35-562c3e18a75e",
"ad595d69-9e2a-5a00-b3d2-cda426c923f1",
"c9a8b69a-9ef8-54c8-9d39-f1a51ed92f62",
"107963fd-5120-518c-9e52-5bd514402623",
"dd9459ce-77e5-5119-a70b-abe5456cf26d",
"9f05c382-7b5a-5365-b1f8-d087d5b6303a",
"2c6b8d19-7869-55b2-87ed-381803673347",
"186b3427-e17e-5804-a60f-bde352aba23b",
"907c6fa2-7316-560d-a781-b0d530e4e960",
"d9609625-9146-52f2-b478-c068c2c74762",
"89b133f7-8c19-5a12-b503-c309322c3aff",
"22938c06-2ee8-56c3-9c5f-da339a2b33af",
"6cbbefc0-cb48-53f6-a507-f406735825dc",
"8d925b75-b9d0-5168-a508-19cd9bed1c20",
"ad14b40d-cad5-5fff-a46a-439cedc475a9",
"1b0477cb-7efe-57b5-ab77-520fefefbe8a",
"77a6e23a-390c-57a2-badc-5ac61b960c65",
"6eb0ca02-8bb5-58db-b9a0-79db8b44ee30",
"553da595-2fc3-58ca-8f10-6af2750c4346",
"2ffd83ef-53ac-5310-918b-1bcc765667f2",
"2362ff6d-c651-5879-97f7-d0d1465c03e9",
"3595d627-b37d-512b-ba1f-e2639cdf26f8",
"2ef6e884-fec9-5591-a87e-ccdb43f56757",
"cb7d14ad-1a4a-583e-8596-88c2433f3abb",
"ea69759f-354f-5334-b2d7-fb909f18852a",
"0c6fd52d-ce80-51ca-aede-addcb048b1dd",
"e56a1480-e4ca-5e57-80f1-505d33976d95",
"3e366d2c-2f18-535b-a8bc-d8539f6b8e72",
"95168888-229a-5265-bfc2-8b9a064bdace",
"a8aa10bf-8e99-528a-a296-2d6b8a8730f0",
"60d66bd4-7a42-51df-8ed8-07f7f7da31a7",
"fde41ce9-4fc8-5554-b552-97d54e136200",
"4e424991-9961-5323-b241-3e9e5024845c",
"cb29036b-032d-5d48-9379-509d4234b16f",
"3b0c6fdc-5b38-53d3-8ed7-9f41c9a2112b",
"eb32546b-edb7-509b-a7c7-d1292afb3f79",
"b6537c81-edc0-5aaa-87c5-17ac9f623ce2",
"f3b7d349-ea69-5d41-8b6a-78f021ae5989",
"a03f775f-24e4-5f9c-ba76-c4463672bdce",
"26547077-b82a-5d0b-ae71-f150f2f62064",
"4333527b-5853-5b78-b512-70e692122b2a",
"7586c818-ce4f-529e-9ef0-0031cf50926a",
"6d232b9e-2ece-5276-ac0c-e8dc878fd817",
"43ff5e9b-93c8-5344-8e46-3d22df02adc7",
"cba7309a-1379-5606-b833-c496a124cd42",
"8a915ab7-dc36-539d-8095-e6562eb99be8",
"4e6edbca-9711-5b70-971b-2963db0d2776",
"45f886e9-a1d9-586c-ad96-40e0943d557d",
"18354911-7471-5863-a4b0-5650198143d8",
"be3bffb3-5994-5200-8f33-f67a2d0068d6",
"6ca9f9da-4098-5c2e-a358-8796603197e7",
"1ce50824-6152-55b2-823f-692312b66f24",
"6c59b68a-a3ff-57c9-9dc5-522f5dca4545",
"dac0e71c-a37c-5a74-8cc3-84582706548e",
"98c1e98a-378e-543c-9690-9caa8d07bacf",
"0fd1ec3d-c20b-5e52-b90a-618df5ba7803",
"546f77ee-7381-50be-af9a-6d44a08a175a",
"b64b412a-a3cd-587a-b187-be0898561af1",
"11b72a53-721b-54af-8b80-e2c5db429998",
"eba66fca-e823-50bc-b387-8e7994cab7fe",
"4c6b60bd-079d-5179-8e4e-8c8f15c49653",
"30a0d814-c804-550e-ad7b-70dbf2e76db8",
"14e6e5bf-bc17-54a9-ba13-33acff16cd1b",
"6d2c7441-0f49-50b0-879f-ba129892174a",
"6da62352-0394-5fec-b829-e14b7bd3ad0a",
"d43e10f7-30b0-55b1-96c8-2a5913403ff3",
"be2e4235-1f94-5169-8d20-ba2315d8f434",
"42c3039a-ab7e-58ff-9e31-c96093b7df19",
"55b1cc61-a45c-579a-a9a3-bb1dcc5906f9",
"e52f5ce6-02cc-5d5e-9d15-0c02ce8cdf10",
"d063b346-e7c6-528d-a926-6dac496a6848",
"d2fbabe2-13ca-5701-a74d-4716dd764e36",
"cfe48fdf-4399-55ef-bd08-74fa216eaf9a",
"88e7a822-d09f-520d-9721-390536d5361b",
"e65ef1ab-5efa-56aa-bd35-a27772ae5d84",
"24d3780c-b427-5ab0-9853-997c88644b00",
"081e83a8-1504-54a4-8943-2b8360ae6a93",
"7e6e1033-ad47-5d95-afd3-d464f191f7a5",
"50a46d95-6bbc-548c-b753-b3363a8c21ca",
"6649a721-c0e8-5451-bab7-4371e3867048",
"8ea8a994-6cc6-5f8b-b8a7-df1ba150f666",
"f0f4e33a-1146-5c47-bd4b-b639c83e69e0",
"bf6757c5-48e2-5a3a-b9ff-16cee1b87e0c",
]

async def test():
    # for uuid in uuids:
    #     with open(f'tests/{uuid}.json', 'w') as f:
    #         redis_name = f'conversation:test'
    #         history = await redis.hget(redis_name, uuid)
    #         history = json.loads(history)

    #         f.write(json.dumps(history, indent=4, ensure_ascii=False))
    redis_name = f'conversation:test'
    history = await redis.hget(redis_name, "d3876997-5836-5e3d-b0e6-6cb6a3643acf")
    history = json.loads(history)

    print(json.dumps(history, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    # import asyncio
    # import sys

    # if sys.version_info < (3, 10):
    #     loop = asyncio.get_event_loop()
    # else:
    #     try:
    #         loop = asyncio.get_running_loop()
    #     except RuntimeError:
    #         loop = asyncio.new_event_loop()
    
    # asyncio.set_event_loop(loop)
    
    # loop.run_until_complete(test())
    from tools.register import tools

    import json
    with open('tests/tools.json', 'w') as f:
        f.write(json.dumps(tools, indent=4, ensure_ascii=False))
