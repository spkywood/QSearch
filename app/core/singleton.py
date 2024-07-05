#! python3
# -*- encoding: utf-8 -*-
'''
@File    : singleton.py
@Time    : 2024/06/13 16:51:49
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import threading

class Singleton(type):
    """ 单例元类 """
    _instance_lock = threading.Lock()

    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super().__init__(*args, **kwargs)

    def _init_instance(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance

        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

    def __call__(cls, *args, **kwargs):
        reinit = kwargs.pop("reinit", True)
        instance = cls._init_instance(*args, **kwargs)
        if reinit:
            # 重新初始化单例对象属性
            instance.__init__(*args, **kwargs)
        return instance