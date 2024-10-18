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
    

class RuleSet(models.Model): # eg: base_v0.0.1
    '''
    Stores all the constant properties of game object types in one place.
    '''
    name = models.TextField(default="base", max_length=20, help_text='Name')
    version = models.TextField(default="0.0", max_length=20, help_text='version', validators=[validate_version])
    terrains = JSONField(default=dict, blank=True, null=True)
    recipes = JSONField(default=dict, blank=True, null=True)
    units = JSONField(default=dict, blank=True, null=True)
    facilities = JSONField(default=dict, blank=True, null=True)
    items = JSONField(default=dict, blank=True, null=True)
    
    
    def __str__(self):
        """String for representing the object (in Admin site etc.)."""
        return f"{self.name} v{self.version}"
    
