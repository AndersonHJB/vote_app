# -*- coding: utf-8 -*-
# @Time    : 2024/12/6 21:22
# @Author  : AI悦创
# @FileName: json_opt.py
# @Software: PyCharm
# @Blog    ：https://bornforthis.cn/
# code is far away from bugs with the god animal protecting
#    I love animals. They taste delicious.
import json
import uuid

# 修改 poll_data.json 数据以适配新的结构
poll_data_path = "poll_data.json"

# 读取现有 poll_data.json 数据
with open(poll_data_path, "r", encoding="utf-8") as file:
    poll_data = json.load(file)

# 更新 poll_data.json 格式，增加链接后缀（默认使用 UUID）
updated_poll_data = {}
for group_name, categories in poll_data.items():
    group_suffix = str(uuid.uuid4())  # 默认使用 UUID 作为后缀
    updated_poll_data[group_name] = {
        "suffix": group_suffix,
        "categories": categories
    }

# 保存更新后的 poll_data.json
with open(poll_data_path, "w", encoding="utf-8") as file:
    json.dump(updated_poll_data, file, ensure_ascii=False, indent=4)

# 确认更新后的结构
updated_poll_data
