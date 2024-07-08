import re
from typing import Dict
from datetime import datetime, timedelta

def get_date_from_match(match, current_year):
    # 提取年份
    year = match.group('year')
    if year:
        year = int(year)
    else:
        year = current_year
    
    # 提取月份和日期
    month = match.group('month')
    day = match.group('day')
    
    # 转换中文月份
    if '月' in month:
        month = month.replace('月', '')
        if '一' <= month <= '十二':
            month = str(["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"].index(month) + 1)
    
    # 转换中文日期
    if '一' <= day <= '三十一':
        day = str(["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十", "二十一", "二十二", "二十三", "二十四", "二十五", "二十六", "二十七", "二十八", "二十九", "三十", "三十一"].index(day) + 1)
    
    return datetime(year, int(month), int(day))

def get_date_range(kwargs: Dict, question: str, start_fmt: str, end_fmt: str):
    # 定义正则表达式模式
    pattern = re.compile(r'''
        (?:(?P<year>\d{4})[年.\s]*)?                # 年份 (可选)
        (?P<month>\d{1,2}|[一二三四五六七八九十十一十二]+)    # 月份 (数字或中文)
        [月.\s]*
        (?P<day>\d{1,2}|[一二三四五六七八九十十一十二十三十四十五十六十七十八十九二十二十一二十二二十三二十四二十五二十六二十七二十八二十九三十三十一]+) # 日期 (数字或中文)
        [号日]?
        .*                                          # 匹配任意字符（非贪婪模式）
        前后                                         # 匹配“前后”
    ''', re.VERBOSE)
    
    # 获取当前年份
    now = datetime.now()
    current_year = datetime.now().year
    
    # 匹配正则表达式
    match = pattern.search(question)
    if match:
        try:
            specific_date = get_date_from_match(match, current_year)
            # 计算前后三天的时间范围
            start_date = specific_date - timedelta(days=3)
            end_date = specific_date + timedelta(days=3)
            kwargs.update({
                "startDate": start_date.strftime(start_fmt),
                "endDate": end_date.strftime(end_fmt),
            })
            return kwargs
        except ValueError:
            return kwargs
        
    elif "上一周" in question:
        end_date = now - timedelta(days=now.weekday() + 1)
        start_date = end_date - timedelta(days=6)
    elif "最近一周" in question or "过去一周" in question:
        end_date = now
        start_date = now - timedelta(days=7)
    elif "上个月" in question:
        first_day_of_this_month = now.replace(day=1)
        end_date = first_day_of_this_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif "过去三天" in question:
        end_date = now
        start_date = now - timedelta(days=3)
    elif "过去五天" in question:
        end_date = now
        start_date = now - timedelta(days=5)
    elif "十天前" in question:
        specific_date = now - timedelta(days=10)

        # 计算前后三天的时间范围
        start_date = specific_date - timedelta(days=3)
        end_date = specific_date + timedelta(days=3)
        
    else:
        return kwargs

    kwargs.update({
        "startDate": start_date.strftime(start_fmt),
        "endDate": end_date.strftime(end_fmt),
    })
    return kwargs

'''
    def get_date_range(kwargs: Dict, question: str, fmt: str, end_fmt: str) -> Dict:
        if 'startDate' not in kwargs and 'endDate' not in kwargs:
            return kwargs
        import re
        now = datetime.now()
        if r'最近一周' in question:
            endDate = now
            startDate = endDate - timedelta(days=7)
            kwargs.update({'startDate': startDate.strftime(fmt), 'endDate': endDate.strftime(end_fmt)})
            return kwargs
        elif r'上周' in question or r'过去一周' in question:
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
            
'''