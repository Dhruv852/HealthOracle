from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('HealthOracle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatbotSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')),
                ('suggestion_text', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('prediction', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='suggestions', to='HealthOracle.predictionhistory')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
    ]