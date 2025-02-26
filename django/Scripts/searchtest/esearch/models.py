from django.db import models

# Create your models here.


class TempData(models.Model):
    fileName=models.CharField(max_length=200)
    jsonId=models.CharField(max_length=200,default="SC0")
    jsonContent=models.JSONField(verbose_name="JSON Content")
    def __str__(self):
        return self.fileName