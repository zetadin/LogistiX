# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

import re
from typing import Collection

from django.db import models
from django.urls import reverse
from jsonfield import JSONField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from warroom.rules.equipment_categories import EquipmentCategory
from warroom.rules.equipment_features import EquipmentFeatures
from warroom.rules.unit_features import UnitFeatures

# utility functions
def comp2str(x, val):
    """
    Compares two strings in a case-insensitive manner.
    """
    return(x.lower()==val.lower())

def comp2list(x, lst):
    """
    Compares checks if string is in list in a case-insensitive manner.
    """
    return(x.lower() in [v.lower() for v in lst])





# validators for the rulesets
def validate_version(value):
    """
    Validates version format.
    """
    s = value.split(".")
    if(len(s)>3 or len(s)<2):
        raise ValidationError(
            _("%(value)s should be in a format of <major>.<minor>.<patch>"),
            params={"value": value},
        )
           

#####################
###### Terrain ######
#####################
def validate_terrain(value, name):
    """
    Validates terrain format.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Terrain %(name)s should be a dictionary"),
            params={"name": name},
        )
    
    good_keys = ["Desc", "Speed_factor", "Mitigation_factor", "Camo_bonus", "Color", "IconURL"]
    for k in value.keys():
        # verify keys
        if not comp2list(k, good_keys):
            raise ValidationError(
                _("Terrain %(name)s contains unrecognized key: %(k)s"),
                params={"name": name, "k": k},
            )
        
        # check Desc is a string
        if comp2str(k, "Desc"):
            if not isinstance(value[k], str):
                raise ValidationError(
                    _("Terrain %(name)s contains non-string name: %(n)s"), 
                    params={"name": name, "n": value[k]},
            )
        
        # check Color
        if comp2str(k, "Color"):
            if not (re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value[k])):
                raise ValidationError(
                    _("Terrain %(name)s contains invalid Color: %(c)s"), 
                    params={"name": name, "c": value[k]},
            )
        
        # check bonuses are floats
        if comp2list(k, ["Mitigation_factor", "Speed_factor", "Camo_bonus"]):
            if not isinstance(value[k], float):
                raise ValidationError(
                    _("Terrain %(name)s contains non-numeric bonus: %(b)s"), 
                    params={"name": name, "b": value[k]},
            )

        # check IconURL is an image (svg, png, or webp)
        if comp2str(k, "IconURL"):
            if not (re.search(r'.(png|svg|webp)$', value[k])):
                raise ValidationError(
                    _("Terrain %(name)s contains invalid icon: %(i)s"), 
                    params={"name": name, "i": value[k]},
            )


def validate_terrains_dict(value):
    """
    Validates dictionary of all terrains.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Terrains dictionary %(value)s should be a dictionary"),
            params={"value": value},
        )

    for k in value.keys():
        # check name is a string
        if not isinstance(k, str):
            raise ValidationError(
                _("Terrains dictionary %(value)s contains non-string named Terrain: %(k)s"), 
                params={"value": value, "k": k},
            )
        # check terrain itself
        validate_terrain(value[k], k)


#####################
###### Recipie ######
#####################
def validate_recipe(value, name):
    """
    Validates recipe format.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Recipie %(name)s should be a dictionary"),
            params={"name": name},
        )
    
    good_keys = ["product", "ingredients", "production_cost", "facilities", "IconURL"]
    for k in value.keys():
        # verify keys
        if not comp2list(k, good_keys):
            raise ValidationError(
                _("Recipie %(name)s contains unrecognized key: %(k)s"),
                params={"name": name, "k": k},
            )
                
        # check ingredients is a dict
        if comp2str(k, "ingredients"):
            if not isinstance(value[k], dict):
                raise ValidationError(
                    _("Recipie %(name)s's ingredients should be a dictionary: %(i)s"), 
                    params={"name": name, "i": value[k]},
            )

            # check each ingredient
            for i in value[k].keys():
                if (not isinstance(value[k][i], int) or value[k][i] <= 0):
                    raise ValidationError(
                        _("Recipie %(name)s has non-positive integer quantity for an ingredient: %(q)s %(i)s"), 
                        params={"name": name, "q": value[k][i], "i": i},
                    )
                
        # check production_cost is a positive float
        if comp2str(k, "production_cost"):
            if (not isinstance(value[k], float) or value[k] <= 0):
                raise ValidationError(
                    _("Recipie %(name)s has non-positive float production cost: %(c)s"), 
                    params={"name": name, "c": value[k]},
            )

        # check facilities
        if comp2str(k, "facilities"):
            if not isinstance(value[k], list):
                raise ValidationError(
                    _("Recipie %(name)s's facilities should be a list: %(f)s"), 
                    params={"name": name, "f": value[k]},
            )

        # check IconURL is an image (svg, png, or webp)
        if comp2str(k, "IconURL"):
            if not (re.search(r'.(png|svg|webp)$', value[k])):
                raise ValidationError(
                    _("Recipie %(name)s contains invalid icon: %(i)s"), 
                    params={"name": name, "i": value[k]},
            )


def validate_recipies_dict(value):
    """
    Validates dictionary of all recipies.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Recipies dictionary %(value)s should be a dictionary"),
            params={"value": value},
        )

    for k in value.keys():
        # check name is a string
        if not isinstance(k, str):
            raise ValidationError(
                _("Recipies dictionary %(value)s contains non-string named Recipie: %(n)s"), 
                params={"value": value, "n": value[k]},
            )
        # check recipie itself
        validate_recipe(value[k], k)



