from django.db import models

class Reward(models.Model):
    title = models.CharField(max_length=200)
    desc = models.TextField()
    price = models.FloatField() 
    partner_name = models.CharField(max_length=100)

    def __str__(self):
        return self.title


