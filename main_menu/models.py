from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faction = models.IntegerField(default=0, help_text='faction the player is in')
    credits = models.IntegerField(default=0, help_text='how much money the player has')
    contribution_score = models.IntegerField(default=0, help_text='how much the player has contributed to the war effort')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()