from django.db import models

# Create your models here.
class CertificationOrganizationType(models.Model):
    definition = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'certification_organization_type'


class CertificationOrganization(models.Model):
    certification_organtization_type = models.ForeignKey(CertificationOrganizationType)
    abbreviation = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255)
    
    class Meta:
        db_table = 'certification_organization'
