from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import numpy as np
import base64
from colorfield.fields import ColorField

# utility functions:
def default_JSON():
    return({})

#settings.configure()

class Map(models.Model):
    """Map consisting of Hexes."""

    # Fields
    name = models.TextField(default="Unnamed map", max_length=20, help_text='Name') # eg: Tutorial

    # Attributes from related models:
    # hex-set
    
    # Metadata
    class Meta:
        ordering = ['name']

    #Methods
    def generate(self):
        pass

    def get_absolute_url(self):
       """Returns the URL to access a particular instance of Map."""
       return reverse('map', args=[str(self.id)])

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name
    

class Hex(models.Model):
    """Type of Platoon. Describes unit composition in terms of entities."""

    # Fields
    x = models.IntegerField(default=0, help_text='x')
    y = models.IntegerField(default=0, help_text='y')
    map = models.ForeignKey('MAP', models.CASCADE, null=True, help_text='Map')
    recon = models.BinaryField(default=base64.b64encode(np.zeros(settings.N_SIDES)), 
                               help_text='recon for many sides')
    control = models.BinaryField(default=base64.b64encode(np.zeros(settings.N_SIDES)), 
                               help_text='control for many sides')
    terrain = models.ForeignKey('Terrain', models.CASCADE, help_text='Terrain')
    improvements = models.JSONField(default=default_JSON, blank=True) # eg ['road_dirt', 'river']

    # Attributes from related models:
    # facility


    # Methods:
    def get_recon(self, side):
        return(np.frombuffer(base64.decodebytes(self.recon), dtype=np.float32)[side])
    
    def get_control(self, side):
        return(np.frombuffer(base64.decodebytes(self.control), dtype=np.float32)[side])

    def set_recon(self, side, value):
        t = np.frombuffer(base64.decodebytes(self.recon), dtype=np.float32)
        t[side] = value
        self.recon = base64.b64encode(t)
    
    def set_control(self, side, value):
        t = np.frombuffer(base64.decodebytes(self.control), dtype=np.float32)
        t[side] = value
        self.control = base64.b64encode(t)
    
    # Metadata
    class Meta:
        ordering = ['x', 'y']

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return f"{self.map}: {self.x} {self.y} {self.terrain}"


class Terrain(models.Model):
    '''Types of Terrain'''
    name = models.TextField(default="Unnamed terrain", max_length=20, help_text='Name', unique=True) # eg: Plains
    speed_factor = models.FloatField(default=1.0, help_text="Scale factor for speed")
    armor_factor = models.FloatField(default=1.0, help_text="Scale factor for armor")
    camo_factor = models.FloatField(default=1.0, help_text="Scale factor for camo")
    color = ColorField(default="#828282", help_text="Color", unique=True)

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name

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


def populate_db_Terrains():
    if(len(Terrain.objects.all())==0):
        plains = Terrain(name="Plains",
                        color="#8ced7b",
                        )
        plains.save()

        forest = Terrain(name="Forest",
                        color="#064a06",
                        speed_factor=0.5,
                        camo_factor=1.5,
                        armor_factor=0.9
                        )
        forest.save()
        
        swamp = Terrain(name="Swamp",
                        color="#3c593e",
                        speed_factor=0.3,
                        camo_factor=1.2,
                        armor_factor=0.7
                        )
        swamp.save()