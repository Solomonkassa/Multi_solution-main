import os
import environ
from pathlib import Path
#from account import bot
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize environment
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = env.str("SECRET_KEY") 



# Encryption key
ENCRYPTION_KEY = env.str("ENCRYPTION_KEY", default=None) 

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    # Retrieve database credentials from environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE_NAME'),
            'USER': os.environ.get('MYSQL_DATABASE_USER'),
            'PASSWORD': os.environ.get('MYSQL_DATABASE_PASSWORD'),
            'HOST': os.environ.get('MYSQL_DATABASE_HOST'),
            'PORT': os.environ.get('MYSQL_DATABASE_PORT', '3306'),  
        }
    }

# Media settings
MEDIA_ROOT = env.str("MEDIA_ROOT")  
MEDIA_URL = env.str("MEDIA_URL") 

# Static files settings
STATIC_URL = env.str("STATIC_URL", default= MEDIA_URL + "static/")  
STATIC_ROOT = env.str("STATIC_ROOT", default=MEDIA_ROOT + "/static/")  

# External API settings 
GEEZ_SMS = {
    "token": env.str("GEEZ_SMS_KEY"),  
    "url": env.str("GEEZ_SMS_URL", default="https://api.geezsms.com/api/v1/sms/send"), 
}


#TELEGRAM_BOT_WEBHOOK_URL = 'https://jedantechnology.tech/webhook/'
#BOT_TOKEN = os.getenv('BOT_TOKEN')

# Set webhook
#bot.remove_webhook()
#bot.set_webhook(url=TELEGRAM_BOT_WEBHOOK_URL + BOT_TOKEN)