#######################
###### Equipment ######
#######################
def validate_equipment(value, name):
    """
    Validates equipment format.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Equipment %(name)s should be a dictionary"),
            params={"name": name},
        )
    
    good_keys = ["Category", "HP", "Features",
                 "Speed",                         # km/h; each hex is 0.5 km
                 "IconURL",
                 "DAM_LGT", "DAM_EXP", "DAM_PEN", # damage types
                 "MIT_LGT", "MIT_EXP", "MIT_PEN", # mitigation types
                 "Cammo", "Recon",                # hiding and spotting others
                 "Volume", "Capacity",            # how much room it takes and how much it can carry when driven  
                 ]
    for k in value.keys():
        # verify keys
        if not comp2list(k, good_keys):
            raise ValidationError(
                _("Recipie %(name)s contains unrecognized key: %(k)s"),
                params={"name": name, "k": k},
            )

        # check category is valid
        if comp2str(k, "Category"):
            if value[k] not in EquipmentCategory._value2member_map_:
                raise ValidationError(
                    _("Equipment %(name)s contains invalid category: %(c)s"), 
                    params={"name": name, "c": value[k]},
                )
            
        # check if Features are a list or emptry and that each listed feature is valid
        if comp2str(k, "Features"):
            if not (isinstance(value[k], list) or not bool(value[k])): # not (a list or empty/None/0)
                raise ValidationError(
                    _("Equipment %(name)s contains non-list Feature list: %(f)s"), 
                    params={"name": name, "f": value[k]},
                )
            for f in value[k]:
                if f not in EquipmentFeatures._value2member_map_:
                    raise ValidationError(
                        _("Equipment %(name)s contains unrecognized Feature: %(f)s"), 
                        params={"name": name, "f": f},
                    )
            
            
        # check IconURL is an image (svg, png, or webp)
        if comp2str(k, "IconURL"):
            if not (re.search(r'.(png|svg|webp)$', value[k])):
                raise ValidationError(
                    _("Equipment %(name)s contains invalid icon: %(i)s"), 
                    params={"name": name, "i": value[k]},
                )
            
        # check HP, volume, and capacity are integers > 0
        if comp2list(k, ["HP", "Volume", "Capacity"]):
            if not isinstance(value[k], int):
                raise ValidationError(
                    _("Equipment %(name)s contains non-integer %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
            
        if(comp2str(k, "HP")):
            if value[k] <= 0:
                raise ValidationError(
                    _("Equipment %(name)s contains %(k)s <= 0 : %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
            
        # check speed, DAMs, MITs, Cammo, and Recon are floats or integers
        if comp2list(k, ["speed", "DAM_LGT", "DAM_EXP", "DAM_PEN", "MIT_LGT", "MIT_EXP", "MIT_PEN", "Cammo", "Recon"]):
            if not (isinstance(value[k], float) or isinstance(value[k], int)):
                raise ValidationError(
                    _("Equipment %(name)s contains non-float %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
            
        # check that speed and MITs are not negative
        if comp2list(k, ["speed", "MIT_LGT", "MIT_EXP", "MIT_PEN", "Volume", "Capacity"]):
            if value[k] < 0:
                raise ValidationError(
                    _("Equipment %(name)s contains negative %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
        # DAMs, Cammo, and Recon can be negative if equipment is hampers others
        

        # check that Volume is less than or equal to Capacity
        if comp2list(k, "Volume"):
            if value[k] > value["Capacity"]:
                raise ValidationError(
                    _("Equipment %(name)s contains Volume > Capacity: %(v)s > %(c)s"), 
                    params={"name": name, "v": value[k], "c": value["Capacity"]},
                )
            



def validate_equipment_dict(value):
    """
    Validates dictionary of all equipment.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Equipment dictionary %(value)s should be a dictionary"),
            params={"value": value},
        )

    for k in value.keys():
        # check name is a string
        if not isinstance(k, str):
            raise ValidationError(
                _("Equipment dictionary %(value)s contains non-string named Equipment: %(n)s"), 
                params={"value": value, "n": value[k]},
            )
        # check equipment itself
        validate_equipment(value[k], k)


########################
###### Facilities ######
########################

