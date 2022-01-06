#!/usr/bin/python3
import sys
import logging

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/html/camtel-captcha/")

activate_this = '/var/www/html/camtel-captcha/venv/bin/activate_this.py'
with open(activate_this) as file_:
  exec(file_.read(), dict(__file__=activate_this))

from app import app as application
