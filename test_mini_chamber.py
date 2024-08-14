import time

import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta, datetime

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

url = 'https://api.thingspeak.com/channels/1999883/feeds.json?api_key=XP1R5CVUPVXTNJT0&'
results = 0 # 받고자 하는 데이터 수 (현재를 기준으로 과거데이터, 데이터간격 3분)

def get_data():
    response = requests.get(url+'results=5000')

    if response.status_code == 200:
        df_chamber = pd.DataFrame(response.json()['feeds'])

        # 한국시간으로 맞추기
        df_chamber.insert(loc=1, column='Date', value=df_chamber['created_at'].str.split('T').str[0])
        df_chamber.insert(loc=2, column='Time', value=df_chamber['created_at'].str.split('T').str[1].str.split('Z').str[0])
        df_chamber.drop(['created_at','field4'], axis=1, inplace=True)

        df_chamber.insert(loc=0, column='Date&Time', value=pd.to_datetime(df_chamber['Date'] + ' ' + df_chamber['Time']))
        df_chamber['Date&Time'] = df_chamber['Date&Time'] + timedelta(hours=9)
        df_chamber['Date&Time'] = df_chamber['Date&Time'].astype(str)
        df_chamber['Date'] = df_chamber['Date&Time'].str.split(' ').str[0]
        df_chamber['Time'] = df_chamber['Date&Time'].str.split(' ').str[1]
        df_chamber.rename(columns={'field1': 'temp', 'field2': 'hum', 'field3': 'lux'}, inplace=True)

    grouped = df_chamber.groupby('Date')
    for group_name, group_df in grouped:
        print(len(group_df))

        if group_name >= '2024-05-17':
            group_df.to_csv(f'./output/csv/{group_name}.csv', index=False)
            print(f'{group_name} 성공')
        else:
            print(f'{group_name} 실패')

def draw_graph(date, y='t_h'):
    df = pd.read_csv(f'output/csv/{date}.csv')
    df = df[['Time', 'temp', 'hum', 'lux']].dropna()
    df['Hour'] = df['Time'].str.split(':').str[0]

    fig, ax1 = plt.subplots()
    color_temp = 'r'
    color_hum = 'b'
    color_lux = 'y'
    sns.lineplot(x=df['Hour'].astype(int), y=df['temp'], ax=ax1, c=color_temp, lw=5, label='temp')
    ax2 = ax1.twinx()

    sns.lineplot(x=df['Hour'].astype(int), y=df['hum'], ax=ax2, c=color_hum, lw=5, label='hum', legend=False)
    # ax.plot(df['Hour'], df['lux'], c=color_lux, lw=5, label='광')

    for s in ["left", "right", "top"]:
        ax1.spines[s].set_visible(False)
    ax1.spines['bottom'].set_linewidth(3)

    ax1.grid(axis="y")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax1.legend(lines, labels, loc='upper right')

    plt.tight_layout()
    # plt.show()
    plt.savefig(f'output/graph/{date}_{y}.png')


def draw_lux_graph(date, y='t&h'):
    df = pd.read_csv(f'output/csv/{date}csv')
    df = df[['Time', 'temp', 'hum', 'lux']].dropna()
    df['Hour'] = df['Time'].str.split(':').str[0]

    fig, ax1 = plt.subplots()
    color_lux = 'y'
    sns.lineplot(x=df['Hour'].astype(int), y=df['lux'], ax=ax1, c=color_lux, lw=5, label='lux')
    for s in ["left", "right", "top"]:
        ax1.spines[s].set_visible(False)
    ax1.spines['bottom'].set_linewidth(3)
    ax1.grid(axis="y")
    ax1.legend(loc='upper right')

    plt.tight_layout()
    # plt.show()
    plt.savefig(f'output/graph/{date}_{y}.png')



def main():
    # get_data()

    # now = datetime.now()
    # now_date = now.date()
    # draw_lux_graph(now_date, 'lux')
    # draw_graph(now_date)

    get_error_date()


# 특정일부터 오류가 계속될 경우, 해당 기간에 대한 데이터를 생성 후 저장하는 함수
def get_error_date():
    base_url = 'https://github.com/Yanghuiwon22/chamber_data/tree/main/output/graph'

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    final_date = soup.find('div').find_all('a', {'class':'Link--primary'})
    # print(final_date)

    files = soup.find_all('a', string=lambda title: 't_h' in title if title else False)
    # print(files[0].text.split('_'))
    #
    # contents = response.json()
    # date = contents[-1]
    # print(contents)

    # page_number = 1
    # last_file_name = 'fail'
    #
    # while True:
    #     now_page = f'{base_url}?page={page_number}'
    #     now_response = requests.get(now_page)
    #     soup = BeautifulSoup(now_response.text, 'html.parser')
    #
    #     files = soup.find_all('a', {'class':'Link--primary'})
    #
    #     if not files:
    #         break
    #
    #     last_file_name = files[-1].text
    #     page_number += 1
    #
    # print(last_file_name)


    driver = webdriver.Chrome()
    driver.get(base_url)

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")

        time.sleep(1)
        if new_height == last_height:
            time.sleep(1)
            break

    ## 스크롤 완.


    time.sleep(1)
    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    rows_len = len(rows)

    print(driver.find_elements(By.XPATH, f'//*[@id="folder-row-{rows_len-2}"]/td[2]/div/div/div/div/a')[0].text)

    # for row in rows:
    #     cells = row.find_elements(By.CLASS_NAME, "Link--primary")
    #     print(len(cells))
    #
    #     for cell in cells:
    #         print(cell.text)



    today_date = datetime.date(datetime.now())




if __name__ == '__main__':
    main()