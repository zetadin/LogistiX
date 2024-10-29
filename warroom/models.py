from django.db import models
from django.urls import reverse
from jsonfield import JSONField
from .map.models import Map
from .map.facilities import ProductionFacilityClass#, Facility
from django.utils.translation import gettext_lazy as _
from warroom.iconedModel import IconedModel
from warroom.rules.equipment_categories import EquipmentCategory
from warroom.rules.RuleSet_model import RuleSet
try:
   from numpy import exp
except:
    from math import exp

def logistic_decay(x,a,k):
    return(1.0-(1.0/(1+exp(-k*(x-a)))))


class Recipe(models.Model): # eg: uniform, rifle, fuel
    '''Describes recipies used in production.'''
    name = models.TextField(default="Unnamed", max_length=20, help_text='Name')
    facilityClass = models.CharField(max_length=3,
        choices=ProductionFacilityClass.choices,
        default=ProductionFacilityClass.ARMS)
    
    ingredients = JSONField(default=dict, blank=True, null=True) # eg {'steel': 3, 'plastic': 1}
    product = models.ForeignKey('SupplyItem', models.CASCADE, null=True, help_text='Product')
    output = models.PositiveSmallIntegerField(default=1, help_text='Number produced')
    cost = models.PositiveSmallIntegerField(default=1, help_text='Production cost')

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name

class SupplyType(models.Model): # eg: uniform, small_arm, fuel
    '''Describes types of suppliable items used in production.'''
    name = models.TextField(default="Unnamed", max_length=20, help_text='Name')

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name
    

class SupplyItem(models.Model): # eg: plate_carrier_0, rifle_0, disel_0
    '''Describes suppliable items used in production.
       Note: treat comsumables as regular supplies to avoid model inheritance issues.
    '''
    name = models.TextField(default="Unnamed", max_length=20, help_text='Name')
    price = models.PositiveIntegerField(default=100, help_text='Base price')
    recipes = models.ManyToManyField(Recipe)
    type = models.ForeignKey('SupplyType', models.CASCADE, null=True, help_text='type')
    tier = models.SmallIntegerField(default=0, help_text='tier') # higher tiera should be used first
    bonuses = JSONField(default=dict, blank=True, null=True) # eg {'penetration_add': 30, "passengers_add": -1}
    salvageChance = models.FloatField(default=0.0, help_text='Salvage chance')
    
    
    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name




class CombatantType(IconedModel): # eg: rifle_inf
    '''Describes types of individual combatants.'''
    name = models.TextField(default="Unnamed", max_length=20, help_text='Name', db_index=True) # eg: rifle_inf, IFV_mg
    entityClass = models.CharField(max_length=3,
        choices=EquipmentCategory.choices,
        default=EquipmentCategory.INFANTRY) # eg: INF, VEH, PLN

    fireRate = models.FloatField(default=1, help_text='Salvos/encounter') # sum over all combatants and round down
    armor = models.PositiveSmallIntegerField(default=0, help_text='Armor thickness (mm)') 
    penetration = models.PositiveSmallIntegerField(default=0, help_text='Penetration (mm)')
    camo = models.SmallIntegerField(default=0, help_text='Camouflage')
    spotting = models.SmallIntegerField(default=0, help_text='Spotting')
    moveSpeed = models.FloatField(default=5.0, help_text='Movement speed (km/h)')
    ammo = models.ForeignKey('SupplyType', models.SET_NULL, null=True, help_text='Ammunition')

    crew = models.PositiveSmallIntegerField(default=1, help_text='Crew size')
    passengers = models.PositiveSmallIntegerField(default=0, help_text='Passenger capacity')
    
    gear_requirements = JSONField(default=dict, blank=True, null=True) # contains SupplyType names
    # eg {'uniform': 1, 'small_arm': 1, 'AT_launcher': 1}

    
    
    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.name
    
    # when updating aCombatant, we need to recalculate the stats and supply requirements
    # of any platoon types that use it
    def save(self, *args, **kwargs):
        super(CombatantType, self).save(*args, **kwargs) # Call models.Model.save()
        # get users of this CombatantType
        items = PlatoonType.objects.filter(composition__contains = self.name)
        for item in items:
            item.calculate_supply_requirements()
            item.save()
    


