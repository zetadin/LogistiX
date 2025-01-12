# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from colorfield.fields import ColorField
from main_menu.models import Profile
from LogistiX_backend.fields import UnsignedIntegerField
from warroom.rules.RuleSet_model import RuleSet

# utility functions:
def default_JSON():
    return({})

#settings.configure()

class MapType(models.IntegerChoices):
    Tutorial = 0, _('Tutorial') # Island
    Default = 1, _('Default')
    Coast = 2, _('Coast')

    # support for the "in" expression
    def __contains__(self, c):
        if(isinstance(c, str)):
            return(hasattr(self, c))
        elif(isinstance(c, MapType)):
            return(hasattr(self, c.name))
        else:
            return(False)


class Map(models.Model):
    """Map consisting of Hexes."""

    # Fields
    name = models.TextField(default="Unnamed map", max_length=100, help_text='Name') # eg: Tutorial
    profiles = models.ManyToManyField(Profile, related_name="maps", help_text='Profiles of users that are allowed on this map')
    seed = UnsignedIntegerField(default=0, help_text='Map generation seed')
    type = UnsignedIntegerField(default=MapType.Tutorial, choices=MapType.choices, help_text='MapType this map is generated as')
    sideLen = UnsignedIntegerField(default=10, help_text='Number of hexes on a side')
    ruleset = models.ForeignKey(RuleSet, models.CASCADE, null=False, help_text='Ruleset', default=RuleSet.get_default_pk())
    active = models.BooleanField(default=False, help_text='Should simulations be running on this map?')
    # subscribers = models.ManyToManyField(Profile, related_name="subscribed_to_maps", help_text='Profiles that are receiving updates from this map')


    # Attributes from related models:
    
    # Metadata
    class Meta:
        ordering = ['name']

    #Methods
    def get_absolute_url(self):
       """Returns the URL to access a particular instance of Map."""
       return reverse('map', args=[str(self.id)])

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return f"{self.name:.20}"
    
class Chunk(models.Model):
    """A 32x32 block of hexes."""
    x = models.IntegerField(default=0, help_text='x')
    y = models.IntegerField(default=0, help_text='y')
    map = models.ForeignKey('MAP', models.CASCADE, null=True, help_text='Map')
    data = models.JSONField(default=default_JSON, blank=True)

    # Metadata
    class Meta:
        ordering = ['x', 'y']

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return f"{str(self.map)}: chunk {self.x} {self.y}"
    

class Improvement(models.Model):
    '''Types of Improvement'''
    name = models.TextField(default="Unnamed improvement", max_length=20, help_text='Name', unique=True) # eg: Plains
    speed_factor = models.FloatField(default=1.0, help_text="Scale factor for speed")
    armor_factor = models.FloatField(default=1.0, help_text="Scale factor for armor")
    camo_factor = models.FloatField(default=1.0, help_text="Scale factor for camo")
    color = ColorField(default="#828282", help_text="Color", unique=True)

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name
