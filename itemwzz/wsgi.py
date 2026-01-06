"""
WSGI config for itemwzz project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# 作为项目运行在 WSGI 兼容的Web服务器上的入口

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itemwzz.settings')

application = get_wsgi_application()
