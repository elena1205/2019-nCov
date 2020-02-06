'''
@Author: your name
@Date: 2020-02-04 19:14:36
@LastEditTime : 2020-02-06 12:13:04
@LastEditors  : Please set LastEditors
@Description: In User Settings Edit
@FilePath: /echarts/2019-nCov.py
'''
from pyecharts import options as opts
from pyecharts.charts import Map, Page, Bar, Grid, Geo, Line
import requests
from bs4 import BeautifulSoup
import re
import json

url = 'https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_pc_3'
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
}

class nCovProvinceInfo():
    def __init__(self, province, jsondata):
        self.province = province
        self.jsontext = jsondata
        self.city_attr = []
        self.city_value = []
        self.pieces = [
            {'min':1, 'max':9},
            {'min':10, 'max':19},
            {'min':20, 'max':29},
            {'min':30, 'max':39},
            {'min':40, 'max':49},
        ]

    def getProvinceList(self):
        provincelist = {}
        if self.jsontext != None:
            print("page title:", self.jsontext["page"]["title"])
            component = self.jsontext['component'][0]
            print("componet title:", (component["title"]))
            caselist = component["caseList"]
            print("provincelist len:", len(caselist))

            for province in caselist:
                provincelist[province["area"]] = province

        return provincelist

    def getProvinceInfo(self):
        provincelist = self.getProvinceList()
        return provincelist[self.province]

    def getProvinceCityList(self):
        citylist = {}
        provinceinfo = self.getProvinceInfo()
        if provinceinfo != None:
            sublist = provinceinfo["subList"]
            for city in sublist:
                citylist[city["city"]] = city
        
        return citylist

    def getProvinceCityInfo(self):
        citylist = self.getProvinceCityList()
        subfix = ''
        for (k,v) in citylist.items():
            if self.province not in ['北京','天津','上海', '重庆']:
                subfix = '市' 
            if v['confirmed'] != '':
                self.city_value.append(int(v['confirmed']))
            # self.city_value.append(v['confirmed'])
            self.city_attr.append(k + subfix)
            # self.pieces.append({'min':min(self.city_value), 'max':max(self.city_value)})

        print(self.city_attr)
        print(self.city_value)

    def drawProvinceMap(self) -> Map:
        mymap = (
            Map()
                .add(self.province, [list(z) for z in zip(self.city_attr, self.city_value)], self.province)
                .set_series_opts(label_opts=opts.LabelOpts())
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=self.province + "肺炎确诊病例"),
                    visualmap_opts=opts.VisualMapOpts(is_piecewise=True, pieces=self.pieces)
                )
        )
        return mymap

    def drawProvinceBar(self) -> Bar:
        mybar = (
            Bar()
                .add_xaxis(self.city_attr)
                .add_yaxis("病例数", self.city_value, label_opts=opts.LabelOpts(position="right"))
                .reversal_axis()
                .set_global_opts(title_opts=opts.TitleOpts(title=self.province + "肺炎确诊病例"))
        )
        return mybar

    def drawProvinceLine(self) -> Line:
        myline = (
            Line()
                .add_xaxis(self.city_attr)
                .add_yaxis("bingli", self.city_value)
        )
        return myline

def getUrlData(url, header):
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        htmldata = response.content.decode()
        bf = BeautifulSoup(htmldata, features='html.parser')
        # print(htmldata)
        data = bf.select('html script')
        for each in data:
            # print('--------------------------------')
            if each.get_text().find('V.conf') != -1 and each.get_text().find('newpneumonia') != -1:
                for i in (each.get_text().split(";")):
                    if i.find("V.conf") != -1:
                        # print(i.split(" = ")[1])
                        jsontext = json.loads(i.split(" = ")[1])
                        break
    
    return jsontext


if __name__ == "__main__":
    jsontext = getUrlData(url, header)

    hebeiInfo = nCovProvinceInfo("北京", jsontext)
    hebeiInfo.getProvinceCityInfo()
    
    mypage = Page()
    mypage.add(
        hebeiInfo.drawProvinceMap(),
        hebeiInfo.drawProvinceBar(),
        hebeiInfo.drawProvinceLine()
    )
    
    mypage.render()
    

    

    




