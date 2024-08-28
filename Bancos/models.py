from django.db import models

# Create your models here.
class Bancos(models.Model):
    id_banco = models.AutoField(primary_key=True)
    nombre_banco = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'bancos'