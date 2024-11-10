import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faction = models.IntegerField(default=0, help_text='Faction the player is in')
    credits = models.IntegerField(default=0, help_text='How much money the player has')
    contribution_score = models.IntegerField(default=0,
                                             help_text='How much the player has contributed to the war effort')
    subsctibed_to_map = models.ForeignKey('warroom.Map', models.SET_NULL, blank=True, null=True, default=None,
                                          help_text='Map player receives updates from')
    last_active = models.DateTimeField(auto_now=False, default=timezone.now)

    # Attributes from related models:
    # maps

    def __str__ (self):
        return '<Profile of %s>' % self.user


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if(not hasattr(instance, 'profile')):
        # create a profile for the user if it is missing
        Profile.objects.create(user=instance)
    instance.profile.save()