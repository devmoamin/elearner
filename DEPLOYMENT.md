# Guide to deploy your Django app

Before you start make sure [git](https://git-scm.com/downloads) is installed

we could separate settings for development and production by creating different files `prod.py` and `dev.py` and importing the requirement environment settings in the main settings file. the following settings are required for production.

### 1. Disable `DEBUG` in your `settings.py`.
Django displays error details in development (`DEBUG = True`) changing this to False indicates that the app is running in production.

```
DEBUG = False
```

### 2. Store sensitive data such as the `SECRET_KEY` in environment variables
we can use `python-dotenv` to load environment variables from `.env` file

```bash
pip install python-dotenv
```

update `settings.py`

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv('APP_SECRET_KEY')

# if you are using emails
EMAIL_HOST_PASSWORD = os.getenv('APP_EMAIL_HOST_PASSWORD')
```

Note that you should get a strong secret key with a minimum of 50 characters, you can use the following function to generate a secret key.
run the following function in the Python shell and take the secret key.

```python
import secrets
import string

def generate_secret_key(length=50):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

generate_secret_key()
```

You should save this key and make sure you never lose it to avoid failures on the application

### 3. Update `ALLOWED_HOSTS`
Add your domain name or server IP address. considering we are deploying to elearner.moamin.dev

```python
ALLOWED_HOSTS = ['elearner.moamin.dev'] # add your domain name, or IP address
```

### 4. Add `ADMINS` And `MANAGERS` settings:
these settings specify the admins of the app so that in case anything goes wrong in production an email is sent to the emails in the list with details of error that happened
```python
ADMINS = [
    ("Your Name", "your-email@gmail.com")
]
MANAGERS = ADMINS
```

### 5. Add security settings for production
for more information about HSTS settings see [this document](https://docs.djangoproject.com/en/5.1/ref/settings/#secure-hsts-include-subdomains)
```python
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# if you're using a reverse proxy such as nginx and this is set to True, Django would not redirect HTTP requests from nginx. 
# so we let nginx handle the redirection to HTTPS
# SECURE_SSL_REDIRECT = True # redirect to HTTPS if attempted to access via HTTP

CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
```

### 6. Install django-csp
```bash
pip install django-csp
```
add settings
```python
MIDDLEWARE += ["csp.middleware.CSPMiddleware"]
CSP_STYLE_SRC = ["'self'", "cdn.jsdelivr.net"]
```

### 7. Install `gunicorn`

in development we run the server using `python manage.py runserver` this cannot be used in production as described by Django
we use gunicorn as a server for the application

```bash
pip install gunicorn
```
add `gunicorn.config.py`

```python
import multiprocessing

wsgi_app = "elearner.wsgi:application"
bind = "0.0.0.0:8001"  # Bind to localhost port 8001
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula for workers
worker_class = "sync"  # Default worker class
threads = 2  # Number of threads per worker
timeout = 30  # Time in seconds for a request to complete
accesslog = "/var/log/elearner/gunicorn/access.log"  # Log file for access logs
errorlog = "/var/log/elearner/gunicorn/error.log"  # Log file for error logs
loglevel = "info"  # Logging level: debug, info, warning, error, critical
# Redirect stdout/stderr to log file
capture_output = True
# Daemonize the Gunicorn process (detach & enter background)
daemon = True
```

to start the server with the settings file with the following command

```bash
gunicorn -c gunicorn.config.py
```

or you could start with the default settings

```bash
gunicorn elearner.wsgi:application --bind 0.0.0.0:8000
```

### 8. Ensure migrations are created, static files are collected, all tests are ok, and all deployment checks are passed

```bash
python manage.py makemigrations
python manage.py collectstatic
python manage.py test
python manage.py check --deploy
```

Note that `python manage.py check --deploy` may give you a warning about the `SECURE_SSL_REDIRECT` setting. it's okay, we will handle that via reverse-proxy server (nginx)

### 9. Capture dependencies in `requirements.txt`

```bash
pip freeze > requirements.txt
```

### 10. Add `.gitignore` file

create a file with the name `.gitigore` this file contains paths that should be ignored while committing the changes like .env file must be ignored, and the local database

```
/db.sqlite3
/.env
/staticroot
```

### 11. Commit and Push to your repo

```bash
git add --all
git commit -m "Deployment"
git push origin main
```

## Deploying to AWS lightsail instance

After creating an account on AWS, we [create a lightsail instance](https://docs.aws.amazon.com/lightsail/latest/userguide/getting-started-with-amazon-lightsail.html), assign a [static IP](https://docs.aws.amazon.com/lightsail/latest/userguide/understanding-public-ip-and-private-ip-addresses-in-amazon-lightsail.html?icmpid=docs_console_unmapped) address to the instance, and create [HTTPS rule](https://docs.aws.amazon.com/en_us/lightsail/latest/userguide/understanding-firewall-and-port-mappings-in-amazon-lightsail.html)
then we start deploying our app

### 1. Update the system and install Python, and git

```
sudo apt update
sudo apt install python3.12 python3.12-venv sqlite3 git
```

we can add alias to `python3.12`

```bash
alias py='python3.12'
```

### 2. Create virtual environment and activate it

```bash
py -m venv awsdemo
source bin/activate
```

### 3. Clone your repo

```bash
mkdir src
cd src
git clone https://github.com/moamindev/elearner.git
cd elearner
```

### 4. Install requirements

```bash
pip install -r requirements.txt
```

### 5. Add `.env` file

```bash
sudo vi .env

APP_SECRET_KEY="YOUR-SECRET-KEY"
APP_EMAIL_PASSWORD="YOUR-EMAIL-PASSWORD"
```

### 6. Migrate and load data

```
py manage.py migrate
py manage.py loaddata data.json
```

### 7. Run app server with gunicorn

start app server

```bash
gunicorn -c gunicorn.config.py
```

you can get the process number running on port 8000 using `net-tools` to be able to kill the process if you want to stop the server

```bash
sudo apt install net-tools
sudo netstat -ltup | grep 8000
```

### 8. Install `nginx` as the reverse proxy server

```bash
sudo apt install nginx
```

add nginx settings at `/etc/nginx/sites-available`

```
cd /etc/nginx/sites-available
sudo vi elearner
```
then editor opens you should write the following in the file

```bash
# Disable emitting nginx version in the "Server" response header field
server_tokens off;

# Use site-specific access and error logs
access_log /var/log/nginx/elearner.access.log;
error_log /var/log/nginx/elearner.error.log;

# Redirect HTTP to HTTPS
server {
    server_name elearner.moamin.dev;
    listen 80;
    return 307 https://$host$request_uri;
}

server {
    server_name: elearner.moamin.dev;
    listen 443; # https port

    # Serve static files directly
    location /static/ {
        autoindex on;
        alias /var/www/elearner/static/;
    }

    location /uploads/ {
        autoindex on;
        alias /var/www/elearner/uploads/;
    }

    # Pass on requests to Gunicorn listening at http://localhost:8000
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
    }
}
```

add default server for nginx on both https and http ports. 
first we generate self signed SSL certifcate (not for production, we just use it to listen to ssl port)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/server.key \
    -out /etc/nginx/ssl/server.crt \
    -subj "/CN=<your-ip>"
```

