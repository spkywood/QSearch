#! python3
# -*- encoding: utf-8 -*-
'''
@File    : register.py
@Time    : 2024/07/01 15:20:50
@Author  : longfellow
@Version : 1.0
@Email   : longfellow.wang@gmail.com
'''


import json
from typing import Dict, List
from datetime import datetime

"""
回复消息模板
"""

def response_template(template: str, **kwargs):
    return template.format(**kwargs)

MESSAGE_TEMPLATE = {
    "get_capacity_curve": "为您查询{}水库库容曲线，结果如下:\n",
}

def generate_capacity_curve(
    data: List
):
    ennm = data[0]['ennm']
    # 提取横坐标和纵坐标
    capacities = [d['capactiy'] for d in data]
    levels = [d['level'] for d in data]

    option = {
        "type": "echarts",
        "content": {
            "title": f"{ennm}水库库容曲线",
            "xAxis": {"name": "库容 (m³)", "data": capacities},
            "yAxis": [
                {"name": "水位（m）"}
            ],
            "series": [
                {"name": '水位',"data": levels}
            ]
        }
    }

    return json.dumps(option, indent=4, ensure_ascii=False)

def format_date(timestamp: str) -> str:
    if timestamp is None:
        return None
    date_time = datetime.fromtimestamp(timestamp / 1000)
    return date_time.strftime('%Y-%m-%d \n %H:%M:%S')

def generate_history_features(
    data: List
):
    ennm = data[0]['ennm']

    template = f"""
<table>
  <caption>{ennm}水库历年特征表</caption>
  <tr>
    <th rowspan='2'>时间</th>
    <th colspan='3'>最高水位</th>
    <th colspan='2'>最大入库</th>
    <th colspan='2'>最大出库</th>
  </tr>
  <tr>
    <td>时间</td>
    <td>水位</td>
    <td>蓄量</td>
    <td>时间</td>
    <td>流量</td>
    <td>时间</td>
    <td>流量</td>
  </tr>
  """
    data.sort(key=lambda x: x['year'], reverse=True)
    for d in data:
        template += f"""
  <tr>
    <td>{d.get('year')}</td>
    <td>{format_date(d.get('ldate'))}</td>
    <td>{d.get('level')}</td>
    <td>{d.get('wq')}</td>
    <td>{format_date(d.get('idate'))}</td>
    <td>{d.get('inflow')}</td>
    <td>{format_date(d.get('odate'))}</td>
    <td>{d.get('outflow')}</td>
  </tr>
"""
    template += "</table>"

    options = {
        "type": "markdown",
        "content": template
    }
    return json.dumps(options, indent=4, ensure_ascii=False)

def generate_reservoir_characteristics(
    data: Dict,
):
    template = f"""
<table>
<caption>{data.get('ennm')}水库特性表</caption>
  <tr>
    <th rowspan='2'>位置</th>
    <th colspan='5'>{data.get('location')}</th>
  </tr>
  <tr>
    <th>上距</th>
    <th colspan='2'>{data.get('upLocation').replace('上距', '').replace('约', '')}</th>
    <th>下距</th>
    <th>{data.get('downLocation').replace('上距', '').replace('约', '')}</th>
  </tr>
  <tr>
    <th>控制面积</th>
    <th colspan='5'>{data.get('basinarea')} km²</th>
  </tr>
  <tr>
    <th>任务</th>
    <th colspan='5'>{data.get('task')}</th>
  </tr>
  <tr>
    <th>历史最高水位</th>
    <th colspan='2'>326.0m</th>
    <th>出现时间</th>
    <th colspan='2'>{data.get('LVL_FLD_CTR_DATE')}</th>
  </tr>
  <tr>
    <th rowspan='6'>特征水位</th>
    <th>防洪高水位</th>
    <th>{data.get('lvlFldMax')} m</th>
    <th>相应库容</th>
    <th colspan='2'>{data.get('capMaxfldlvl')} 亿m³</th>
  </tr>
  <tr>
    <th>正常蓄水位</th>
    <th>{data.get('lvlNormal')} m</th>
    <th>相应库容</th>
    <th colspan='2'>{data.get('capNormallvl')} 亿m³</th>
  </tr>
  <tr>
    <th rowspan='4'>汛限水位</th>
    <th colspan='3'>前汛期</th>
    <th>{data.get('capCtrlvlBe')} m</th>
  </tr>
  <tr>
    <th colspan='3'>防洪库容</th>
    <th>{data.get('capCtrlvlBe')} 亿m³</th>
  </tr>
  <tr>
    <th colspan='3'>后汛期</th>
    <th>380.8m</th>
  </tr>
  <tr>
    <th colspan='3'>防洪库容</th>
    <th>{data.get('capCtrlvlAf')} 亿m³</th>
  </tr>
  <tr>
    <th>过渡期</th>
    <th colspan='5'>{data.get('transtionPeriod')}</th>
  </tr>
</table>
"""
    options = {
        "type": "markdown",
        "content": template
    }
    return json.dumps(options, indent=4, ensure_ascii=False)


def generate_realtime_water_condition(
    data: Dict
) -> str:
    ennm = data[0].get('ennm')

    level = [item.get('level') for item in data]
    inflow = [item.get('inflow') for item in data]
    outflow = [item.get('outflow') for item in data]
    wq = [item.get('wq') for item in data]

    xAxis_data = [format_date(item.get('date')) for item in data]
    
    option = {
        "type": "echarts",
        "content": {
            "title": f"{ennm}水库水情",
            "xAxis": {"name": "时间", "data": xAxis_data},
            "yAxis": [
                {"name": "水位（m）"},
                {"name": "入库流量（m³）"},
                {"name": "出库流量（m³）"},
                {"name": "蓄量（m³）"}
            ],
            "series": [
                {"name": '水位', "data": level},
                {"name": '入库流量', "data": inflow},
                {"name": '出库流量', "data": outflow},
                {"name": '蓄量', "data": wq}
            ]
        }
    }

    return json.dumps(option, ensure_ascii=False, indent=4)


GENERATR_TEMPLATE = {
    "get_capacity_curve": generate_capacity_curve,
    "get_history_features": generate_history_features,
    "get_reservoir_characteristics": generate_reservoir_characteristics,
    "get_realtime_water_condition": generate_realtime_water_condition,
}
