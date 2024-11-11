from django.db import models
# from django.urls import reverse
# from jsonfield import JSONField
from warroom.map.models import Map
# from .map.facilities import ProductionFacilityClass#, Facility
from django.utils.translation import gettext_lazy as _
# from warroom.iconedModel import IconedModel
# from warroom.rules.equipment_categories import EquipmentCategory
from warroom.rules.RuleSet_model import RuleSet
from warroom.units.models import Company
try:
   from numpy import exp
except:
    from math import exp

def logistic_decay(x,a,k):
    return(1.0-(1.0/(1+exp(-k*(x-a)))))


# class Recipe(models.Model): # eg: uniform, rifle, fuel
#     '''Describes recipies used in production.'''
#     name = models.TextField(default="Unnamed", max_length=20, help_text='Name')
#     facilityClass = models.CharField(max_length=3,
#         choices=ProductionFacilityClass.choices,
#         default=ProductionFacilityClass.ARMS)
    
#     ingredients = JSONField(default=dict, blank=True, null=True) # eg {'steel': 3, 'plastic': 1}
#     product = models.ForeignKey('SupplyItem', models.CASCADE, null=True, help_text='Product')
#     output = models.PositiveSmallIntegerField(default=1, help_text='Number produced')
#     cost = models.PositiveSmallIntegerField(default=1, help_text='Production cost')

#     def __str__(self):
#         """String for representing the object (in Admin site etc.)."""
#         return self.name

# class SupplyType(models.Model): # eg: uniform, small_arm, fuel
#     '''Describes types of suppliable items used in production.'''
#     name = models.TextField(default="Unnamed", max_length=20, help_text='Name')

#     def __str__(self):
#         """String for representing the object (in Admin site etc.)."""
#         return self.name
    

# class SupplyItem(models.Model): # eg: plate_carrier_0, rifle_0, disel_0
#     '''Describes suppliable items used in production.
#        Note: treat comsumables as regular supplies to avoid model inheritance issues.
#     '''
#     name = models.TextField(default="Unnamed", max_length=20, help_text='Name')
#     price = models.PositiveIntegerField(default=100, help_text='Base price')
#     recipes = models.ManyToManyField(Recipe)
#     type = models.ForeignKey('SupplyType', models.CASCADE, null=True, help_text='type')
#     tier = models.SmallIntegerField(default=0, help_text='tier') # higher tiers should be used first
#     bonuses = JSONField(default=dict, blank=True, null=True) # eg {'penetration_add': 30, "passengers_add": -1}
#     salvageChance = models.FloatField(default=0.0, help_text='Salvage chance')
    
    
#     def __str__(self):
#         """String for representing the object (in Admin site etc.)."""
#         return self.name


