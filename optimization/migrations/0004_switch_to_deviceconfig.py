from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('optimization', '0003_optimization_log'),
        ('simulation', '0002_deviceconfig_simulationconfig_weatherconfig_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpreference',
            name='device',
        ),
        migrations.AddField(
            model_name='userpreference',
            name='device',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='preference', to='simulation.deviceconfig'),
            preserve_default=False,
        ),
    ]
