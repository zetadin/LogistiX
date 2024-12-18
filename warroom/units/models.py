# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

import random
from django.db import models
from jsonfield import JSONField
from django.core.exceptions import ValidationError
from django.utils.html import mark_safe
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from warroom.rules.RuleSet_model import RuleSet
from warroom.map.models import Map



class Company(models.Model):
    """
    Unit showable on map.
    """
    # coordinates
    map = models.ForeignKey('MAP', models.CASCADE, null=True, help_text='Map', db_index=True)
    x = models.IntegerField(default=0, help_text='x')
    y = models.IntegerField(default=0, help_text='y')

    faction = models.IntegerField(default=0, help_text='Faction the company is in')

    name = models.TextField(default="", help_text='Name') # eg: Tutorial
    type = models.TextField(default="", help_text='Company type')

    active_equipment = JSONField(default=dict, blank=True, null=True,
                                 help_text='Equipment in the field')  # contains contains RuleSet.equipment elements
    all_equipment = JSONField(default=dict, blank=True, null=True,
                              help_text="All the company's equipment")  # contains RuleSet.equipment elements
    
    visible_to = JSONField(default=list, blank=True, null=True,
                           help_text="Factions that can see this company")
    

    # current stats
    HP = models.SmallIntegerField(default=0, help_text='Deployed equipment Hit Points')
    camo = models.FloatField(default=0, help_text='Camouflage')
    spotting = models.FloatField(default=0, help_text='Spotting')
    moveSpeed = models.FloatField(default=0, help_text='Movement speed (km/h)')
    DAM_LGT = models.FloatField(default=0, help_text='Light damage')
    DAM_EXP = models.FloatField(default=0, help_text='Explosive damage')
    DAM_PEN = models.FloatField(default=0, help_text='Penetration damage')
    MIT_LGT = models.FloatField(default=0, help_text='Light mitigation')    
    MIT_EXP = models.FloatField(default=0, help_text='Explosive mitigation')
    MIT_PEN = models.FloatField(default=0, help_text='Penetration mitigation')
    CTRL_RAD = models.FloatField(default=0, help_text='Controlradius') # After this many hexes exerted control decays by half
    CTRL_POW = models.FloatField(default=0, help_text='Control power') # Max control this unit exerts on its curent hex
    

    def __str__(self):
        return self.name
    
    def icon_preview(self):
        """
        Returns HTML for showing icon in admin panel.
        """
        icon = self.map.ruleset.units[self.type]["IconURL"]
        return mark_safe(f'<img src = "{icon}" width = "64"/>')
    
    def icon_preview_tiny(self):
        """
        Returns HTML for showing icon in admin panel.
        """
        icon = self.map.ruleset.units[self.type]["IconURL"]
        return mark_safe(f'<img src = "{icon}" height = "20"/>')

    def update_supplies_missing(self):
        pass

    def update_supplies_in_use(self):
        pass

    def update_stats(self):
        pass

    def gen_name(self):
        if(not self.name):
            bat = random.uniform(1,9999)
            bat_end ="th"
            if(bat%10==1): bat_end="st"
            elif(bat%10==2): bat_end="nd"
            elif(bat%10==3): bat_end="rd" 
            company = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
            self.name = f"{bat_end}{bat} Batallion {company} Company"


    def get_spotted_JSON(self, enemy_spoting):
        '''Get JSON dictionary of spotted combatants given an enemy spotting score.'''

        # get hiding chance from curent map hex
        # spotted_chance = hiding_chance * logistic_decay(x=enemy_spoting, a=self.camo, k=4/self.camo)

        return({});


    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        """Override Model.full_clean to add custom multi-field validation."""
        # single field validation
        errors = {}
        try:
            super().full_clean(exclude, validate_unique, validate_constraints)
        except ValidationError as e:
            errors = e.update_error_dict(errors)


        # single-field validation
        ###### Visiblity ######
        try:
            if not isinstance(self.visible_to, list):
                raise ValidationError(
                    _("Company %(name)s's visible_to should be a list: %(v)s"), 
                    params={"name": self.name, "v": self.visible_to},
                )
            for v in self.visible_to:
                if not (isinstance(v, int) and v>=0):
                    raise ValidationError(
                        _("Company %(name)s's visible_to should be a list of non-negative integers: %(v)s"), 
                        params={"name": self.name, "v": self.visible_to},
                    )
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # multi-field validation

        ###### Type ######
        # check that type is valid under map's ruleset
        try:
            if self.type not in self.map.ruleset.units.keys():
                raise ValidationError(
                    _("Company %(name)s has an unrecognized type: %(t)s"), 
                    params={"name": self.name, "t": self.type},
                )
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)