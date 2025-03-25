# E-Commerce Project Setup Guide

## **For Dockerized App Setup**

1. **Build and Start the Docker Containers:**
   ```sh
   docker compose up --build -d
   ```
   
2. **Check Running Containers:**
   ```sh
   docker ps
   ```
   
3. **Apply Migrations:**
   ```sh
   docker exec -it ps_thakker_e_commerce python manage.py migrate
   ```
   
4. **Create a Superuser (Optional for Admin Panel):**
   ```sh
   docker exec -it ps_thakker_e_commerce python manage.py createsuperuser
   ```
   
5. **Check Logs:**
   ```sh
   docker logs -f ps_thakker_e_commerce
   ```
   
6. **Restart Containers:**
   ```sh
   docker compose restart
   ```
   
7. **Stop Containers:**
   ```sh
   docker compose down
   ```

## **For Normal Setup (Without Docker)**

### **1. Create and Activate Virtual Environment**
#### **Ubuntu/Linux/macOS:**
```sh
virtualenv venv
source venv/bin/activate
```
#### **Windows:**
```sh
virtualenv venv
. venv/bin/activate
```

### **2. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **3. Setup PostgreSQL Database**
```sh
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

### **4. Configure PostgreSQL**
```sh
sudo -u postgres psql
```
Inside PostgreSQL shell, run:
```sql
CREATE DATABASE e_commerce;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER USER postgres WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE e_commerce TO postgres;
\q
```

### **5. Apply Migrations and Start the Server**
```sh
python manage.py migrate
python manage.py runserver
```










# Customer View:
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/57257787-2e48-47a4-a88e-ed1e1082949c)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/00b59bac-a6df-485e-b6f2-d5f71c7dd28c)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/aa45d5ce-253c-4780-9af5-cfe67989e673)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/e1e62bad-3aa0-470c-b93c-283e976001ec)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/413a33b0-6984-422c-b516-d01146319be7)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/3f92d6a5-b75a-4453-bcda-3af72c554922)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/8a99c51c-0673-4b88-a0f4-0903505ee58d)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/44ebd03b-909a-424f-ab47-c0c35c4df4a6)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/792d23b0-aad3-4903-bc1c-0eec2b3d0ea5)

# Admin View:
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/05381910-5e20-42a6-a646-5212e96d6729)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/eaf9e4ea-78ab-4a58-879c-641a187f663e)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/9b8c57af-59a8-46a2-9c63-0538915db922)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/7c8d5c1e-8de9-4aad-9c1f-ad4bf30aabe2)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/fbcd8287-a695-4981-adcb-9ef97265976c)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/dd21ad58-1320-432a-b496-19dc19f5e447)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/4dd50d29-7235-4d47-957d-8f2d8259fadc)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/0789064c-9885-4c5c-9053-c53f5717ad34)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/df7ef086-ab0d-478b-89aa-e2ef0d033fef)
![image](https://github.com/Malay-Thakkar/E-commerce/assets/78149426/5422c7a0-ac65-4758-ba6a-7eec502793f5)
