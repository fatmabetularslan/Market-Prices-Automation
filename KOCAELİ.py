import requests
from bs4 import BeautifulSoup
import pandas as pd
import pypyodbc
import pyodbc
from datetime import datetime

r = requests.get("https://www.kocaeli.bel.tr/tr/main/halfiyatlari")
source = BeautifulSoup(r.content, "html.parser", from_encoding="iso-8859-8")


data = []


for table in source.find_all("div", attrs={"class": "halfiyatlari col-md-6 col"}):
    for meyve in table.find_all("tr"):
        ürünadı = meyve.find_all("td")[0].text
        birim = meyve.find_all("td")[1].text
        enaz = meyve.find_all("td")[2].text
        ençok = meyve.find_all("td")[3].text

        if ürünadı != "Ürün Adı":
            # Verileri bir sözlük olarak ekleyin
            kocaelihalfiyatı = {
                "UrunAdi": ürünadı,
                "Birim": birim,
                "EnazFiyat": enaz,
                "EncokFiyat": ençok,
                "Tarih": datetime.now()

            }
            data.append(kocaelihalfiyatı)



df = pd.DataFrame(data)

conn = pyodbc.connect(f'Driver={{SQL Server Native Client 11.0}};'
                      f'Server={{DESKTOP-QSBKBOA\MSSQL2}};'
                      f'Database={{HalTuru}};'
                      f'Trusted_Connection=yes;')




cursor = conn.cursor()


for index, row in df.iterrows():
    sql_sorgusu = "EXEC [dbo].[spkocaelihalfiyatı] ?,?,?,?,?"
    sql_sorgusu = "INSERT INTO kocaelihalfiyatı (UrunAdi,Birim,EnazFiyat,EncokFiyat, Tarih) VALUES (?, ?, ?, ?,?)"
    veri = (row['UrunAdi'], row['Birim'], row['EnazFiyat'],row['EncokFiyat'], row['Tarih'])
    cursor.execute(sql_sorgusu, veri)
    print(index,row)
    cursor.commit()


cursor.close()
conn.close()



