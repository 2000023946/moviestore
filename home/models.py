from django.db import models

# Create your models here.
class Petition(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def vote_count(self):
        return VotePetition.objects.filter(petition=self).count()

class VotePetition(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Only create vote if it doesn't already exist
        if not VotePetition.objects.filter(user=self.user, petition=self.petition).exists():
            print('Creating vote for', self.user.username, 'on petition', self.petition.name)
            super().save(*args, **kwargs)
        else:
            print('Vote already exists for', self.user.username, 'on petition', self.petition.name)


    def __str__(self):
        return f"{self.user.username} voted for {self.petition.name}"
    