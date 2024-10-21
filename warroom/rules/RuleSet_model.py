# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

import re

from django.db import models
from django.urls import reverse
from jsonfield import JSONField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
def validate_terrain(value):
    """
    Validates terrain format.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("%(value)s should be a dictionary"),
            params={"value": value},
        )
    
    good_keys = ["desc", "speed_factor", "mitigation_factor", "camo_bonus", "color", "iconURL"]
    for k in value.keys():
        # verify keys
        if k not in good_keys:
            raise ValidationError(
                _("Terrain %(value)s contains unrecognized key: %(k)s"),
                params={"value": value, "k": k},
            )
        
        # check desc is a string
        if(k == "desc"):
            if not isinstance(value[k], str):
                raise ValidationError(
                    _("Terrain %(value)s contains non-string name: %(n)s"), 
                    params={"value": value, "n": value[k]},
            )
        
        # check color
        if(k == "color"):
            if not (re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value[k])):
                raise ValidationError(
                    _("Terrain %(value)s contains invalid color: %(c)s"), 
                    params={"value": value, "c": value[k]},
            )
        
        # check bonuses are floats
        if(k == "mitigation_factor" or k == "speed_factor" or k == "camo_bonus"):
            if not isinstance(value[k], float):
                raise ValidationError(
                    _("Terrain %(value)s contains non-numeric bonus: %(b)s"), 
                    params={"value": value, "b": value[k]},
            )

        # check iconURL is an image (svg, png, or webp)
        if(k == "iconURL"):
            if not (re.search(r'.(png|svg|webp)$', value[k])):
                raise ValidationError(
                    _("Terrain %(value)s contains invalid icon: %(i)s"), 
                    params={"value": value, "i": value[k]},
            )


def validate_terrains_dict(value):
    """
    Validates dictionary of all terrains.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("%(value)s should be a dictionary"),
            params={"value": value},
        )

    for k in value.keys():
        # check name is a string
        if not isinstance(k, str):
            raise ValidationError(
                _("Terrains dictionary %(value)s contains non-string named Terrain: %(n)s"), 
                params={"value": value, "n": value[k]},
            )
        # check terrain itself
        validate_terrain(value[k])


#####################
###### Recipie ######
#####################
def validate_recipe(value, known_equipment, known_facilities):
    """
    Validates recipe format.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("Recipie %(value)s should be a dictionary"),
            params={"value": value},
        )
    
    good_keys = ["product", "ingredients", "production_cost", "facilities", "iconURL"]
    for k in value.keys():
        # verify keys
        if k not in good_keys:
            raise ValidationError(
                _("Recipie %(value)s contains unrecognized key: %(k)s"),
                params={"value": value, "k": k},
            )
        
        # check product is known equipment
        if(k == "product" and value[k] not in known_equipment.keys()):
            raise ValidationError(
                _("Recipie %(value)s contains unknown product: %(p)s"), 
                params={"value": value, "p": value[k]},
            )
        
        # check ingredients is a dict and each ingredient is known equipment with integer quantity
        if(k == "ingredients"):
            if not isinstance(value[k], dict):
                raise ValidationError(
                    _("Recipie %(value)s's ingredients should be a dictionary: %(i)s"), 
                    params={"value": value, "i": value[k]},
            )

            # check each ingredient
            for i in value[k].keys():
                if i not in known_equipment.keys():
                    raise ValidationError(
                        _("Recipie %(value)s has an unknown ingredient: %(i)s"), 
                        params={"value": value, "i": i},
                    )
                if (not isinstance(value[k][i], int) or value[k][i] <= 0):
                    raise ValidationError(
                        _("Recipie %(value)s has non-positive integer quantity for an ingredient: %(q)s %(i)s"), 
                        params={"value": value, "q": value[k][i], "i": i},
                    )
                
        # check production_cost is a positive float
        if(k == "production_cost"):
            if (not isinstance(value[k], float) or value[k] <= 0):
                raise ValidationError(
                    _("Recipie %(value)s has non-positive float production cost: %(c)s"), 
                    params={"value": value, "c": value[k]},
            )

        # check facilities is a list of known facilities
        if(k == "facilities"):
            if not isinstance(value[k], list):
                raise ValidationError(
                    _("Recipie %(value)s's facilities should be a list: %(f)s"), 
                    params={"value": value, "f": value[k]},
            )
            for f in value[k]:
                if f not in known_facilities.keys():
                    raise ValidationError(
                        _("Recipie %(value)s has an unknown facility: %(f)s"), 
                        params={"value": value, "f": f},
                    )

        # check iconURL is an image (svg, png, or webp)
        if(k == "iconURL"):
            if not (re.search(r'.(png|svg|webp)$', value[k])):
                raise ValidationError(
                    _("Recipie %(value)s contains invalid icon: %(i)s"), 
                    params={"value": value, "i": value[k]},
            )



def validate_recipies_dict(value, known_equipment, known_facilities):
    """
    Validates dictionary of all recipies.
    """
    if not isinstance(value, dict):
        raise ValidationError(
            _("%(value)s should be a dictionary"),
            params={"value": value},
        )

    for k in value.keys():
        # check name is a string
        if not isinstance(k, str):
            raise ValidationError(
                _("Recipies dictionary %(value)s contains non-string named Recipie: %(n)s"), 
                params={"value": value, "n": value[k]},
            )
        # check terrain itself
        validate_terrain(value[k], known_equipment, known_facilities)


            
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
    equipment = JSONField(default=dict, blank=True, null=True)
    facilities = JSONField(default=dict, blank=True, null=True)
    
    def validate_recipes_dict_wrapper(self, args):
        """
        Wraps validate_recipies_dict to provide it dicts of equipment and
        facility types present in this RuleSet.
        Requires equipment & facilities to be cleaned first.
        """
        return validate_recipies_dict(
                args,
                known_equipment = self.cleaned_data["equipment"],
                known_facilities = self.cleaned_data["facilities"]
                )
    recipes = JSONField(default=dict, blank=True, null=True, validators=[validate_recipes_dict_wrapper])
    units = JSONField(default=dict, blank=True, null=True)
    items = JSONField(default=dict, blank=True, null=True)
    
    
    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return f"{self.name} v{self.version}"
    
