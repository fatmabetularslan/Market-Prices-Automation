import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import urllib3
import psycopg2
import json

# Uyarı mesajlarını devre dışı bırakma
urllib3.disable_warnings()
# id numarasını hesaplayan fonksiyon
def get_id_for_date(date):
    start_date = datetime(2019, 6, 4)
    delta_days = (date - start_date).days
    id = delta_days + 1  # Çünkü id 1'den başlıyor
    return id

# Veriyi çekme fonksiyonu
def fetch_adana_data(ti):  # ti, XCom için gerekli
    date = datetime.now()
    id = get_id_for_date(date)
    url = f"https://www.adana.bel.tr/tr/hal-detay/{id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    try:
        # HTML içeriğini çekme
        r = requests.get(url, headers=headers, verify=False)
        if r.status_code != 200:
            print(f"Bağlantı hatası: {r.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print("Bağlantı sırasında hata oluştu:", e)
        return

    # HTML içeriğini parse etme
    source = BeautifulSoup(r.content, "lxml")
    
    # Veri çıkarma fonksiyonu
    def extract_data(table):
        data = []
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    try:
                        Cinsi = cells[0].text.strip()
                        Birim = cells[1].text.strip()
                        EnazFiyat = float(cells[2].text.strip().replace(',', '.'))
                        EnçokFiyat = float(cells[3].text.strip().replace(',', '.'))
                        data.append({
                            'Cinsi': Cinsi,
                            'Birim': Birim,
                            'EnazFiyat': EnazFiyat,
                            'EnçokFiyat': EnçokFiyat,
                            "Tarih": datetime.now()
                        })
                    except ValueError as e:
                        print("Veri dönüştürme hatası:", e)
        return data

    # Sebze ve meyve tablosunu bulma
    sebze_table = source.find('div', {'id': 'sebze'}).find('table')
    sebze_data = extract_data(sebze_table)

    meyve_table = source.find('div', {'id': 'meyve'}).find('table')
    meyve_data = extract_data(meyve_table)
    
    # Veriyi DataFrame'e dönüştürme
    df = pd.DataFrame(sebze_data + meyve_data)
    
    if df.empty:
        print("Veri bulunamadı.")
        return
    
    # 'Tarih' sütunundaki Timestamp değerlerini string formatına çevir
    df['Tarih'] = df['Tarih'].astype(str)
def save_to_database(df, ti=None):
    try:
        # Tarih sütununu datetime formatına çevir
        df['Tarih'] = df['Tarih'].astype(str)  # XCom için string'e çeviriyoruz

        conn = psycopg2.connect(
                host='your_host', 
                database='your_db,
                user='your_user',
                password='your_password',
                port=5432
            )
        cur = conn.cursor()
    except Exception as e:
        print("Veritabanına bağlanırken hata oluştu:", e)
        return
    insert_query = """
            INSERT INTO adana_halfiyati (Birim,Cinsi,EnazFiyat,EnçokFiyat,Tarih) 
            VALUES (%s, %s, %s, %s, %s)
        """ 
    for record in data:
            cur.execute(insert_query, (
                record['Birim'],
                record['Cinsi'],
                record['EnazFiyat'],
                record['EnçokFiyat'],
                record['Tarih']
            ))

        # Değişiklikleri kaydet ve bağlantıyı kapat
    conn.commit()
    # XComs'a veri gönderme (DataFrame'i JSON formatına çevirebilirsiniz)
    ti.xcom_push(key='adana_data', value=df.to_dict(orient="records"))
    print("Veri XComs'a gönderildi.")
    
    return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=4)