then add the following settings in file `default`

```bash
server_tokens off;

# Return 444 status code & close connection if no Host header present
server {
    listen * default_server;
    listen [::] default_server;
    server_name _;
    return 444;
}

server {
    listen 443 ssl default_server;
    listen [::]:443 default_server;
    server_name _;
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    return 444;
}
```

### 9. Link site to `sites-enabled`
we create our app in `sites-available` directory, we need to link to `sites-enabled` in order to run the server

```bash
sudo ln -s /etc/nginx/sites-available/elearner /etc/nginx/sites-enabled
```

### 10 Check every things is Ok for nginx and start the service

```bash
sudo nginx -t
sudo systemctl start nginx
```

### 11. Install certbot to add SSL certificate

```bash
sudo apt install certbot
sudo certbot --nginx --rsa-key-size 4096 --no-redirect
```
you enter you email address and specify the domain names and SSL certificate would be generated and added to `sites-available/elearner` file
restart nginx service and you should see the you app available at your domain `https://elearner.moamin.dev`

```bash
sudo systemctl restart nginx
```
### 12. Give access to media root and static root and media root

```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/elearner/src/elearner/{uploads,staticfiles}/
sudo chmod -R 755 /home/ubuntu/elearner/src/elearner/{uploads,staticfiles}/
```

restart nginx service

```bash
sudo systemctl restart nginx
```
