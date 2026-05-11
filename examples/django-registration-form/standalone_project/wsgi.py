"""WSGI config for standalone Django example."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "standalone_project.settings")

application = get_wsgi_application()
