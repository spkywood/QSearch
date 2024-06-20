# 小禹机器人内部demo接口

## 1. 鉴权接口

### 1.1 请求URL

http://192.168.1.126:14525/oauth/login

### 1.2 请求方式

POST

### 1.3 请求参数

```json
{
    "accessKey": "test",
    "secretKey": "8f5ad4b447f0e23a2f47154481ec8187"
}
```

### 1.4 返回参数

```json
{
    "code": 200,
    "msg": "success",
    "data": "{Token}"
    
}
```

## 2. 水库最新水情列表（水库GIS图、水库列表）

### 2.1 请求URL

http://192.168.1.126:14525/hydrometric/rhourrt/listLatest

### 2.2 请求方式

GET


## 3. 水库基础信息（水库简介、水库特征）

### 3.1 请求URL

http://192.168.1.126:14525/project/resv/get

### 3.2 请求方式

GET

## 4. 水库库容曲线


### 4.1 请求URL

http://192.168.1.126:14525/project/resvzv/list

### 4.2 请求方式

GET


## 5. 水库历年特征

### 5.1 请求URL

http://192.168.1.126:14525/hydrometric/resv/selectResMaxInfo

### 5.2 请求方式

GET

## 6. 水库实时水情

### 6.1 请求URL

http://192.168.1.126:14525/hydrometric/rhourrt/list

### 6.2 请求方式

GET

## 7. 水库历史水情

### 7.1 请求URL

http://192.168.1.126:14525/hydrometric/rdayrt/list?resname=BDA00000111

### 7.2 请求方式

GET

## 8. 地图展示水库降雨等值面

### 8.1 请求URL

http://192.168.1.126:14525/hydrometric/mock/getInfo1

### 8.2 请求方式

GET

## 9. 地图展示水库位置

### 9.1 请求URL

http://192.168.1.126:14525/hydrometric/mock/getInfo2

### 9.2 请求方式

GET

## 10. 根据水库名查询水库信息

### 10.1 请求URL

http://192.168.1.126:14525/project/resv/getByName

### 10.2 请求方式

GET

## 11. 文档图片查询接口（所有模块文件都用此接口）

### 11.1 请求URL

http://192.168.1.126:14525/filemanage/file/download

### 11.2 请求方式

GET

## 12. 水库实时水位

### 12.1 请求URL