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

    
    @staticmethod
    def Rear_desc():
        return _("Rear units are mostly used as guards for urban strategic facilities and occupation forces. "
                 "They can hold a large territory but don't do well in combat.")
    
    @staticmethod
    def Drop_desc():
        return _("Drop toroops can be rapidly inserted into hostile areas far away by launching from a spaceport or an orbital troop carrier. "
                 "Often being the first boots on the ground in any invasion, their insertion method does not leave much room for heavy armor.")