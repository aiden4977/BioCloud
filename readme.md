### BioCloud: a Django-based Bioinfomatics Analysis Platform

![Django](https://img.shields.io/badge/django-4.0-blue?style=for-the-badge&logo=django&logoColor=blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1-blueviolet?style=for-the-badge&logo=Bootstrap&logoColor=blueviolet)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=Python&logoColor=blue)

Python + Django + Celery + SQLitedb + Redis

## Main function🍳

### 1. Bioinformatics Task Submission
- Supports remote access within the local area network. 
- Supports local data upload or direct selection of sequencing data on the server. 
### 2. Task Management
- Real-time updates of task status (successful/failed/queued/running).
- Support setting the maximum number of tasks and memory.
- View HTML reports and download report files.


## Start🍳
    python manage.py makemigrations 
    python manage.py migrate 
    python manage.py createsuperuser 
    python manage.py 0.0.0.0:3001