import requests
import sys
import re
import time
import ffmpy
import os

def down_vd(url, headers):
    try:
        response = requests.get(url=url, headers=headers)
        content = response.text
        name_pattern = re.compile('h1 title="(.*?)"', re.S)
        name = name_pattern.findall(content)[0]
        vid_title = re.sub(r'\W', '', name)
        seq = (vid_title, 'mp4')
        suf = '.'
        zh_name = suf.join(seq)
        #set file name due to the bv
        bv_pattern = r"BV([\w]+)"
        bv_match = re.search(bv_pattern, url)
        bv_num = bv_match.group(1)
        vd_pattern = re.compile('"min_buffer_time".*?"baseUrl":"(.*?)"', re.S)
        vd_url = vd_pattern.findall(content)[0]
        ad_pattern = re.compile('"audio".*"base_url":"(.*?)"', re.S)
        ad_url = ad_pattern.findall(content)[0]
        #then create folder
        down_path = os.path.join(sys.path[0], 'bilibili_video', bv_num)
        if not os.path.exists(down_path):
            os.makedirs(down_path)
        vd_file_name = os.path.join(down_path, '1.mp4').replace('\\', '//')#1 is only mp4
        ad_file_name = os.path.join(down_path, '2.aac').replace('\\', '//')#2 is only aac
        vd_zh_name = os.path.join(down_path, zh_name).replace('\\', '//')
        print('正在分析...')
        response1 = requests.get(url=vd_url, headers=headers)
        size = 0
        chunk_size = 1024
        content_size = int(response1.headers['Content-Length'])
        print('开始下载视频,[视频大小]:{size:.2f} MB'.format(size=content_size / chunk_size / 1024))
        with open(vd_file_name, 'wb') as f:
            for data in response1.iter_content(chunk_size=chunk_size):
                f.write(data)
                size += len(data)
                print(
                    '\r' + '[下载进度]:%s%.2f%%' % ('>' * int(size * 50 / content_size), float(size / content_size * 100)),
                    end='')
        print('\n')
        time.sleep(0.5)
        response2 = requests.get(url=ad_url, headers=headers)
        size = 0
        chunk_size = 1024
        content_size = int(response2.headers['Content-Length'])
        print('开始下载音频,[音频大小]:{size:.2f} MB'.format(size=content_size / chunk_size / 1024))
        with open(ad_file_name, 'wb') as f:
            for data in response2.iter_content(chunk_size=chunk_size):
                f.write(data)
                size += len(data)
                print(
                    '\r' + '[下载进度]:%s%.2f%%' % ('>' * int(size * 50 / content_size), float(size / content_size * 100)),
                    end='')
        print('\n')
        #视频压缩
        vd_360p_name = os.path.join(down_path, '_360p.mp4').replace('\\', '//')
        ff = ffmpy.FFmpeg(
            executable='G:\\cv\\机器学习\\bilividsdown\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe',
            inputs={vd_file_name: None},
            outputs={vd_360p_name: '-s 640x360 -c:v libx264 -b:v 1M -c:a copy'}
        )
        ff.run()
        time.sleep(0.5)
        list_disk = os.listdir(down_path)
        for i in list_disk:
            if i == '1.mp4':
                os.remove(os.path.join(down_path, i))
            #if i == '2.aac':
                #os.remove(os.path.join(down_path, i)) if we need to convert
        time.sleep(0.5)
        print('下载成功...')
        time.sleep(1.5)


    except Exception as e:
        print(e)
        print('Error')
        time.sleep(3)