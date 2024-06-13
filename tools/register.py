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
from collections import OrderedDict
from types import GenericAlias
from typing import get_origin, Annotated, Dict

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