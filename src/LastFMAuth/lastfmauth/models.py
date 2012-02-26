# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class LastFMUser( models.Model ):
    user = models.ForeignKey( User, unique=True )
    url = models.CharField( max_length=200, blank=True, null=True )
    image = models.CharField( max_length=200, blank=True, null=True )
    age = models.IntegerField( blank=True, null=True)
    playcount = models.IntegerField( blank=True, null=True )