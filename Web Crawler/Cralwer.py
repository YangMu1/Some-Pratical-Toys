#!/usr/bin/python
#coding:utf-8

'''
@version 0.1
@date 2016-04-4
@author yangmu
'''

'''
本程序是在开发电影票房预测系统中,使用python进行web网页爬虫的一个demo
爬取的网站是预告片网站的2015年和2016年的预告片电影信息
对应的url链接为:http://www.yugaopian.com/movlist/___pubtime_
'''

import json
import urllib2
import socket
import sys, os
import time
import datetime
import re
from BeautifulSoup import BeautifulSoup


def CalculateLastNDate(n):
    n_days_ago = (datetime.datetime.now() - datetime.timedelta(days = n))
    result_form = n_days_ago.strftime("%Y%m%d")
    return result_form

def getMovieslist(year, results):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    url = 'http://www.yugaopian.com/movlist/__' + str(year) + '_pubtime_'
    preUrl = 'http://www.yugaopian.com'


    flag = True
    flag_end = True
    while flag:
        flag = False
        for j in range(0, 5):
            time.sleep(30)
            try:
                fd = urllib2.urlopen(url)
                pageData = fd.read()

                soup = BeautifulSoup(pageData)
                data = soup.findAll('li', {'class':"show-movtip"})
                for mdata in data:
                    mname = mdata['data-name']
                    mtime = mdata['data-pubdate']
                    if mtime < today:
                        flag_end = False
                        break
                    murl = 'http://www.yugaopian.com' + mdata.a['href']
                    item = {'mtime': mtime, 'murl': murl, 'yugaopian': {}}
                    results[mname]=item

                data = soup.findAll('li', {'class':"last show-movtip"})
                for mdata in data:
                    mname = mdata['data-name']
                    mtime = mdata['data-pubdate']
                    if mtime < today:
                        flag_end = False
                        break
                    murl = 'http://www.yugaopian.com' + mdata.a['href']
                    item = {'mtime': mtime, 'murl': murl, 'yugaopian': {}}
                    results[mname]=item

                if not flag_end:
                    flag = False
                    break

                datalist = soup('p', {'class':'page-nav'})
                for item in datalist:
                    link_list = item('a')
                    for it in link_list:
                        if '下一页' in it.getText():
                            flag = True
                            url = preUrl + it['href']
                            break
                break
            except Exception, e:
                print e

