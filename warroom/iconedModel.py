from django.db import models
from django.utils.html import mark_safe
from django.templatetags.static import static

# base class for models that need an icon so that it will show up in the admin interface
class IconedModel(models.Model):
    iconURL = models.TextField(null=False, default="graphics/absent.svg" , help_text='Icon URL relative to site root')
    def icon_preview(self): 
        return mark_safe(f'<img src = "{static(self.iconURL)}" width = "80"/>')
    class Meta:
        abstract = True