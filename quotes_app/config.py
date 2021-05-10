import os
import json

PER_PAGE = 5
BEST_TREND = 5

with open('/etc/quotes_app.config.json') as config_file:
    
    config = json.load(config_file)


class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    MAX_CONTENT_LENGTH = int(config.get('MAX_CONTENT_LENGTH'))
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('MAIL_USERNAME')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD')
