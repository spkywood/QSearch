#! python3
# -*- encoding: utf-8 -*-
'''
@File    : minio_client.py
@Time    : 2024/06/15 17:10:09
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import urllib
import urllib.parse
from minio import Minio
from minio.error import S3Error

from logger import logger
from app.core.singleton import Singleton

class MinioClient(metaclass=Singleton):
    def __init__(self, endpoint, access_key, secret_key, secure=True) -> None:
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def bucket_exists(self, bucket_name):
        return self.client.bucket_exists(bucket_name)
    
    def create_bucket(self, bucket_name):
        if bucket := self.bucket_exists(bucket_name):
            logger.warning(f"{bucket} has exists.")
        else:
            try:
                self.client.make_bucket(bucket_name)
            except S3Error as e:
                logger.warning(f"create {bucket} {e}.")

    def delete_bucket(self, bucket_name):
        try:
            self.client.remove_bucket(bucket_name)
        except Exception as e:
            logger.info(f'delete bucket {bucket_name} exception {e}')


    def upload_data(self, bucket_name, obj_name, data, size):
        try:
            self.client.put_object(bucket_name, obj_name, data, size)
        except S3Error as e:
            logger.warning(f"put object {obj_name} to {bucket_name} {e}.")
            raise Exception(f"{e}.")
    
    def upload_file(self, bucket_name, file_name, file_path):
        try:
            self.client.fput_object(bucket_name, file_name, file_path)
            logger.info(f"文件 {file_path} 上传成功。")
        except S3Error as e:
            print(f"上传文件时出错: {e}")

    def get_obj_url(self, bucket_name, obj_name):
        # url = self.client.presigned_get_object(bucket_name, obj_name)
        return self.client.presigned_get_object(bucket_name, obj_name)

from settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

minio_client = MinioClient(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)