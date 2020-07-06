# -*- coding: utf-8 -*-
#   网易buff爬虫

import requests
import re
import time
import numpy as np
import pandas as pd
import csv


# # 写入文档
# with open('./origin_page.html', 'w', encoding='utf-8') as fp:
#     fp.write(html_text0)
sleeptime = 1
def initialization():   # 初始化头信息即cookies
    global headers
    global cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    }
    # cookie
    cookie_str = r'Device-Id=xLoPYA08mzx1RcfxWgJ7; Locale-Supported=zh-Hans; game=csgo; _ga=GA1.2.308981242.1590934310; _gid=GA1.2.1199922105.1591931691; NTES_YD_SESS=ibf9I12bOgxvKCyxN2P3JoQtaAcvZGsJXKGNOEdpOTkD5CnFOwbg6tpHCs4mpmrOfn3nyBCzmupp1Xja1RhK1BkZRbFbI.5zzW.kjFHpMfDXjiFRh0664TPZynx.teVt43efjkfBDzsGdK9WE4cCONux_NiUXwAJYKH67Ni5EPG2ypuWiHwHwY1dCFUEWQ4lR2U42gbXpQscfik7gAAdLCxxA8gg1V8aOxu71AI_usoRq; S_INFO=1591931716|0|3&80##|18588891371; P_INFO=18588891371|1591931716|1|netease_buff|00&99|null&null&null#CN&null#10#0|&0|null|18588891371; session=1-XJCjTQFMSIgRQUkgJTN9xoP1nvWaLC0KpoJ8E9M-A5N62043038656; _gat_gtag_UA_109989484_1=1; csrf_token=IjQxZTQ3MTFhZmE5M2QwMzU1MWFkYmViN2IzYTQwMjExODA4NzY3ZjUi.EcSFQg.StET4McSLh1iM2IH1Gkjpq2Pwe0'
    cookies = {}
    for line in cookie_str.split(';'):
        key, value = line.split('=', 1)
        cookies[key] = value
def get_category(): # 获取category
    global category_list
    # Buff csgo武器页面源代码
    source_page_url = "https://buff.163.com/market/?game=csgo#tab=selling&page_num=1"
    cat_response = requests.get(url=source_page_url, headers=headers, cookies=cookies)
    html_text0 = cat_response.text
    # 找出各个武器种类
    category_list = re.findall( r'li value="weapon_(.+?)">', html_text0, re.M)
    for i in range(len(category_list)):
        category_list[i] = "weapon_" + category_list[i]
def decode_pages(): # 解析网页
    # 物品名字
    names_list = []
    # 物品价格
    price_list = []
    # id
    id_list = []
    # 指定蝴蝶刀界面“https://buff.163.com/market/?game=csgo#tab=selling&page_num=1&category=weapon_knife_butterfly”
    root_url = 'https://buff.163.com/api/market/goods?game=csgo&'
    for i in range(len(category_list)):
        # 获取不同物件名称
        # 标准url：https://buff.163.com/api/market/goods?game=csgo&page_num=1&category=weapon_knife_butterfly
        category_url = "&category=" + category_list[i]
        first_url = 'https://buff.163.com/api/market/goods?game=csgo&page_num=1' + category_url
        # 获取单一物件的总页码
        page_response = requests.get(url=first_url, headers=headers, cookies=cookies)
        html_text1 = page_response.text
        page_num_list = re.findall(r'"total_page": (.*)', html_text1, re.M)
        page_num = page_num_list[0]
        time.sleep(sleeptime)
        # 获取单一物件每一页的信息
        for page in range(1, int(page_num) + 1):
            time.sleep(sleeptime)
            page_str = 'page_num=' + str(page)
            # 合并成新的url
            url = root_url + page_str + category_url
            detail_response = requests.get(url=url, headers=headers, cookies=cookies)
            html_text2 = detail_response.text
            # 获取名字和价格
            names_list_temp = re.findall(r'"market_hash_name": "(.*)",', html_text2, re.M)
            price_list_temp = re.findall(r'"sell_min_price": "(.*)",', html_text2, re.M)
            id_list_temp = re.findall(r'"id": (.*),', html_text2, re.M)
            # 异常处理
            if names_list_temp == [] or price_list_temp == [] or id_list_temp == []:
                lost_page = page
                lost_catergory = category_list[i]
                lost_text = "Lost in page:" + str(lost_page) + "of category:" + lost_catergory
                with open('wrong.txt', 'w', encoding='utf-8') as fp:
                    fp.write(lost_text)
                return 0
            names_list = names_list + names_list_temp
            price_list = price_list + price_list_temp
            id_list = id_list + id_list_temp
    # 汇合信息写成表格并保存
    csv_name = ["id","name","price"]
    csv_data = zip(id_list,names_list,price_list)
    items_information = pd.DataFrame(columns=csv_name, data=csv_data)
    items_information.to_csv("items_information.csv")