def getMovieDetail(year, results):
    for key in results:
        murl = results[key]['murl']
        mname = key
        for n in range(0, 5):
            time.sleep(30)
            try:
                fd = urllib2.urlopen(murl)
                pageData = fd.read()

                yugaopian_info = {}
                yugaopian_info['YugaopianNum'] = ['0']
                yugaopian_info['YugaopianPlayNum'] = ['0']
                yugaopian_info['YugaopianPlayNumList'] = ['-']
                yugaopian_info['YugaopianPlayDateList'] = ['-']
                yugaopian_info['HuaxuNum'] = ['0']
                yugaopian_info['HuaxuPlayNum'] = ['0']
                yugaopian_info['HuaxuPlayNumList'] = ['-']
                yugaopian_info['HuaxuPlayDateList'] = ['-']

                soup = BeautifulSoup(pageData)

                ### get total vedio num ###
                #<h4 class="list-subtitle">预告片<span>(40)</span></h4>
                #<h4 class="list-subtitle">片段和花絮<span>(39)</span></h4>
                vedio_num_list = soup('h4', {'class':'list-subtitle'})
                vedio_num_list += soup('h3', {'class':'list-title'})
                yugaopian_num = 0
                huaxu_num = 0
                for vedio_num_item in vedio_num_list:
                    vedio_num_text = vedio_num_item.getText('\t').encode('utf-8')
                    vedio_num_list = re.findall('\d+', vedio_num_text)
                    if len(vedio_num_list) > 0:
                        if vedio_num_text.find("预告片") >= 0:
                            yugaopian_num = int(vedio_num_list[0])
                        elif vedio_num_text.find("花絮") >= 0:
                            huaxu_num = int(vedio_num_list[0])

                ### get vedio play num ###
                #<table class="tlist">
                vedio_list = soup('table', {'class':'tlist'})
                vedio_list_len = len(vedio_list)
                #print "vedio_list_len:" + str(vedio_list_len)

                cur_year = year

                total_play_num_list = []
                play_num_list = []
                play_date_list = []
                for i in range(vedio_list_len):
                    play_num = 0
                    tmp_play_num_list = []
                    tmp_play_date_list = []
                    contents_num = len(vedio_list[i].contents)
                    for j in range(contents_num):
                        sub_contents_num = len(vedio_list[i].contents[j])
                        if sub_contents_num < 2:
                            continue
                        play_date = "-"
                        for k in range(sub_contents_num):
                            if k == 1:
                                play_date = vedio_list[i].contents[j].contents[k].getText()
                                if play_date.find("-") == 2:
                                    play_date = cur_year + "-" + play_date
                            elif k == 5:
                                play_text_array = vedio_list[i].contents[j].contents[k].getText('\t').encode('utf-8').split('\t')
                                if (len(play_text_array) == 2) and (play_text_array[0] == "播放"):
                                    play_num += int(play_text_array[1])
                                    tmp_play_date_list.append(play_date)
                                    tmp_play_num_list.append(play_text_array[1])
                    total_play_num_list.append(play_num)
                    play_num_list.append(tmp_play_num_list)
                    play_date_list.append(tmp_play_date_list)

                ### yugaopian_num ###
                if yugaopian_num > 0:
                    yugaopian_info['YugaopianNum'][0] = str(yugaopian_num)
                    if len(total_play_num_list) > 0:
                        yugaopian_info['YugaopianPlayNum'][0] = str(total_play_num_list[0])
                        yugaopian_info['YugaopianPlayNumList'] = play_num_list[0]

                        YugaopianPlayDateList_1 = []
                        for item1 in play_date_list[0]:
                            if '月' in item1:
                                tmp = year + '年' + item1
                                YugaopianPlayDateList_1.append(tmp)
                            elif len(item1) == 10:
                                tmp = item1[0: 4] + '年' + item1[5: 7] + '月' + item1[8: 10] + '日'
                                YugaopianPlayDateList_1.append(tmp)
                            else:
                                YugaopianPlayDateList_1.append(item1)

                        yugaopian_info['YugaopianPlayDateList'] = YugaopianPlayDateList_1
                ### huaxu_num ###
                if huaxu_num > 0:
                    yugaopian_info['HuaxuNum'][0] = str(huaxu_num)
                    if len(total_play_num_list) > 1:
                        yugaopian_info['HuaxuPlayNum'][0] = str(total_play_num_list[1])
                        yugaopian_info['HuaxuPlayNumList'] = play_num_list[1]

                        HuaxuPlayDateList_1 = []
                        for item1 in play_date_list[1]:
                            if '月' in item1:
                                tmp = year + '年' + item1
                                HuaxuPlayDateList_1.append(tmp)
                            elif len(item1) == 10:
                                tmp = item1[0: 4] + '年' + item1[5: 7] + '月' + item1[8: 10] + '日'
                                HuaxuPlayDateList_1.append(tmp)
                            else:
                                HuaxuPlayDateList_1.append(item1)

                        yugaopian_info['HuaxuPlayDateList'] = HuaxuPlayDateList_1

                results[key]['yugaopian'] = yugaopian_info

                print '电影名:' + mname

                break
            except Exception, e:
                print e


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    socket.setdefaulttimeout(20)

    yearlist = ['2015', '2016']

    results = {}
    for year in yearlist:
        getMovieslist(year, results)
        getMovieDetail(year, results)

    sys.exit(0)
