from django.urls import path#type: ignore
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review,
        name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/',views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/',
        views.delete_review, name='movies.delete_review'),
    path('wishList/<int:movie_id>/add/',
        views.addWishList, name='movies.addWishList'),
    path('wishList/<int:movie_id>/remove/',
        views.removeWishList, name='movies.removeWishList'),
    path('vote_review/<int:review_id>',
        views.vote_review, name='movies.vote_review'),
    path('<int:id>/vote/', views.vote_movie, name='movies.vote_movie'),
    path('<int:id>/vote_down/', views.vote_movie_down, name='movies.vote_movie_down'),
]