# Django-blog (portfolio)

This project is a full-stack blogging platform built with Django and PostgreSQL. Authors can create and manage articles through a rich text editor, while authenticated users can search, like, comment on, and discover content through a recommendation system. The application is containerized with Docker, tested automatically through GitHub Actions, and deployed on Render.

## Live demo

[https://django-blog-jq2v.onrender.com/blog/blogs/](https://django-blog-jq2v.onrender.com/blog/blogs/)

## Screenshots

<img width="1872" height="893" alt="Image" src="https://github.com/user-attachments/assets/9d393aab-2432-4d73-8073-5fe74cf4dbc0" />

## Features

- Author-only article publishing
- Draft and published posts
- TinyMCE rich text editor
- Search functionality
- Categories
- Likes and comments
- Author profiles
- View statistics
- Related article recommendations
- Dockerized development and production environments
- Automated testing
- CI/CD with GitHub Actions
- Automatic deployment to Render

## Tech Stack

Backend:
- Django
- PostgreSQL

Frontend:
- HTML
- CSS
- JavaScript
- TinyMCE

Infrastructure:
- Docker
- Nginx
- Gunicorn
- GitHub Actions
- Render
- Supabase Storage

## Installation

```bash
git clone https://github.com/ludovicnicolau/django-blog.git
```
Add an .env file at the root containing:
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY="a secret key used by django for your website"
POSTGRES_DB="The name of your database"
POSTGRES_PASSWORD="The password for your database user"
POSTGRES_USER="The name of your database user"
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
Launch postgres, gunicorn django, nginx:
```bash
docker compose -f compose.yaml up --build -d 
```
Apply the migrations:
```bash
docker compose exec blog python manage.py migrate
```
Create an admin:
```bash
docker compose exec blog python manage.py createsuperuser
```
Collect the static files (css, js, static images):
```bash 
docker compose exec blog python manage.py collectstatic
```
Launch a custom command to create the blogger group:
```bash
docker compose exec blog python manage.py init_groups
```

To enable HTTPS locally, generate a self signed certificate.
```bash
openssl genrsa -out server.key 2048
openssl req -new -x509 -key server.key -out server.crt -days 365
```

They should be called *server.key* and *server.crt* and be placed at the root next to compose.yaml and nginx.conf.

### ⚠️ Important note (you should add this)

```md
⚠️ This certificate is self-signed and will trigger a browser security warning.
This is expected in development environments. You should not use this method for production.
You can also use something like mkcert to avoid the browser security warning.
For production, you should use a *Certificate Authority* like *Let's Encrypt*

## Testing

Run the test suite:

```bash
docker compose -f compose.test.yaml up --build --abort-on-exit
```

The project currently contains 112 tests.

## Usage

Once the application is running, access it at:

```text
https://localhost/
```

The Django administration panel is available at:

```text
https://localhost/admin/
```

```md
You must have a superuser to access it. If you followed the installation, you already created one.
```

### Create categories

The first thing you will have to do is create categories. For this, go to the administration panel and login with the superuser you previously created.
Click *Add* next to *Categories*. Enter the name of your category and click "save" or "save and another" to create another category.

### Give author role to users

Go to the administration panel and login.
Click on *Users* and in the following page, select the user you would like to become author.
In *Groups*, click on *bloggers* and finally click *SAVE* in the bottom of the page.
Now, this user can create blog posts, edit them and delete them.