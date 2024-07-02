
# from db import minio_client, es_client, milvus_client

# def main(kb_name):
#     minio_client.delete_bucket(kb_name)
#     milvus_client.client.drop_collection(kb_name)
#     es_client.delete_index(kb_name)

#     # minio_client.create_bucket(kb_name)
#     # es_client.create_index(kb_name)
#     # milvus_client.create_collection(kb_name, dim=1024)
#     return milvus_client.list_collections()

# if __name__ == '__main__':
    
#     print(main('hgbfp5cd2qcs'))