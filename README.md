# Hal Fiyatları Web Scraping Projesi

Bu proje, Adana, Kocaeli ve Mersin belediyelerinin hal fiyatlarını otomatik olarak çekmek, PostgreSQL veritabanında saklamak ve Airflow ile süreçleri otomatikleştirmek için geliştirilmiştir. Web scraping işlemleri Python ile gerçekleştirilmiştir.

## 📋 Proje Özeti

- **Amaç:** Hal fiyatlarının belediye web sitelerinden düzenli olarak çekilmesi, saklanması ve analiz için hazır hale getirilmesi.
- **Kullanılan Teknolojiler:**
  - **Python**: Veri çekme ve işleme
  - **PostgreSQL**: Veritabanı saklama
  - **Airflow**: İş akışı otomasyonu
  - **Docker**: Projenin konteynerize edilmesi
  - **BeautifulSoup ve Requests**: Web scraping için
  - **Psycopg2**: PostgreSQL bağlantısı

---

## 🚀 Kurulum

### 1. Gerekli Bağımlılıkları Yükleyin
Aşağıdaki Python kütüphaneleri gereklidir:
```bash
pip install requests beautifulsoup4 psycopg2 airflow
```
---
## 2. Docker Kurulumu

Docker ile PostgreSQL ve Airflow'u çalıştırmak için aşağıdaki adımları takip edin:

### 1. Docker Compose Dosyasını İndirin veya Oluşturun

Aşağıdaki YAML kodunu `docker-compose.yml` dosyasına yapıştırın:

```yaml
version: '3.7'
services:
  postgres:
    image: postgres:latest
    container_name: your_container_name
    environment:
      POSTGRES_USER:your_postgres_user
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: your_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  airflow:
    image: apache/airflow:latest
    container_name: your_container_name
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://your_postgres_user:password@your_password:5432/Postgres_DB
    depends_on:
      - postgres

volumes:
  postgres_data:
```
---

### 2. Docker'ı Başlatın

Aşağıdaki komutla Docker konteynerlerini başlatabilirsiniz:

```bash
docker-compose up -d
```
---
## 📂 Proje Yapısı

```bash
hal-fiyatlari/
├── dags/
│   ├── adana_dag.py           # Adana için Airflow DAG
│   ├── kocaeli_dag.py         # Kocaeli için Airflow DAG
│   └── mersin_dag.py          # Mersin için Airflow DAG
├── scripts/
│   ├── adana.py               # Adana Belediyesi Web Scraping
│   ├── kocaeli.py             # Kocaeli Belediyesi Web Scraping
│   └── mersin.py              # Mersin Belediyesi Web Scraping
├── docker-compose.yml         # Docker Compose Dosyası
├── README.md                  # Proje Hakkında Bilgi

```
---

## 🛠 Kullanım

### Airflow'u Başlatın:
```bash
docker-compose up airflow

```
---
```bash
python scripts/adana.py
python scripts/kocaeli.py
python scripts/mersin.py
```
---
**Airflow UI'ı Kullanın:**

Airflow UI'ına http://localhost:8080 adresinden erişin ve DAG'leri aktif edin.



