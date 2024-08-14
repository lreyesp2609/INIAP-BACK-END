from django.db import models

# Create your models here.
class Provincias(models.Model):
    id_provincia = models.AutoField(primary_key=True)
    provincia = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'provincias'