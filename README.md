# QSearch

个人开发 RAG 应用，调用ChatGLM-4和Qwen-max

## 应用部署

```sh
git clone https://github.com/spkywood/QSearch.git

cd QSearch

touch .env
```

在.env文件中配置

```sh
# MYSQL 
MYSQL_HOST = ''
MYSQL_PORT = 3306
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_DATABASE = ''

# API_KEY
QWEN_API_KEY = ''
CHATGLM_API_KEY = ''
```

### 数据库初始化

```sh
python3 init.py
```

### 启动服务

```sh
python startup.py
```

## 主要组件

- fastapi 
- milvus    向量数据库
- mysql     系统数据库
- minio     对象存储
- es        全文检索

## 高级特性

- 上下文扩展
- 多路召回
- 查询后处理 Reranker

## TODO

- [ ] UI
- [ ] Document解析
- [ ] COT 
- [ ] 查询意图识别
- [ ] 查询分解
- [ ] 查询路由
- [ ] RAPTOR


## PS 

欢迎贡献代码代码，请联系

- 邮箱：longfellow.wang@gmail.com

## 参考

- [Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat)
- [Dify](https://github.com/langgenius/dify)
- [RAGflow](https://github.com/infiniflow/ragflow)
- [FastGPT](https://github.com/labring/FastGPT)
- [MaxKB](https://github.com/1Panel-dev/MaxKB)
