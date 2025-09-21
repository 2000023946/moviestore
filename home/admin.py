from django.contrib import admin

# Register your models here.

from .models import Petition, VotePetition

admin.site.register(Petition)
admin.site.register(VotePetition)   
