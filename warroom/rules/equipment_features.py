# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

from django.db import models
from django.utils.translation import gettext_lazy as _

class EquipmentFeatures(models.TextChoices):
    """
    Static class that holds posible equipment features
    and callback functions for their efffects on a unit.
    """

    CNC = "CnC", _('Command and Control') # radios, binoculars, etc.
    LOGI = "Logi", _('Logistics and Transportation') # transport trucks, cargo planes, supply drones
    BLD = "Constr", _('Construction and Building') # excavators, cement mixers, shovels & hammers, etc.
    ARTY = "Arty", _('Artillery') # heavy guns that can throw explosives far
    
    @staticmethod
    def CnC():
        pass;

    @staticmethod
    def Logi():
        pass;

    @staticmethod
    def Constr():
        pass;