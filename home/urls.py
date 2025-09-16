from django.urls import path #type: ignore
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('subs', views.subs, name='home.subs'),
]
