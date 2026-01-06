"""
ASGI config for itemwzz project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# 作为项目运行在 ASGI 兼容的 Web 服务器上的入口

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itemwzz.settings')

application = get_asgi_application()
