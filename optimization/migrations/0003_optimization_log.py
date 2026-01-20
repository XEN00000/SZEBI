# Generated migration for OptimizationLog model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('optimization', '0002_update_optimization_rule'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptimizationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('running', 'W trakcie'), ('success', 'Sukces'), ('failed', 'Błąd')], default='running', max_length=20)),
                ('action', models.CharField(blank=True, max_length=255)),
                ('affected_devices_count', models.IntegerField(default=0, help_text='Liczba urządzeń, na które wpłynęła operacja')),
                ('message', models.TextField(blank=True, help_text='Opis operacji lub błąd')),
                ('details', models.JSONField(blank=True, default=dict, help_text='Dodatkowe szczegóły operacji')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('rule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='optimization.optimizationrule')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
