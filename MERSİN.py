import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import pyodbc
cookies = {
    'PHPSESSID': 'q4o3jv9i915vo7knl8qusi9jao',
    'MBB-Cookie': '2399275530.47873.0000',
    'CookieInfoScript': '1',
    'TS01f00959': '017de0d5fafedb9ee09bcd1a92a6baec792bdec189d074662f40d6c1de87b6caa56e7987ba3d20ed54d22ff60875037ae5d30fba9ec80c6d08ff1a30f2b015b113522edfe456abe669034fa8415b980b4cc3786605',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8,tr-TR;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'PHPSESSID=q4o3jv9i915vo7knl8qusi9jao; MBB-Cookie=2399275530.47873.0000; CookieInfoScript=1; TS01f00959=017de0d5fafedb9ee09bcd1a92a6baec792bdec189d074662f40d6c1de87b6caa56e7987ba3d20ed54d22ff60875037ae5d30fba9ec80c6d08ff1a30f2b015b113522edfe456abe669034fa8415b980b4cc3786605',
    'Origin': 'https://www.mersin.bel.tr',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


for i in range(3,5):

    data = {
        'published': '' + str(datetime.date.today()) + '',  # tarihi dinamik
        'product_category': '' + str(i) + '',  # 3 meyve 4 sebze
    }

    response = requests.post('https://www.mersin.bel.tr/hal-fiyatlari-day', cookies=cookies, headers=headers, data=data)


source = BeautifulSoup(response.content, "html.parser", from_encoding="iso-8859-8")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
df = pd.read_html(response.content.decode('utf-8'))[0]

#print(df)

current_date = datetime.date.today()
df['Tarih'] = current_date
conn = pyodbc.connect(f'Driver={{SQL SERVER}};'
                       f'Server={{BETULLL\SQLEXPRESS}};'
                       f'Database={{HalFiyatları}};'
                       f'Trusted_Connection=yes;')

Cursor = conn.cursor()

for index, row in df.iterrows():
     sql_sorgusu = "INSERT INTO mersinhalfiyatı (Şube, Ürün, Cinsi, Türü ,MinFiyat, MaxFiyat, OrtFiyat, Birim, Tarih) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
     veri = (
         row['ŞUBE'], 
         row['ÜRÜN'], 
         row['CİNSİ'], 
         row['TÜRÜ'],
         float(row['Min. Fiyat'].replace(' TL', '').replace(',', '.')),
         float(row['Mak. Fiyat'].replace(' TL', '').replace(',', '.')),
         float(row['Ort. Fiyat'].replace(' TL', '').replace(',', '.')),
         row['Birim'], 
         row['Tarih']
     )
     print(index, veri)  # Log verileri kontrol etmek için
     Cursor.execute(sql_sorgusu, veri)

conn.commit()  # Tüm işlemler bittiğinde commit çağrılır
Cursor.close()
conn.close()
