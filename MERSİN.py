import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import psycopg2
import json

# Çerezler ve başlıklar
cookies = {
    'PHPSESSID': 'q4o3jv9i915vo7knl8qusi9jao',
    'MBB-Cookie': '2399275530.47873.0000',
    'CookieInfoScript': '1',
}

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

def fetch_mersin_data(ti=None):  # Airflow için ti parametresi ekledik
    all_data = []

    # Kategoriler: 3 = Meyve, 4 = Sebze
    for category in range(3, 5):
        data = {
            'published': str(datetime.date.today()),  # Tarihi dinamik olarak gönder
            'product_category': str(category),
        }

        # POST isteği gönder
        response = requests.post('https://www.mersin.bel.tr/hal-fiyatlari-day', cookies=cookies, headers=headers, data=data)

        if response.status_code == 200:
            # Yanıtı parse et
            df_list = pd.read_html(response.content.decode('utf-8'))
            if df_list:
                df = df_list[0]
                
                # Sütunları ve veriyi kontrol et
                if not df.empty:
                    current_date = datetime.date.today()
                    df['Tarih'] = current_date
                    all_data.append(df)
        else:
            print(f"Hata: {response.status_code}")

    # Veriyi birleştir
    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
        save_to_database(full_df, ti)  # Veriyi kaydet ve XCom'a gönder
    else:
        print("Veri bulunamadı.")

def save_to_database(df, ti=None):
    try:
        # Tarih sütununu datetime formatına çevir
        df['Tarih'] = df['Tarih'].astype(str)  # XCom için string'e çeviriyoruz

        conn = psycopg2.connect(
            host='your_host', 
            database='your_db',
            user='your_user',
            password='your_password',
            port=5432
        )
        cur = conn.cursor()

        # Tabloyu oluştur (eğer yoksa)
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS mersin_halfiyati (
                id SERIAL PRIMARY KEY,
                sube VARCHAR(100),
                urun VARCHAR(100),
                cinsi VARCHAR(100),
                turu VARCHAR(100),
                min_fiyat NUMERIC,
                max_fiyat NUMERIC,
                ort_fiyat NUMERIC,
                birim VARCHAR(20),
                tarih DATE
            )
        """)

        # Veri ekleme sorgusu
        insert_query = """
            INSERT INTO mersin_halfiyati (sube, urun, cinsi, turu, min_fiyat, max_fiyat, ort_fiyat, birim, tarih) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for index, row in df.iterrows():
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
            cur.execute(insert_query, veri)

        # Değişiklikleri kaydet
        conn.commit()

        # XCom'a JSON olarak gönderme
        if ti:
            ti.xcom_push(key='mersin_data', value=df.to_dict(orient='records'))

        print("Veri başarıyla veritabanına eklendi.")
    
    except Exception as e:
        print("Veritabanına bağlanırken hata oluştu:", e)

    finally:
        if conn:
            cur.close()
            conn.close()
            
        # JSON formatında döndürme
        return json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    fetch_mersin_data()
