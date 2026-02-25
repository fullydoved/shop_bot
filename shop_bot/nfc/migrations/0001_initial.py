import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NfcTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(help_text='Tag UID (hex)', max_length=32, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('lost', 'Lost')], default='active', max_length=10)),
                ('written_url', models.URLField(blank=True, help_text='NDEF URL written to this tag')),
                ('last_scanned_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nfc_tags', to='inventory.bin')),
            ],
            options={
                'ordering': ['bin__code'],
            },
        ),
        migrations.CreateModel(
            name='NfcScanLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(help_text='Tag UID at time of scan', max_length=32)),
                ('bin_code', models.CharField(max_length=10)),
                ('source', models.CharField(default='unknown', help_text='How the scan happened: reader, android, web', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('tag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scan_logs', to='nfc.nfctag')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
