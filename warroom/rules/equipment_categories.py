# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

from django.db import models
from django.utils.translation import gettext_lazy as _

class EquipmentCategory(models.TextChoices):
        '''Class of combatants for enumeration.'''
        INFANTRY = 'INF', _('Infantry')
        VEHICLE = 'VEH', _('Vehicle')
        TANK = 'TNK', _('Tank')
        AIRCRAFT = 'AIR', _('Aircraft')
        SHIP = 'SHP', _('Ship')
        SUPPLY = 'SUP', _('Supply')
        CONSTRUCTION = 'CON', _('Construction material')