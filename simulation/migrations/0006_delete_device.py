from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('simulation', '0005_alter_deviceconfig_type'),
        ('optimization', '0004_switch_to_deviceconfig'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Device',
        ),
    ]
