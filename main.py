#todo : simplify
import time
import ffmpy
import os
import urllib3
from get_music_info_2 import get_music_info
from down_vd import down_vd



def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print('超级无敌超级牛逼狂霸酷炫批站下载')
    bv = input('输入BV号:')
    bv_list = bv.split(',')
    # print(bv_list)
    for file in bv_list:
        url = 'https://www.bilibili.com/video/' + file.replace(' ', '')
        headers = {
            'origin': 'https://www.bilibili.com',
            'referer': url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        }
        # print(url.replace(' ', ''))
        down_vd(url, headers)
        get_music_info(url)
    print('下载成功')
    time.sleep(3)

main()