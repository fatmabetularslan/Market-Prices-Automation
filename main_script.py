import schedule
import time
import sys
import os

# Dosya dizinini ekleyin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ADANA
import KOCAELİ
import MERSİN
import OSMANİYE

def update_all_data():
    print("Starting data update...")
    ADANA.update_data()
    KOCAELİ.update_data()
    MERSİN.update_data()
    OSMANİYE.update_data()
    print("Data update completed.")

# Schedule the job to run daily
schedule.every().day.at("02:00").do(update_all_data)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)

