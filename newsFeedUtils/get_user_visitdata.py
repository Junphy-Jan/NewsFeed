import json
import datetime
import pandas as pd


visit_data = {"Prolific ID": [], "NewsSeq": [], "文章ID": [], "startTime": [], "endTime": [], "duration": [],
              "rawData": [], "channel": []}

with open("../attachment/statisticalData.json", "r") as f:
    data = json.load(f)
date_format = "%Y-%m-%d %H:%M:%S"

for d in data:
    for vd in d["visitData"]:
        visit_data["Prolific ID"].append(d["uid"])
        visit_data["NewsSeq"].append(d["newsSeq"])
        visit_data["文章ID"].append(vd["newsId"])
        visit_data["startTime"].append(vd["startTime"])
        visit_data["endTime"].append(vd["endTime"])
        s_time = datetime.datetime.strptime(vd["startTime"], date_format)
        if vd["endTime"] is not None:
            e_time = datetime.datetime.strptime(vd["endTime"], date_format)
            visit_data["duration"].append((e_time - s_time).seconds)
        else:
            visit_data["duration"].append(None)
        visit_data["rawData"].append(vd)
        visit_data["channel"].append(d["channel"])

df = pd.DataFrame.from_dict(visit_data)
df.to_excel("../attachment/用户看文章顺序表_v2.xlsx")

