
from db import minio_client, es_client, milvus_client

def main(kb_name):
    minio_client.delete_bucket(kb_name)
    milvus_client.client.drop_collection(kb_name)
    es_client.delete_index(kb_name)

    minio_client.create_bucket(kb_name)
    es_client.create_index(kb_name)
    milvus_client.create_collection(kb_name, dim=1024)

if __name__ == '__main__':
    import random
    import string
    a = ''.join(random.choices(string.ascii_lowercase, k=4))
    b = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    print(a+b)

