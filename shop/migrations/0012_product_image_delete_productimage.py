# Generated by Django 4.0.1 on 2022-01-31 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_remove_product_images_productimage_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(default=1, upload_to='static/uploads/products/'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
