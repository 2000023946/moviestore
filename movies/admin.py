from django.contrib import admin# type: ignore
from .models import Movie, Review, WishList, WishListItem
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

admin.site.register(Movie, MovieAdmin)

admin.site.register(Review)

admin.site.register(WishList)
admin.site.register(WishListItem)


