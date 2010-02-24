from stinkomanlevels.main.models import *
from django.contrib import admin

admin_models = (
    Profile,
    Rating,
    Comment,
    Level,
)

map( lambda x: admin.site.register(x), admin_models )
