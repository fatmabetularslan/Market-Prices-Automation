import requests
from bs4 import BeautifulSoup
import pandas as pd
import pyodbc
import datetime
url = "https://www.halfiyatlari.net/osmaniye-hal-fiyatlari"
r = requests.get(url)

if r.status_code == 200:
    encoding = r.apparent_encoding
    source = BeautifulSoup(r.content, "html.parser", from_encoding=encoding)

    tables = source.find_all('table')

    if tables:
        df = pd.read_html(str(tables[0]), skiprows=1)[0]

        df.columns = ['Ürün', 'En Düşük', 'En Yüksek']

        for index, row in df.iterrows():
            Ürün = row['Ürün']
            EnazFiyat = row['En Düşük']
            EnçokFiyat = row['En Yüksek']
            print(f"Ürün: {Ürün}, EnazFiyat: {EnazFiyat}, EnçokFiyat: {EnçokFiyat}")

        print(df)
    else:
        print("No tables found on the web page.")
else:
    print(f"Failed to retrieve the page. Status code: {r.status_code}")

current_date = datetime.date.today()
df['Tarih'] = current_date

conn = pyodbc.connect(f'Driver={{SQL Server Native Client 11.0}};'
                      f'Server={{DESKTOP-QSBKBOA\MSSQL2}};'
                      f'Database={{HalTuru}};'
                      f'Trusted_Connection=yes;')

Cursor = conn.cursor()

for index, row in df.iterrows():
     sql_sorgusu = "INSERT INTO osmaniyehalfiyatı (Ürün, EnazFiyat, EnçokFiyat, Tarih) VALUES (?, ?, ?, ?)"
     sql_sorgusu = "EXEC [dbo].[sposmaniyehalfiyatı] ?,?,?,?"
     veri = (row['Ürün'],
             row['En Düşük'].replace(' TL', '').replace(',', '.'),
             row['En Yüksek'].replace(' TL', '').replace(',', '.'),
             row['Tarih'])
     print(index, row)
     Cursor.execute(sql_sorgusu, veri)
     conn.commit()  # Commit after each insertion

Cursor.close()
conn.close()


