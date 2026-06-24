from django.db import models


class Benchmark(models.Model):
    age_group = models.CharField(max_length=10)
    sex = models.CharField(max_length=1)
    variable_name = models.CharField(max_length=50)
    mean_value = models.FloatField()

    class Meta:
        unique_together = ('age_group', 'sex', 'variable_name')