"""
WSGI config for social project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
<<<<<<< HEAD
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
=======
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
>>>>>>> f98a03bb387ce676ea1fbb6a689c3a739dfe7f67
"""

import os

from django.core.wsgi import get_wsgi_application

<<<<<<< HEAD
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social.settings")
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social.settings')
>>>>>>> f98a03bb387ce676ea1fbb6a689c3a739dfe7f67

application = get_wsgi_application()
