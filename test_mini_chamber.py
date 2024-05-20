import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta, datetime

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

        if group_name >= '2024-05-17' and len(group_df) > 1400:
            group_df.to_csv(f'./output/csv/{group_name}.csv', index=False)
            print(f'{group_name} 성공')
        else:
            print(f'{group_name} 실패')

def draw_graph(date, y):
    df = pd.read_csv(f'output/csv/{date}.csv')

    graph_df = df[['Time', y]]
    graph_df['Hour'] = df['Time'].str.split(':').str[0]
    plt.figure()
    ax = sns.lineplot(data=graph_df, x='Hour', y=y)
    ax.set_ylabel(y)
    ax.set_xlabel('Time')
    ax.set_title(f'{date}-{y} graph')
    plt.savefig(f'output/graph/{date}_{y}.png')



def main():
    now = datetime.now()
    now_date = now.date()
    # now_date = '2024-05-18'

    get_data()
    draw_graph(now_date, 'temp')
    draw_graph(now_date, 'hum')
    draw_graph(now_date, 'lux')

if __name__ == '__main__':
    main()