def validate_facility(value, name):
    """
    Validates facility format.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Facility %(name)s should be a dictionary"),
            params={"name": name},
        )
    
    good_keys = ["Description", "HP", "IconURL",
                 "Production_rate", "Capacity"
                 ]
    
    for k in value.keys():
        # verify keys
        if not comp2list(k, good_keys):
            raise ValidationError(
                _("Facility %(name)s contains invalid key: %(k)s"), 
                params={"name": name, "k": k},
            )
        
        # Description should be a string
        if comp2str(k, "Description"):
            if not isinstance(value[k], str):
                raise ValidationError(
                    _("Facility %(name)s contains non-string Description: %(d)s"), 
                    params={"name": name, "d": value[k]},
                )
            
        # check icon is an image (svg, png, or webp)
        if comp2str(k, "IconURL"):
            if not (re.search(r'.(png|svg|webp)$', value[k])):
                raise ValidationError(
                    _("Facility %(name)s contains invalid icon: %(i)s"),
                    params={"name": name, "i": value[k]},
                )
            
        # check HP, production_rate, and capacity are integers > 0
        if comp2list(k, ["HP", "Capacity"]):
            if not isinstance(value[k], int):
                raise ValidationError(
                    _("Facility %(name)s contains non-integer %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
            if value[k] <= 0:
                raise ValidationError(
                    _("Facility %(name)s contains non-positive integer %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
            
        # check production_rate is not negative float or in
        if comp2str(k, "Production_rate"):
            if not (isinstance(value[k], float) or isinstance(value[k], int)):
                raise ValidationError(
                    _("Facility %(name)s contains non-number %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )
            if value[k] < 0:
                raise ValidationError(
                    _("Facility %(name)s contains negative %(k)s: %(v)s"), 
                    params={"name": name, "k": k, "v": value[k]},
                )



def validate_facilities_dict(value):
    """
    Validates dictionary of all facilities.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Facility dictionary %(value)s should be a dictionary"),
            params={"value": value},
        )

    for k in value.keys():
        # check name is a string
        if not isinstance(k, str):
            raise ValidationError(
                _("Facility dictionary %(value)s contains non-string named Facility: %(n)s"), 
                params={"value": value, "n": value[k]},
            )
        # check facility itself
        validate_facility(value[k], k)

            
###########################
###### RuleSet Model ######
###########################

class RuleSet(models.Model): # eg: base_v0.0.1
    '''
    Stores all the constant properties of game object types in one place.
    '''
    name = models.TextField(default="base", max_length=20, help_text='Name')
    version = models.TextField(default="0.0", max_length=20, help_text='version', validators=[validate_version])
    terrains = JSONField(default=dict, blank=True, null=True, validators=[validate_terrains_dict])
    recipes = JSONField(default=dict, blank=True, null=True, validators=[validate_recipies_dict])
    equipment = JSONField(default=dict, blank=True, null=True, validators=[validate_equipment_dict])
    facilities = JSONField(default=dict, blank=True, null=True, validators=[validate_facilities_dict])
    missions = JSONField(default=dict, blank=True, null=True)
    units = JSONField(default=dict, blank=True, null=True)
    
    
    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return f"{self.name} v{self.version}"
    

    def save(self, *args, **kwargs):
        # Game rules should always be validated before saving
        self.full_clean()

        super(RuleSet, self).save(*args, **kwargs)


    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        """Override Model.full_clean to add custom multi-field validation."""
        # single field validation
        errors = {}
        try:
            super(RuleSet, self).full_clean(exclude, validate_unique, validate_constraints)
        except ValidationError as e:
            errors = e.update_error_dict(errors)
        

        # multi-field validation

        ###### Recipies ######
        # check that each recipie's product, ingredients, and facilities are known
        known_equipment = list(self.equipment.keys())
        known_facilities = list(self.facilities.keys())
        for k in self.recipes.keys():
            # product
            try:
                if self.recipes[k]["product"] not in known_equipment:
                    raise ValidationError(
                        _("Recipie %(name)s has an unknown product: %(p)s"), 
                        params={"name": k, "p": self.recipes[k]["product"]},
                    )
            except ValidationError as e:
                errors = e.update_error_dict(errors)

            # ingredients
            for i in self.recipes[k]["ingredients"]:
                try:
                    if i not in known_equipment:
                        raise ValidationError(
                            _("Recipie %(name)s has an unknown ingredient: %(i)s"), 
                            params={"name": k, "i": i},
                        )
                except ValidationError as e:
                    errors = e.update_error_dict(errors)

            # facilities
            for f in self.recipes[k]["facilities"]:
                try:
                    if f not in known_facilities:
                        raise ValidationError(
                            _("Recipie %(name)s has an unknown facility: %(f)s"), 
                            params={"name": k, "f": f},
                        )
                except ValidationError as e:
                    errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)
        


        ###### Units ######
        # TODO: validate that extra missions are in list of known missions