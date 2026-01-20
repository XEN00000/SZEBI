# Generated migration to update OptimizationRule model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimization', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='optimizationrule',
            name='condition',
        ),
        migrations.AddField(
            model_name='optimizationrule',
            name='conditions',
            field=models.JSONField(blank=True, default=list, help_text='Lista warunków jako JSON'),
        ),
    ]
