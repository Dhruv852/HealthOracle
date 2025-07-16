from django.db import models
from django.contrib.auth.models import User

class PredictionHistory(models.Model):
    TEST_TYPES = (
        ('heart', 'Heart Disease'),
        ('lung', 'Lung Disease'),
        ('liver', 'Liver Disease'),
        ('diabetes', 'Diabetes'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    risk_percentage = models.FloatField()
    category = models.CharField(max_length=20)
    advice = models.TextField()
    input_data = models.JSONField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_test_type_display()} Prediction"