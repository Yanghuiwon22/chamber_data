import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/Yanghuiwon22/chamber_data/main/output/2024-05-19.csv')

df['Time'] = df['Time'].dt.tz_localize('UTC')
df['Time'] = df['Time'].dt.tz_convert('Asia/Seoul')
print(df)