# Generated by Django 5.0.3 on 2024-03-25 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_cartitem_cart_remove_cartitem_product_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productmodel',
            old_name='disc',
            new_name='desc',
        ),
    ]
