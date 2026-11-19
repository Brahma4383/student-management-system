from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations


def hash_passwords(apps, schema_editor):
    """Earlier versions stored passwords as plain text. Hash any that still are."""
    User = apps.get_model('accounts', 'User')
    for user in User.objects.all():
        try:
            identify_hasher(user.password)
        except ValueError:
            user.password = make_password(user.password)
            user.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(hash_passwords, migrations.RunPython.noop),
    ]