def boxes_sorting():
    with open('items_information.csv', 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
    temp_dic = {}
    main_dic = {}
    # 处理行信息
    for row in result:
        temp_dic[row[1]] = [row[2], row[3]]
    for key in temp_dic.keys():
        if '\\u2605' not in temp_dic[key][0]:
            main_dic[key] = temp_dic[key]
    # 崭新出厂
    fac_new_dic = {}
    for key in main_dic.keys():
        if 'Factory New' in main_dic[key][0]:
            fac_new_dic[key] = main_dic[key]
    fac_new_all_dic = fac_new_dic
    # statTrack
    fac_new_dic = {}
    fac_new_st_dic = {}
    for key in fac_new_all_dic.keys():
        if 'StatTrak\\u2122' in fac_new_all_dic[key][0]:
            fac_new_st_dic[key] = fac_new_all_dic[key]
        else:
            fac_new_dic[key] = fac_new_all_dic[key]
    standard_url = "https://buff.163.com/market/goods?goods_id=39954&from=market"
    root_url = "https://buff.163.com/market/goods?goods_id="
    tail_url = "&from=market"
    box_sort_dic = {}
    items_type = ["消费", "工业", "军规", "受限", "保密", "隐秘"]

    for id in list(fac_new_all_dic.keys()):
        time.sleep(sleeptime)
        sort_url = root_url + id + tail_url
        sort_response = requests.get(url=sort_url, headers=headers, cookies=cookies)
        html_text4 = sort_response.text
        # 找出各个武器的中文名字
        chinese_list = re.findall(r'<head><title>(.*?)_CS:GO饰品交易', html_text4, re.M)
        # 找出所属箱子
        box_list = re.findall(r',(.*?)收藏品,', html_text4, re.M)
        if box_list == []:
            box_list = re.findall(r',(.*?)collection,', html_text4, re.M)
        # 判断稀有度
        for str in items_type:
            if str in html_text4:
                type_str = str
                break
            else:
                if items_type.index(str) == len(items_type):
                    type_str = "Na"
                    print("type error occurd in id:" + id)
                else:
                    continue
        try:
            if len(box_list[0]) > 19:
                tstr = box_list[0]
                box_list[0] = tstr.split(",")[-1]
        except(IndexError):
            pass
        if box_list == []:
            print("box_list empty occurd in id:" + id)
            box_sort_dic[id] = [chinese_list[0], ["Na"], type_str]
            continue
        box_sort_dic[id] = [chinese_list[0], box_list[0], type_str]
    with open('items_information.csv', 'r', encoding="UTF-8") as f2:
        reader2 = csv.reader(f2)
        result2 = list(reader2)
    temp_dic2 = {}
    for row in result2:
        temp_dic2[row[1]] = [row[2], row[3]]
    for key in box_sort_dic.keys():
        box_sort_dic[key].append(temp_dic2[key][1])

    name = ["id", "Chinese_name", 'belonging', "type", "price"]
    data = zip(list(box_sort_dic.keys()), [x[0] for x in list(box_sort_dic.values())],
               [x[1] for x in list(box_sort_dic.values())]
               , [x[2] for x in list(box_sort_dic.values())], [x[3] for x in list(box_sort_dic.values())])
    items_sorting = pd.DataFrame(columns=name, data=data)
    items_sorting.to_csv("items_sorting.csv")
def get_history_price():
    # AWP 永恒之枪 价格历史标准url
    standard_url = "https://buff.163.com/api/market/goods/price_history/buff?game=csgo&goods_id=776481&currency=CNY&days=90"
    with open('items_information.csv', 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
    id_list = []
    his_dic = {}
    # 处理行信息
    for row in result:
        id_str = row[1]
        id_list.append(id_str)
    id_list.pop(0)

    error_index = []
    # 遍历所有id的历史价格
    for id in id_list:
        time.sleep(sleeptime)
        history_url = "https://buff.163.com/api/market/goods/price_history/buff?game=csgo&goods_id=" + id + "&currency=CNY&days=90"
        history_response = requests.get(url=history_url, headers=headers, cookies=cookies)
        html_text3 = history_response.text
        history_list = re.findall(r'"price_history": (.*)]', html_text3, re.S)
        # 文本处理
        his_str_list = history_list[0].replace(" ", "").replace(",", "").replace("[", "").replace("]", "").split("\n")
        try:
            while True:
                his_str_list.pop(his_str_list.index(""))
        except(ValueError):
            pass
        his_pri = []
        # 处理出历史价格数组
        try:
            for i in range(int(len(his_str_list) / 2)):
                num_temp = his_str_list[2 * i - 1]
                his_pri.append(num_temp)
            temperary = his_pri[0]
            his_pri.pop(0)
            his_pri.append(temperary)
            his_dic[id] = his_pri
        except(IndexError):
            error_index.append(id)
            print("error occurded in id:" + id)
            continue
    np.save("his_pri.npy", his_dic)
def his_pri_analyze():
    dict_load = np.load('his_pri.npy')
    his_pri_dic = dict_load.item()
    id_list = list(his_pri_dic.keys())
    values_list = list(his_pri_dic.values())

    new_dic = {}
    for i in range(len(id_list)):
        for k in range(len(values_list[i])):
            values_list[i][k] = round(int(float(values_list[i][k])), 1)
        max_val = max(values_list[i])
        max_index = values_list[i].index(max_val)
        min_val = min(values_list[i])
        min_index = values_list[i].index(min_val)
        mean_val = round((np.mean(values_list[i])), 1)
        std_val = round((np.std(values_list[i], ddof=1)), 1)
        new_list = [max_val, round(max_index / len(values_list[i]), 2), min_val,
                    round(min_index / len(values_list[i]), 2), mean_val, std_val]
        new_dic[id_list[i]] = new_list

    name = ["id", "max_price", "max_time", "min_price", "min_time", "mean", "std"]
    data = zip(list(new_dic.keys()), [x[0] for x in list(new_dic.values())], [x[1] for x in list(new_dic.values())]
               , [x[2] for x in list(new_dic.values())], [x[3] for x in list(new_dic.values())]
               , [x[4] for x in list(new_dic.values())], [x[5] for x in list(new_dic.values())])
    items_analysation = pd.DataFrame(columns=name, data=data)
    items_analysation.to_csv("items_analysation.csv")

if __name__ == '__main__':
    start_time = time.time()
    initialization()    # 初始化
    get_category()      # 获取目录
    decode_pages()      # 解码页面，获取csv
    boxes_sorting()        # 武器分类
    # get_history_price()   # 获取历史价格
    # his_pri_analyze()     # 分析历史价格（待完善）

    end_time = time.time()
    dtime = end_time-start_time
    print("spending time:"+str(dtime))





