import pandas as pd
from datetime import datetime
import psycopg2
import requests

def fetch_izmir_data(ti=None):
    base_url = "https://openapi.izmir.bel.tr/api/ibb/halfiyatlari/sebzemeyve/"
    today = datetime.now().date()
    url = f"{base_url}{today.year}-{today.month:02d}-{today.day:02d}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            result_json = response.json()["HalFiyatListesi"]
            df = pd.json_normalize(result_json)
            df["Tarih"] = today
            print(f"{today}: Veri başarıyla çekildi.")
            
            # XCom'a kaydetmek için sadece gerekli sütunları seçin
            simplified_data = df[['MalAdi', 'AsgariUcret', 'AzamiUcret', 'Tarih']].to_dict(orient="records")
            if ti:
                ti.xcom_push(key='izmir_data', value=simplified_data)
            
            return df
        elif response.status_code == 204:
            print(f"{today}: Veri bulunamadı.")
        else:
            print(f"Hata: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("Bağlantı sırasında hata oluştu:", e)
   
    return pd.DataFrame()

def save_to_database(ti=None):
    try:
        # XCom'dan veri al
        if ti:
            records = ti.xcom_pull(task_ids='fetch_izmir_data', key='izmir_data')
            df = pd.DataFrame(records)
        else:
            print("XCom'dan veri alınamadı.")
            return
        
        # PostgreSQL bağlantısı
        conn = psycopg2.connect(
            host='postgres', 
            database='airflow',
            user='postgres',
            password='postgres',
            port=5432
        )
        cur = conn.cursor()

        # Tablo oluşturma
        cur.execute('''
        CREATE TABLE IF NOT EXISTS izmir_hal_fiyatlari (
            Product_Name TEXT,
            Min_Price REAL,
            Max_Price REAL,
            Tarih DATE
        )
        ''')
        conn.commit()

        # Verileri tabloya ekleme
        for _, row in df.iterrows():
            cur.execute('''
            INSERT INTO izmir_hal_fiyatlari (
                Product_Name, Min_Price, Max_Price, Tarih
            ) VALUES (%s, %s, %s, %s)
            ''', (
                row['MalAdi'], row['AsgariUcret'], row['AzamiUcret'], row['Tarih']
            ))
        conn.commit()
        print("Veri başarıyla veritabanına kaydedildi.")
    except Exception as e:
        print("Veritabanına kaydedilirken hata oluştu:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    # Bu kod Airflow DAG'inde bağımsız olarak kullanılacak
    print("Bu kod Airflow üzerinden çalıştırılmalıdır.")
