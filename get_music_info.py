#2023.8.1 finish basic
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import os
import sys

#todo : 转换播放量用函数
# def convert_views_to_number(views_str):
#     if '万' in views_str:
#         parts = views_str.split('万')
#         num_before_wan = float(parts[0])
#         num_after_wan = float(parts[1]) if parts[1].isdigit() else 0
#         return int((num_before_wan * 10000) + num_after_wan)
#     else:
#         try:
#             return int(views_str)
#         except ValueError:
#             # If the value cannot be converted to an integer, return 0
#             return 0

def get_music_info(url):

    driver = None
    try:
        start_time = time.time()  # 记录开始时间
        # Setting up the driver
        service = Service(executable_path='G:\\cv\\bilibilipa\\chromedriver-win64\\chromedriver.exe')
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)

        #获取网页
        driver.get(url)

        # 实现点击

        button_xpath = "//div[@class='bgm-tag']//div[contains(@class, 'bgm-link')]"
        for i in range(10):  # Repeat the click action 3 times
            button = driver.find_element(By.XPATH, button_xpath)
            button.click()
            time.sleep(0.5)  # Wait for 5 seconds between each click

        # 等待动态元素出现
        wait = WebDriverWait(driver, 30)
        dynamic_content = wait.until(EC.visibility_of_element_located((By.ID, 'bgm-entry')))
        # Extracting the desired information from the dynamic content
        html_content = dynamic_content.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        title_elements = soup.find_all('div', {'class': 'title'})
        if len(title_elements) >= 2:
            title = title_elements[1].text.strip()
        else:
            title = "Not Found"  # 因为这个bgm entry下面第一个title是 音乐详情 第二个title才是音乐
        singer = soup.find('div', {'class': 'singer'}).text.strip()
        album = soup.find('div', {'class': 'des'}).text.strip()
        music_info = f"{title}, {singer}, {album}"
        print("音乐信息：", music_info)

        #获取其他视频信息
        video_list_elements = soup.find_all('div', class_='video-list')[0].find_all('a')
        #获取music video对应链接
        mv_pattern = re.compile(r"https://www.bilibili.com/video/(.+?)/\?p=1")
        # 为0时就是播放量，为1时为标题
        flag = 0
        #判断当前是否要保存
        flag_2 = 0
        video_info_list = []
        for element in video_list_elements:
            href = element.get('href')
            if href:
                match = mv_pattern.match(href)
                if match:
                    bv_number = match.group(1).split('/')[0]
                    title = element.get_text(strip=True)

                    #进行筛选
                    driver.get(href)
                    video_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # 找到对应的tags进行匹配
                    tags_section = video_soup.find('div', class_='tag not-btn-tag')
                    desired_tags = ["音乐"]
                    if tags_section and all(tag in tags_section.get_text() for tag in desired_tags):
                        video_info_list.append((bv_number, title))

        # 将播放量抽离 并转换成数值
        combined_video_info = {}
        for bv_num, title in video_info_list:
            if bv_num not in combined_video_info:
                combined_video_info[bv_num] = {'title': None, 'views': title}
            elif combined_video_info[bv_num]['title'] is None:
                combined_video_info[bv_num]['title'] = title
            else:
                combined_video_info[bv_num]['views'] = title
        #todo: 万转数字
        # for bv_num, info in combined_video_info.items():
        #     if 'views' in info:
        #         info['views'] = convert_views_to_number(info['views'])

        for bv_num, info in combined_video_info.items():
            print(f"BV号: {bv_num}, 标题: {info['title']}, 播放量: {info['views']}")

        df = pd.DataFrame(combined_video_info).T
        df.index.name = 'BV号'
        df = df[['title', 'views']]  # Reorder columns as '标题', and '播放量'

        df['播放量'] = df['views']
        df = df.rename(columns={'title': '标题', 'views': '播放量'})
        #df.drop(columns=['播放量'], inplace=True)  # Remove the old 'views' column
        #放在对应的bv文件夹视频中
        bv_pattern = r"BV([\w]+)"
        bv_match = re.search(bv_pattern, url)
        bv_num = bv_match.group(1)
        csv_save_path = os.path.join(sys.path[0], 'bilibili_video', bv_num)
        if not os.path.exists(csv_save_path):
            os.makedirs(csv_save_path)
        csv_file = os.path.join(csv_save_path, 'video_info.csv')
        df.to_csv(csv_file, index=True)
#todo:基于什么创建文件夹名称？
    except Exception as e:
        print(e)
        return None


    finally:
        if driver is not None:
            driver.quit()