class PlatoonType(IconedModel):
    """Type of Platoon. Describes unit composition in terms of entities."""

    # Fields
    type = models.TextField(default="Unnamed", max_length=20, help_text='Type', db_index=True) # eg: Infantry, Assault, Heavy Weapons
    composition = JSONField(default=dict, blank=True, null=True) # contains CombatantType names
    # eg {'rifle_inf': 30, 'AT_inf': 4, 'AA_inf': 2, 'MG_inf': 4}
    supply_requirements = JSONField(default=dict, blank=True, null=True)  # contains SupplyType names
    # eg {'uniform': 1, 'small_arm': 1, 'AT_launcher': 1}
    
    # Metadata
    class Meta:
        ordering = ['type']

    # Methods
    #def get_absolute_url(self):
    #    """Returns the URL to access a particular instance of MyModelName."""
    #    return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return self.type
    
    def calculate_supply_requirements(self):
        # add up all the gear needed by combatants
        self.supply_requirements = {}
        for ct_key in self.composition.keys():
            ct = CombatantType.objects.get(name=ct_key) # should only be one
            for gear_key in ct.gear_requirements.keys():
                if(not gear_key in self.supply_requirements.keys()):
                    self.supply_requirements[gear_key]=0
                self.supply_requirements[gear_key] += ct.gear_requirements[gear_key] * self.composition[ct_key]

    def save(self, *args, **kwargs):
        self.calculate_supply_requirements()
        super(PlatoonType, self).save(*args, **kwargs) # Call models.Model.save()
        # update Platoons of this type
        items = Platoon.objects.filter(type = self.id)
        for item in items:
            item.update_supplies_missing()
            item.update_supplies_in_use()
            item.update_stats()
            item.save()
        


#######################################
# Entities modifiable through bonuses #
#######################################

class Platoon(models.Model):
    # coordinates
    map = models.ForeignKey('MAP', models.CASCADE, null=True, help_text='Map', db_index=True)
    x = models.IntegerField(default=0, help_text='x')
    y = models.IntegerField(default=0, help_text='y')

    faction = models.IntegerField(default=0, help_text='faction the platoon is in')

    number = models.PositiveSmallIntegerField(default=1, help_text='Number of Platoon in Company')  # eg: 3rd
    type = models.ForeignKey('PlatoonType', models.CASCADE, help_text='Type')

    supplies_in_use = JSONField(default=dict, blank=True, null=True)  # contains SupplyItems for each SupplyType
    # eg {'uniform':   {'plate_carrier_0': 40},
    #     'small_arm': {'rifle_1':10, 'rifle_0':30}
    #    }

    supplies_missing = JSONField(default=dict, blank=True, null=True)  # contains SupplyTypes
    # eg {'uniform': 1, 'small_arm': 1, 'AT_launcher': 1}


    average_supply_bonuses = JSONField(default=dict, blank=True, null=True)  # contains bonuses for each SupplyType
    # eg {'uniform':   {'armor_add': 0, 'speed_add': 0},
    #     'small_arm': {'fireRate_add': 0.05}
    #    }

    available_ammo = JSONField(default=dict, blank=True, null=True)  # contains AmmoItems by AmmoType
    # eg {'7.62mm':   {'7.62mm_standard': 100, '7.62mm_incendriary': 20} }

    # average values over Combatants
    camo = models.SmallIntegerField(default=0, help_text='Camouflage')
    spotting = models.SmallIntegerField(default=0, help_text='Spotting')
    moveSpeed = models.FloatField(default=5.0, help_text='Movement speed (km/h)')

    # stance = models.ForeignKey('Stance', models.SET_NULL, help_text='Stance')
    # position = models.ForeignKey('Hex', models.CASCADE, help_text='Map Hex')

    def __str__(self):
        """String for representing the Platoon object (in Admin site etc.)."""
        name=str(self.number)
        if(self.number==0): name="HQ"
        elif(self.number==1): name+="st"
        elif(self.number==2): name+="nd"
        elif(self.number==3): name+="rd"
        else: name+="th"
        name+= " " + self.type.type + " Platoon"
        return name

    def update_supplies_missing(self):
        pass

    def update_supplies_in_use(self):
        pass

    def update_stats(self):
        pass

    def get_spotted_JSON(self, enemy_spoting):
        '''Get JSON dictionary of spotted combatants given an enemy spotting score.'''

        # get hiding chance from curent map hex
        # spotted_chance = hiding_chance * logistic_decay(x=enemy_spoting, a=self.camo, k=4/self.camo)

        return({});