from django.db import models
from .models import PredictionHistory

class ChatbotSuggestion(models.Model):
    prediction = models.ForeignKey(PredictionHistory, on_delete=models.CASCADE, related_name='suggestions')
    suggestion_text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"Suggestion for {self.prediction.test_type} - {self.prediction.date_created}"