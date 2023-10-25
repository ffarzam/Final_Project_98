# RSS Feed Django Project
Welcome to the RSS Feed Django project! 

## Table of Contents
* [About the Project](#about-the-project)
* [Build With](#build-with)
* [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

* [Running the Project](#running-the-project)
* [License](#license)
* [Contributing](#contributing)



## About the Project
This project is a web application built with Django Rest framework for content aggregation from RSS Feeds. This README file will guide you through the setup process, provide instructions for running the project, and explain how to contribute to its development.


## Build With
* [![Django][django.js]][django-url]
* [![Django Rest Framework][Django Rest Framework.js]][Django Rest Framework-url]
* [![Postgres][Postgres.js]][Postgres-url]
* [![Redis][Redis.js]][Redis-url]
* [![Docker][Docker.js]][Docker-url]
* [![RabbitMQ][RabbitMQ.js]][RabbitMQ-url]
* [![ElasticSearch][ElasticSearch.js]][ElasticSearch-url]
* [![Gunicorn][Gunicorn.js]][Gunicorn-url]
* [![Nginx][Nginx.js]][Nginx-url]
* [![Minio][Minio.js]][Minio-url]


## Setup

### Prerequisites
Before setting up the RSS Feed Django project, ensure that you have the following prerequisites installed on your machine:
- [![Python][Python.js]][Python-url]
- [![PIP][PIP.js]][PIP-url]
- [![Github][Github.js]][Github-url]
- [![Docker][Docker.js]][Docker-url]


### Installation
Follow these steps to set up the project:

1- Clone the repository using Git:

```bash
git clone https://github.com/ffarzam/Final_Project_98.git
```
2- Create a .env file in your project root to store environment variables base on Django project settings like this:
```
SECRET_KEY= your secret key

NAME= your postgres name
HOST=your postgres host
PORT=your postgres port
USER=your postgres username
PASSWORD=your postgres password

REDIS_HOST=your redis host
REDIS_PORT=your redis port

RABBITMQ_HOST=your rabbitmq host
RABBITMQ_PORT=your rabbitmq port
RABBITMQ_USERNAME=your rabbitmq host username
RABBITMQ_PASSWORD=your rabbitmq host password

DEFAULT_FROM_EMAIL=your email
EMAIL_BACKEND=your email backend
EMAIL_HOST=your email host
EMAIL_HOST_USER=your email host user
EMAIL_HOST_PASSWORD=your email host password
EMAIL_PORT=your email port
EMAIL_USE_TLS=your conf

ELASTICSEARCH_HOST=your elasticsearch host
ELASTICSEARCH_PORT=your elasticsearch port

MINIO_ROOT_USER=your minio username
MINIO_ROOT_PASSWORD=your minio password
```


Congratulations! The RSS Feed Django project has been successfully set up on your machine.


### Running the Project
To run the RSS Feed Django project, follow these steps:

1- Start the Docker containers:
```
docker-compose up -d --build
```
This command will launch the Django app, a database (e.g., PostgreSQL), and any other services defined in your docker-compose.yml file.

2- Access your Django admin panel in your web browser:

Django Admin: http://localhost/admin/

### License
![MIT][MIT.js]


### Contributing
We welcome contributions to the RSS Feed Django project. If you'd like to contribute, please follow these steps:

Fork the repository on GitHub.

Clone your forked repository to your local machine:

```bash
git clone https://github.com/ffarzam/Final_Project_98.git
```
Create a new branch for your changes:


```bash
git checkout -b feature/your-feature-name
```
Make the necessary changes and commit them:


```bash
git commit -m "Add your commit message here"
```
Push your changes to your forked repository:

```bash
git push origin feature/your-feature-name
```
Open a pull request on the original repository, describing your changes and explaining why they should be merged.

Wait for the project maintainers to review your pull request. Once approved, your changes will be merged into the main project.

Thank you for your interest in contributing to the RSS Feed Django project! We appreciate your help.

[django.js]: https://img.shields.io/badge/Django-F77FBE?style=for-the-badge&logo=django&logoColor=black
[django-url]: https://www.djangoproject.com/
[Django Rest Framework.js]: https://img.shields.io/badge/Django%20Rest%20Framework-blue?style=for-the-badge
[Django Rest Framework-url]: https://www.django-rest-framework.org/

[Redis.js]: https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.com/

[Postgres.js]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/

[Docker.js]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/

[ElasticSearch.js]: https://img.shields.io/badge/-ElasticSearch-005571?style=for-the-badge&logo=elasticsearch
[ElasticSearch-url]: https://www.elastic.co/

[RabbitMQ.js]: https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white
[RabbitMQ-url]: https://www.rabbitmq.com/

[Nginx.js]: https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white
[Nginx-url]: https://www.nginx.com/

[Gunicorn.js]: https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white
[Gunicorn-url]: https://gunicorn.org/

[Minio.js]: https://img.shields.io/badge/Minio-c72c48.svg?style=for-the-badge&logo=minio&logoColor=white
[Minio-url]: https://min.io/

[Python.js]: https://img.shields.io/badge/Python-red?style=for-the-badge&logo=python&logoColor=black
[Python-url]: https://www.python.org/
[PIP.js]: https://img.shields.io/badge/PIP_(Python_package_manager)-blue?style=for-the-badge&logo=pypi&logoColor=white

[PIP-url]: https://pypi.org/
[Github.js]: https://img.shields.io/badge/GitHub-green?style=for-the-badge&logo=github&logoColor=black
[Github-url]: https://github.com/
[MIT.js]: https://img.shields.io/badge/License-MIT-F77FBE.svg
[MIT-url]: https://www.python.org/
