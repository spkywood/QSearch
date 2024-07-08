import re
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

def get_date_range_from_text(text):
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
    current_year = datetime.now().year
    
    # 匹配正则表达式
    match = pattern.search(text)
    if match:
        try:
            specific_date = get_date_from_match(match, current_year)
            # 计算前后三天的时间范围
            start_date = specific_date - timedelta(days=3)
            end_date = specific_date + timedelta(days=3)
            return {
                "startDate": start_date.strftime('%Y-%m-%d %H:%M:%S'),
                "endDate": end_date.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except ValueError:
            return None
    else:
        return None

# 示例用法
text_list = [
    "2023.6.12暴雨前后，小浪底水库水位和流量有何变化？",
    "2023年6月12号暴雨前后",
    "2023年六月十二号前后",
    "6.12前后",
    "6月12号前后",
    "六月十二"
]

for text in text_list:
    result = get_date_range_from_text(text)
    if result:
       print(result)
    else:
        print(f"无法解析输入文本: {text}")

from datetime import datetime, timedelta

def get_date_range_from_description(description):
    now = datetime.now()
    
    if description == "上一周":
        end_date = now - timedelta(days=now.weekday() + 1)
        start_date = end_date - timedelta(days=6)
    elif description in ["最近一周", "过去一周"]:
        end_date = now
        start_date = now - timedelta(days=7)
    elif description == "上个月":
        first_day_of_this_month = now.replace(day=1)
        end_date = first_day_of_this_month - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif description == "过去三天":
        end_date = now
        start_date = now - timedelta(days=3)
    elif description == "过去五天":
        end_date = now
        start_date = now - timedelta(days=5)
    elif description == "十天前":
        end_date = now - timedelta(days=10)
        start_date = end_date
    else:
        return None

    return start_date, end_date

# 示例用法
descriptions = [
    "上一周",
    "最近一周",
    "过去一周",
    "上个月",
    "过去三天",
    "过去五天",
    "十天前"
]

for description in descriptions:
    result = get_date_range_from_description(description)
    if result:
        start_date, end_date = result
        print(f"描述: {description}")
        print(f"从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    else:
        print(f"无法解析描述: {description}")
