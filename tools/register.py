#! python3
# -*- encoding: utf-8 -*-
'''
@File    : register.py
@Time    : 2024/06/13 14:39:08
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import json
import inspect
from datetime import datetime, time
from collections import OrderedDict
from types import GenericAlias
from typing import get_origin, Annotated, Dict, List
import requests
from common import logger

tools = []
_TOOL_HOOKS = OrderedDict()

def register_tools(func: callable):
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip()
    python_params = inspect.signature(func).parameters
    tool_params = []
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")
        if get_origin(annotation) != Annotated:
            raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")

        typ, (description, required) = annotation.__origin__, annotation.__metadata__
        typ: str = str(typ) if isinstance(typ, GenericAlias) else typ.__name__
        if not isinstance(description, str):
            raise TypeError(f"Description for `{name}` must be a string")
        if not isinstance(required, bool):
            raise TypeError(f"Required for `{name}` must be a bool")

        tool_params.append({
            "name": name,
            "description": description,
            "type": typ,
            "required": required
        })

    properties = OrderedDict()
    for param in tool_params:
        properties[param["name"]] = {
            "description": param["description"],
            "type": param["type"]
        }

    tool_def = {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            "parameters": {
                "type": "object",
                "properties": properties,
            },
            "required": [tool_param["name"] for tool_param in tool_params if tool_param["required"]]
        },
        
    }

    tools.append(tool_def)
    _TOOL_HOOKS[tool_name] = func
    
    return func

def dispatch_tool(tool_name: str, kwargs: dict):
    if tool_name not in _TOOL_HOOKS:
        logger.info(f"Tools `{tool_name}` not defined")
        raise RuntimeError(f"Tools `{tool_name}` not defined")
    
    tool_call = _TOOL_HOOKS[tool_name]
    try:
        logger.info(f'tool_call:{kwargs}')
        ret = tool_call(**kwargs)
    except Exception as e:
        raise RuntimeError(f"Tools `{tool_name}` Call {e}")
    return ret

# -------------------------------------
# -----------   自定义工具   -----------
# -------------------------------------

import json
BASE_URL = 'http://192.168.1.126:14525'

RESERVOIR_DICT = {
    "龙羊峡" : "BDA00000011",
    "刘家峡" : "BDA00000031",
    "青铜峡" : "BDA00000072",
    "海勃湾" : "BDA00000081",
    "万家寨" : "BDA00000092",
    "龙口" : "BDA00000101",
    "三门峡" : "BDA00000111",
    "小浪底" : "BDA00000121",
    "西霞院" : "BDA00000171",
    "河口村" : "BDA00000761",
    "故县" : "BDA80000661",
    "陆浑" : "BDA80200721",
    "东平湖" : "BDD11000012"
}

def get_token() -> str:
    url = f'{BASE_URL}/oauth/login'
    payload = json.dumps({
        "accessKey": "test",
        "secretKey": "8f5ad4b447f0e23a2f47154481ec8187"
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    return json.loads(response.text)['data']

@register_tools
def get_capacity_curve(
    ennm: Annotated[str, '水库名称，例如：龙羊峡或者龙羊峡水库', True]
):
    """ 
    根据水库名称查询水库库容、水位曲线、水库库容曲线、库容与水位关系，库容变化趋势等；
    
    Args:
        ennm: 水库名称，例如：龙羊峡或者龙羊峡水库
    return:
        data: List
    """

    '''参数匹配'''
    if "水库" in ennm:
        ennm = ennm.replace('水库', '')

    if ennm not in RESERVOIR_DICT.keys():
        raise f"{ennm}水库不存在"
    ennmcd = RESERVOIR_DICT.get(ennm)

    headers = {
        "Content-Type": "application/json",
        "Authorization": get_token()
    }
    params = {"resname": ennmcd}

    url = f'{BASE_URL}/project/resvzv/list'
    response = requests.get(url, headers=headers, params=params)
    data = json.loads(response.text)['data']

    if len(data) == 0:
        raise f"{ennm}水库数据暂未获取"
    
    return data

@register_tools
def get_history_features(
    ennm: Annotated[str, '水库名称，例如：龙羊峡或者龙羊峡水库', True],
    start_year: Annotated[int, '查询年份，格式：%Y', False] = None,
    end_year: Annotated[int, '查询年份，格式：%Y', False] = None
):
    """
    根据水库名称和年份时间范围内查询水库历史特征、水库极值特征、库容极值、最大出库、最大入库等；
    例如：最高水位、最大出库、最大入库发生在什么时候？
    开始年份和结束年份，例如：2020-2024最高水位，最大出库，最大入库等。
    最近5年的最大水位数据，对应查询时间范围为2020-2024
    最近三年的最大出库流量，对应查询时间范围为2022-2024
    
    Args:
        ennm: 水库名称，例如：龙羊峡或者龙羊峡水库
        start_year: 开始年份，例如：%Y，为空则查询最近5年的数据
        end_year: 结束年份，例如：%Y，为空则查询最近5年的数据
    return:

    """
    
    if "水库" in ennm:
        ennm = ennm.replace('水库', '')

    if ennm not in RESERVOIR_DICT.keys():
        return f"{ennm}水库不存在"
    ennmcd = RESERVOIR_DICT.get(ennm)

    if not isinstance(start_year, int):
        start_year = None
    if not isinstance(end_year, int):
        end_year = None

    headers = {
        "Content-Type": "application/json",
        "Authorization": get_token()
    }
    params = {"resname": ennmcd}

    url = f'{BASE_URL}/hydrometric/resv/selectResMaxInfo'
    response = requests.get(url, headers=headers, params=params)
    data: List = json.loads(response.text)['data']

    if len(data) == 0:
        raise f"{ennm}水库数据暂未获取"

    if start_year is None:
        return data[:5]
    if start_year is not None and end_year is None:
        return [d for d in data if d['year'] == start_year]
    if start_year is not None and end_year is not None:
        return [d for d in data if d['year'] >= start_year and d['year'] <= end_year]
    

@register_tools
def get_reservoir_characteristics(
    ennm: Annotated[str, '水库名称，例如：龙羊峡或者龙羊峡水库', True]
) -> str:
    """ 
    根据水库名称查询水库信息，水库特性等
    水库特性是指描述水库特征和功能的一些关键参数和水位设定，可能包括水库类型与位置、库容与规模、特征水位等参数。
    包括“水库特性”、“水库特征”、“水库信息”、“介绍xx水库”、“水库参数”、“特征水位”、“水库类型”、“水库任务”等关键词
    """
    
    if "水库" in ennm:
        ennm = ennm.replace('水库', '')

    if ennm not in RESERVOIR_DICT.keys():
        raise f"{ennm}水库不存在"
    ennmcd = RESERVOIR_DICT.get(ennm)

    headers = {
        "Content-Type": "application/json",
        "Authorization": get_token()
    }
    params = {"resname": ennmcd}

    url = f'{BASE_URL}/project/resv/get'
    response = requests.get(url, headers=headers, params=params)
    data = json.loads(response.text)['data']

    if len(data) == 0:
        raise f"{ennm}水库数据暂未获取"
    
    return data


@register_tools
def get_realtime_water_condition(
    ennm: Annotated[str, '水库名称', True],
    startDate: Annotated[str, '开始时间，%Y-%m-%d 00:00:00', False] = None,
    endDate: Annotated[str, '结束时间，%Y-%m-%d 00:00:00', False] = None
) -> str:
    """
    根据水库名称和时间查询水库“水情”、“水位”、“流量”、“蓄量”、“蓄水量”等信息
    查询xx水库/地区水情时，调取对应的水位、入库流量、出库流量、蓄量数据，
    例如：龙羊峡水库今天水位为多少，实时水情怎么样？
    
    Args:
        ennm: 水库名称，例如：龙羊峡或者龙羊峡水库
        startDate: 开始时间，格式：%Y-%m-%d 00:00:00,可以为空
        endDate: 结束时间，例如：%Y-%m-%d 00:00:00,可以为空
    """
    logger.info(f"**kwargs**:{ennm} {startDate}, {endDate}")
    '''参数匹配'''
    if "水库" in ennm:
        ennm = ennm.replace('水库', '')
    startDate = '' if startDate is None else startDate
    
    if ennm not in RESERVOIR_DICT.keys():
        raise f"{ennm}水库不存在"
    ennmcd = RESERVOIR_DICT.get(ennm)

    headers = {
        "Content-Type": "application/json",
        "Authorization": get_token()
    }
    startDate = '' if startDate is None else startDate
    endDate = '' if endDate is None else endDate

    params = {
        "resname": ennmcd,
        "startDate": startDate,
        "endDate": endDate
    }

    url = f'{BASE_URL}/hydrometric/rhourrt/list'
    response = requests.get(url, headers=headers, params=params)
    data = json.loads(response.text)['data']

    if len(data) == 0:
        raise f"{ennm}水库数据暂未获取"
    
    if startDate is None and endDate is None:
        dates = [datetime.fromtimestamp(d['date'] / 1000) for d in data]
        from bisect import bisect_left, bisect_right
        start = datetime.strftime(startDate, '%Y-%m-%d %H:%M:%S')
        end = datetime.strftime(endDate, '%Y-%m-%d %H:%M:%S')

        start_index = bisect_left(dates, start)
        end_index = bisect_right(dates, end)

        return data[start_index:end_index]

    return data[-7:]


@register_tools
def get_position(
    ennm: Annotated[str, '水库名称', True],
):
    """
    根据水库名称查询水库位置，经纬度坐标等
    
    Args:
        ennm: 水库名称，例如：龙羊峡或者龙羊峡水库
    """
    return {"ennm" : ennm}

@register_tools
def get_water_rain(
    ennm: Annotated[str, '水库名称', True],
    startDate: Annotated[str, '开始时间，%Y-%m-%d 00:00:00', True] = None,
    endDate: Annotated[str, '结束时间，%Y-%m-%d 23:59:59', True] = None
) -> str:
    """
    根据水库名称和时间查询降水等值线数值，降水量空间分布特征，降雨等值线图等
    """
    
    return {
        "ennm" : ennm,
        "startDate" : startDate,
        "endDate" : endDate
    }
