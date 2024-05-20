import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta,datetime

url = 'https://api.thingspeak.com/channels/1999883/feeds.json?api_key=XP1R5CVUPVXTNJT0&'
results = 0 # 받고자 하는 데이터 수 (현재를 기준으로 과거데이터, 데이터간격 3분)

def get_data():
    response = requests.get(url+'results=5000')

    if response.status_code == 200:
        df_chamber = pd.DataFrame(response.json()['feeds'])
        df_chamber.insert(loc=1, column='Date', value=df_chamber['created_at'].str.split('T').str[0])
        df_chamber.insert(loc=2, column='Time', value=pd.to_datetime(df_chamber['created_at'].str.split('T').str[1].str.split('Z').str[0], format='%H:%M:%S').dt.time)
        df_chamber['Time'] = df_chamber['Time'].apply(lambda t: (datetime.combine(datetime.min, t) + timedelta(hours=9)).time())

        df_chamber.drop(['created_at','field4'], axis=1, inplace=True)
        df_chamber.rename(columns={'field1': 'temp', 'field2': 'hum', 'field3': 'lux'}, inplace=True)

    grouped = df_chamber.groupby('Date')
    for group_name, group_df in grouped:
        if group_name >= '2024-05-17':
            print(f"========={group_name}=========")
            print(group_df)
            group_df.to_csv(f'./output/{group_name}.csv', index=False)

def draw_graph(date):
    df = pd.read_csv(f'{date}.csv')

    ax = sns.lineplot(data=df, x='Time', y='temp')
    ax.set_xticks(range(0, len(df)+1, 60))
    plt.savefig(f'{date}.png')



def main():
    output_dir = './output'

    get_data()
    draw_graph(f'{output_dir}/2024-05-20')

    data1 = pd.read_csv(f'{output_dir}/2024-05-19.csv')
    data2 = pd.read_csv(f'{output_dir}/2024-05-18.csv')


if __name__ == '__main__':
    main()