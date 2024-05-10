from django.contrib import admin
from app1.models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Feedback)
admin.site.register(Warning)
admin.site.register(Notice)
