import time

import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta, datetime

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


url = 'https://api.thingspeak.com/channels/1999883/feeds.json?api_key=XP1R5CVUPVXTNJT0&'
results = 0 # 받고자 하는 데이터 수 (현재를 기준으로 과거데이터, 데이터간격 3분)

def get_data():
    response = requests.get(url+'results=50000')

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
        print(group_df)

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
    get_data()

    # now = datetime.now()
    # now_date = now.date()
    # draw_lux_graph(now_date, 'lux')
    # draw_graph(now_date)

    ## 오류가 날 경우 실행시킬 코드
    # error_date = get_error_date()
    error_date = ['2024-07-15', '2024-07-16', '2024-07-17', '2024-07-18', '2024-07-19', '2024-07-20', '2024-07-21', '2024-07-22',
     '2024-07-23', '2024-07-24', '2024-07-25', '2024-07-26', '2024-07-27', '2024-07-28', '2024-07-29', '2024-07-30',
     '2024-07-31', '2024-08-01', '2024-08-02', '2024-08-03', '2024-08-04', '2024-08-05', '2024-08-06', '2024-08-07',
     '2024-08-08', '2024-08-09', '2024-08-10', '2024-08-11', '2024-08-12', '2024-08-13', '2024-08-14']

    for date in error_date:
        draw_graph(date)
        draw_lux_graph(date, 'lux')


# 특정일부터 오류가 계속될 경우, 해당 기간에 대한 데이터를 생성 후 저장하는 함수
def get_error_date():
    print('loading get_errordate(01/08)')
    base_url = 'https://github.com/Yanghuiwon22/chamber_data/tree/main/output/graph'

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print('loading get_errordate(02/08)')

    # selenium
    op = Options()
    print('loading get_errordate(03/08)')

    driver = webdriver.Chrome(options=op)
    driver.get(base_url)
    print('loading get_errordate(04/08)')


    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")

        time.sleep(1)
        if new_height == last_height:
            time.sleep(1)
            print('loading get_errordate(05/08)')
            break

    time.sleep(1)
    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    rows_len = len(rows)
    print('loading get_errordate(06/08)')

    final_date = driver.find_elements(By.XPATH, f'//*[@id="folder-row-{rows_len-2}"]/td[2]/div/div/div/div/a')[0].text.split('_')[0]
    print('loading get_errordate(07/08)')
    print('='*20)

    # 처리되지 않는 날짜들 구하기
    final_date = datetime.strptime(final_date, '%Y-%m-%d').date()
    today_date = datetime.date(datetime.now())

    error_date = [(final_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, (today_date - final_date).days)]
    print('loading get_errordate(08/08)')

    return error_date


if __name__ == '__main__':
    main()