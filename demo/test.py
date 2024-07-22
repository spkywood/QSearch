import json
import os
import random
from datetime import datetime, timedelta

FILE_PATH = '/home/wangxh/workspace/QSearch/demo/data/水库实时水情'
files = [os.path.join(FILE_PATH, f) for f in os.listdir(FILE_PATH)]

for file_path in files:
    # Load the JSON file
    # file_path = "/mnt/data/sample.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Filter out entries that are not at 8:00:00 AM
    filtered_data = [entry for entry in data if datetime.fromtimestamp(entry["date"] / 1000).time() == datetime.strptime("08:00:00", "%H:%M:%S").time()]

    # 确保所有记录都有完整字段
    required_fields = ["date", "ennm", "ennmcd", "inflow", "level", "outflow", "wq"]
    
    inflow = [e['inflow'] for e in filtered_data if 'inflow' in e and e['inflow'] != 0]
    outflow = [e['outflow'] for e in filtered_data if 'outflow' in e and e['outflow'] != 0]
    if inflow == []:
        inflow = [round(random.uniform(0, 100), 2) for _ in range(100)]
    if outflow == []:
        outflow = [round(random.uniform(0, 100), 2) for _ in range(100)]
    for entry in filtered_data:
        if entry['inflow'] == 0:
            entry['inflow'] = random.choice(inflow)
        if entry['outflow'] == 0:
            entry['outflow'] = random.choice(outflow)
        for field in required_fields:
            if field not in entry:
                if field == 'inflow':
                    entry[field] = random.choice(inflow)
                elif field == 'outflow':
                    entry[field] = random.choice(outflow)
                # entry[field] = random.choice([e[field] for e in filtered_data if field in e and e[field] != 0])
                # if field in ["inflow", "outflow"]:
                #     entry[field] = random.choice([e[field] for e in filtered_data if field in e])
                # else:
                #     entry[field] = None

    # Create a set of all dates from the start date to today
    start_date = datetime.fromtimestamp(filtered_data[0]["date"] / 1000).date()
    end_date = datetime.today().date()
    all_dates = set(start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))

    # Create a set of dates that are present in the filtered data
    present_dates = set(datetime.fromtimestamp(entry["date"] / 1000).date() for entry in filtered_data)

    # Find missing dates
    missing_dates = all_dates - present_dates

    # Randomly select existing entries to fill missing dates
    random.seed(100)
    new_entries = []
    for missing_date in missing_dates:
        template_entry = random.choice(filtered_data)
        new_entry = template_entry.copy()
        new_entry["date"] = int(datetime.combine(missing_date, datetime.strptime("08:00:00", "%H:%M:%S").time()).timestamp() * 1000)
        new_entries.append(new_entry)

    # Combine filtered data with new entries
    complete_data = filtered_data + new_entries
    complete_data.sort(key=lambda x: x["date"])

    # Save the result to a new JSON file
    # output_file_path = "/mnt/data/complete_data.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(complete_data, file, ensure_ascii=False, indent=4)



# # 获取所有日期集合
# start_date = datetime.fromtimestamp(filtered_data[0]["date"] / 1000).date()
# end_date = datetime.today().date()
# all_dates = set(start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))

# # 获取已存在日期集合
# present_dates = set(datetime.fromtimestamp(entry["date"] / 1000).date() for entry in filtered_data)

# # 找出缺失的日期
# missing_dates = all_dates - present_dates

# # 随机选择现有记录来补充缺失的日期
# new_entries = []
# for missing_date in missing_dates:
#     template_entry = random.choice(filtered_data)
#     new_entry = template_entry.copy()
#     new_entry["date"] = int(datetime.combine(missing_date, datetime.strptime("08:00:00", "%H:%M:%S").time()).timestamp() * 1000)
#     new_entries.append(new_entry)

# # 合并过滤后的数据和新记录
# complete_data = filtered_data + new_entries
# complete_data.sort(key=lambda x: x["date"])

# # 保存结果到新 JSON 文件
# output_file_path = "path/to/your/complete_data.json"
# with open(output_file_path, "w", encoding="utf-8") as file:
#     json.dump(complete_data, file, ensure_ascii=False, indent=4)
