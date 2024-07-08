from typing import Dict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


'''参数规则匹配'''
def get_date_range(kwargs: Dict, question: str) -> Dict:
    fmt = '%Y-%m-%d 00:00:00'
    end_fmt = '%Y-%m-%d 23:59:59'
    if 'startDate' not in kwargs and 'endDate' not in kwargs:
        return kwargs
    import re
    now = datetime.now()
    if r'最近一周' in question:
        endDate = now
        startDate = endDate - timedelta(days=7)
        kwargs.update({'startDate': startDate.strftime(fmt), 'endDate': endDate.strftime(end_fmt)})
        return kwargs
    elif r'上周' in question:
        endDate = now - timedelta(days=now.weekday() + 1)
        startDate = endDate - timedelta(days=6)
        kwargs.update({'startDate': startDate.strftime(fmt), 'endDate': endDate.strftime(end_fmt)})
        return kwargs
    elif match := re.search(r'(\d{1,2}\.\d{1,2})(.*)前后', question):
        date_str = match.group(1)
        description = match.group(2).strip()
        # 解析日期
        try:
            specific_date = datetime.strptime(date_str, "%m.%d")
            specific_date = specific_date.replace(year=datetime.now().year)
            if specific_date > datetime.now():
                specific_date = specific_date.replace(year=datetime.now().year - 1)
            # 计算前后三天的时间范围
            start_date = specific_date - timedelta(days=3)
            end_date = specific_date + timedelta(days=3)

            kwargs.update({'startDate': start_date.strftime(fmt), 'endDate': end_date.strftime(end_fmt)})
            return kwargs
        except ValueError:
            return kwargs
    elif r'上个月' in question:
        endDate = now - timedelta(days=now.day)
        startDate = (now.replace(day=1) - relativedelta(months=1)).replace(day=1)
        endDate = (now.replace(day=1) - relativedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        kwargs.update({'startDate': startDate.strftime(fmt), 'endDate': endDate.strftime(end_fmt)})
        return kwargs
        
if __name__ == '__main__':
    result = get_date_range(
        {'ennm': '小浪底水库', 'startDate': '2023-01-01', 'endDate': '2023-01-31'}, 
        '小浪底水库上个月水位变化如何？'
    )
    print(result)