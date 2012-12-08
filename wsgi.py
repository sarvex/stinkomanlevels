import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
new_path = os.path.dirname(__file__)
new_path2 = os.path.join(new_path, "..")
if new_path not in sys.path:
    sys.path.append(new_path)
if new_path2 not in sys.path:
    sys.path.append(new_path2)
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
