from django.db import models# type: ignore
from django.contrib.auth.models import User#type: ignore
# Create your models here.

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    votes = models.IntegerField(default=0)
    genre = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
    def de_vote(self):
        self.votes = max(self.votes-1, 0)
        self.save()
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class WishList(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishList')

class WishListItem(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='wishList')
    wishList = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='wishList', null=True)


    def save(self, *args, **kwargs):
        if WishListItem.objects.filter(movie=self.movie, wishList=self.wishList).exists():
            return
        super().save(*args, **kwargs)
