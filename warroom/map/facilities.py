from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Chunk

class ProductionFacilityClass(models.TextChoices):
        '''Class of ProductionFacility for enumeration.'''
        ARMS = 'ARM', _('Small arms')
        VEHICLE = 'VEH', _('Vehicle')
        TANK = 'TNK', _('Tank')
        AIR = 'AIR', _('Airplane')
        SHIPYARD = 'SHP', _('Shipyard')
        CHEM = 'CHE', _('Chemical')
        REFINERY = 'REF', _('Refinery')
        PUMP = 'PMP', _('Pump/Derrick')
        IRONWORKS = 'IRO', _('Ironworks')
        OREMINE = 'ORE', _('Ore mine')
        REPAIRYARD = "REP", _('Repair Yard')
        SALVAGEYARD = "SLV", _('Salvage Yard')

class Facility(models.Model):
    """Facility that can make stuff."""

    # Fields
    name = models.TextField(default="Unnamed Facility", max_length=20, help_text='Name') # eg: Tester's Ironworks
    chunk = models.ForeignKey(Chunk, on_delete=models.CASCADE, null=True, help_text='Chunk')
    x = models.IntegerField(default=0, help_text='x')
    y = models.IntegerField(default=0, help_text='y')
    type = models.CharField(max_length=3,
        choices=ProductionFacilityClass.choices,
        default=ProductionFacilityClass.ARMS)
    
    # Metadata
    class Meta:
        ordering = ['name']

    #Methods
    def get_absolute_url(self):
       """Returns the URL to access a particular instance of Map."""
       return reverse('map', args=[str(self.id)])

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name