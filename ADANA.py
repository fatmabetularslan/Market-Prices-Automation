import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib3
import pyodbc


urllib3.disable_warnings()
header="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

r = requests.get("https://www.adana.bel.tr/tr/hal-detay/1490",verify=False)
source = BeautifulSoup(r.content, from_encoding="UTF-8",features="lxml")

def extract_data(table):
    data = []
    if table:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                Cinsi = cells[0].text.strip()
                Birim = cells[1].text.strip()
                EnazFiyat = float(cells[2].text.strip())
                EnçokFiyat = float(cells[3].text.strip())
                data.append({
                    'Cinsi': Cinsi,
                    'Birim': Birim,
                    'EnazFiyat': EnazFiyat,
                    'EnçokFiyat': EnçokFiyat,
                    "Tarih": datetime.now()
                })

    return data

sebze_table = source.find('div', {'id': 'sebze'}).find('table')
sebze_data = extract_data(sebze_table)

meyve_table = source.find('div', {'id': 'meyve'}).find('table')
meyve_data = extract_data(meyve_table)

for item in sebze_data:
     print(item)

for item in meyve_data:
     print(item)
df = pd.DataFrame(sebze_data + meyve_data)


conn = pyodbc.connect(f'Driver={{SQL SERVER}};'
                      f'Server={{BETULLL\SQLEXPRESS}};'
                      f'Database={{HalFiyatları}};'
                      f'Trusted_Connection=yes;')
cursor = conn.cursor()
for index, row in df.iterrows():
       sql_sorgusu = "EXEC [dbo].[spadanahalfiyatı] ?, ?, ?, ?, ?"
       sql_sorgusu = "INSERT INTO adanahalfiyatı (Cinsi,Birim,EnazFiyat,EnçokFiyat, Tarih) VALUES (?, ?, ?, ?,?)"
       veri = (row['Cinsi'], row['Birim'], row['EnazFiyat'],row['EnçokFiyat'], row['Tarih'])
       cursor.execute(sql_sorgusu, veri)
#print(index,row)

cursor.execute('SELECT * FROM adanahalfiyatı ')

conn.commit()


cursor.close()
conn.close()