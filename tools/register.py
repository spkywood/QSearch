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
import httpx
import inspect
from collections import OrderedDict
from types import GenericAlias
from typing import get_origin, Annotated, Dict
import requests

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
        raise RuntimeError(f"Tools `{tool_name}` not defined")
    
    tool_call = _TOOL_HOOKS[tool_name]
    try:
        ret = tool_call(**json.loads(kwargs))
    except:
        raise RuntimeError(f"Tools `{tool_name}` Call error")
    return ret

@register_tools
def get_weather(
    city: Annotated[str, '城市名', True],
) -> str:
    """
    Get the weather for `city`.
    """
    
    if not isinstance(city, str):
        raise TypeError("City must be a string")
    
    return "Sunny"

@register_tools
def get_flight_number(
    date: Annotated[str, '出发日期', True], 
    departure: Annotated[str, '出发地', True], 
    destination: Annotated[str, '目的地', True]
) -> Dict[str, str]:
    """
    根据始发地、目的地和日期，查询对应日期的航班号
    """
    
    flight_number = {
        "北京":{
            "上海" : "1234",
            "广州" : "8321",
        },
        "上海":{
            "北京" : "1233",
            "广州" : "8123",
        }
    }
    return { "flight_number":flight_number[departure][destination] }

@register_tools
def get_ticket_price(
    date: Annotated[str, '日期', True] , 
    flight_number: Annotated[str, '航班号', True]
) -> Dict[str, str]:
    """
    查询某航班在某日的票价
    """

    return {"ticket_price": "1000"}


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
    ennm: Annotated[str, '水库名称', True]
):
    """ 
    根据水库名称查询水库库容曲线
    """
    if ennm not in RESERVOIR_DICT.keys():
        return f"{ennm}水库不存在"
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
        return f"{ennm}水库数据暂未获取"

    '''绘制图像'''
    from pylab import mpl
    import matplotlib.pyplot as plt
    from matplotlib.ticker import AutoLocator, MaxNLocator 

    # 设置中文字体
    mpl.rcParams['font.family']= "SimHei"      
    mpl.rcParams['axes.unicode_minus']=False
    # 提取横坐标和纵坐标
    capacities = [d['capactiy'] for d in data]
    levels = [d['level'] for d in data]

    # 绘制曲线
    x0 = len(capacities) if len(capacities) <= 20 else 20
    plt.figure(figsize=(x0 if x0 > 8 else 12, 8))
    plt.plot(capacities, levels, marker='o')
    # 在曲线上标注数值
    for i, level in enumerate(levels):
        plt.annotate(f"{level} m", (capacities[i], levels[i]), textcoords="offset points", xytext=(0,10), ha='center')

    start = int(min(levels))
    end = int(max(levels))
    a = int(int(end - start)/6)
    for i in range(start, end, a):
        plt.axhline(y=i, color='#D3D3D3', linestyle='--', linewidth=1, label=f'y={i}')

    plt.fill_between(capacities, levels, y2=start, color='#1E90FF', alpha=0.1)
    # 设置标题和坐标轴标签
    plt.title(f'{ennm}水库库容与水位关系曲线')
    plt.xlabel(r'库容 (m$^{{\scr 3}}$)')
    plt.ylabel('水位 (m)')
    plt.tight_layout()  # 自动调整参数，使图像各元素位置不重叠
    # 设置横坐标步长
    plt.xticks(capacities)
    # 显示网格
    plt.grid(False)
    # 显示图表
    # plt.show()
    
    plt.savefig(f'demo/data/result/{ennm}.png')
    return 



