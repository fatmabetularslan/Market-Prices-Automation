import requests
from bs4 import BeautifulSoup
import pandas as pd
import pyodbc
from datetime import datetime

# Web sitesinden veri çekme
r = requests.get("https://www.kocaeli.bel.tr/tr/main/halfiyatlari")
source = BeautifulSoup(r.content, "html.parser", from_encoding="iso-8859-8")

data = []

# Verileri toplama
for table in source.find_all("div", attrs={"class": "halfiyatlari col-md-6 col"}):
    for meyve in table.find_all("tr"):
        ürünadı = meyve.find_all("td")[0].text
        birim = meyve.find_all("td")[1].text
        enaz = meyve.find_all("td")[2].text.replace(",", ".")  # Sayısal veri dönüşümü
        ençok = meyve.find_all("td")[3].text.replace(",", ".")  # Sayısal veri dönüşümü

        if ürünadı != "Ürün Adı":
            kocaelihalfiyatı = {
                "UrunAdi": ürünadı.strip(),
                "Birim": birim.strip(),
                "EnazFiyat": float(enaz),
                "EncokFiyat": float(encok),
                "Tarih": datetime.now()
            }
            data.append(kocaelihalfiyatı)

# Verileri DataFrame'e dönüştürme
df = pd.DataFrame(data)

# SQL bağlantısı
conn = pyodbc.connect(f'Driver={{SQL SERVER}};'
                      f'Server=your_serverS;'
                      f'Database=your_databse;'
                      f'Trusted_Connection=yes;')

cursor = conn.cursor()

# Veri ekleme
for index, row in df.iterrows():
    sql_sorgusu = "INSERT INTO kocaelihalfiyatı (UrunAdi, Birim, EnazFiyat, EncokFiyat, Tarih) VALUES (?, ?, ?, ?, ?)"
    veri = (row['UrunAdi'], row['Birim'], row['EnazFiyat'], row['EncokFiyat'], row['Tarih'])
    cursor.execute(sql_sorgusu, veri)
    print(f"Veri ekleniyor: {veri}")

# Değişiklikleri kaydetme
conn.commit()

# Kapatma
cursor.close()
conn.close()
