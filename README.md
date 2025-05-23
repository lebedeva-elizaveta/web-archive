# Веб-архив
## Описание
Проект представляет собой веб-приложение, которое позволяет сохранять копии веб-страниц и собирать информацию о домене:
- доменное имя веб-страницы;
- IP-адрес, на котором размещена веб-страница;
- протокол WHOIS для получения информации о владельце домена.
  
## Запуск проекта
1. Выполните команду для клонирования репозитория:
```bash
git clone https://github.com/lebedeva-elizaveta/web-archive
```
2. Перейдите в директорию проекта:
```bash
cd web-archive
```
3. Создайте свой ``SECRET_KEY``, просто скопируйте и выполните в терминале вот эту команду:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
4. Создайте файл '.env' в корневой директории проекта и добавьте в него следующие переменные окружения:
```bash
IS_DOCKER=true
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
POSTGRES_DB=postgres
DATABASE_URL=postgresql://postgres:1234@db:5432/postgres
PGADMIN_DEFAULT_EMAIL=admin@admin.ru
PGADMIN_DEFAULT_PASSWORD=1234
SECRET_KEY=ваш_новый_ключ
```

5. Выполните следующую команду для сборки контейнеров с помощью Docker Compose:
```bash
docker compose build
```
6. Выполните следующую команду для запуска контейнеров с помощью Docker Compose:
```bash
docker compose up
```
7. Приложение будет доступно по адресу http://localhost:5000
8. Для доступа к административной панели перейдите по ссылке: http://localhost:5050. Используйте данные PGADMIN_DEFAULT_EMAIL и PGADMIN_DEFAULT_PASSWORD для входа в pgAdmin.
