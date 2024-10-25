# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

from django.db import models
from django.utils.translation import gettext_lazy as _

class UnitFeatures(models.TextChoices):
    """
    Static class that holds posible unit features
    and the callback functions implementing them.
    """

    Rear = "Rear", _('Rear area unit')
    Drop = "Drop", _('Droppable from orbit')
    Indirect = "Indir", _('Indirect fire')

    
    @staticmethod
    def Rear_desc():
        return _("Rear units are mostly used as guards for urban strategic facilities and occupation forces. "
                 "They can contest a large territory but don't do well in combat. "
                 "Their Control_radius is doubled.")
    
    @staticmethod
    def Drop_desc():
        return _("Drop toroops can be rapidly inserted into hostile areas far away by launching from a spaceport or an orbital troop carrier. "
                 "Often being the first boots on the ground in any invasion, their insertion method does not leave much room for heavy armor.")
    
    @staticmethod
    def Indirect_desc():
        return _("Indirect fire support units can provide fire on known enemies at quadruple their Control_radius.")