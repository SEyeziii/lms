# Generated by Django 4.0.6 on 2023-02-22 08:53

from django.db import migrations
import django_pydantic_field._migration_serializers
import django_pydantic_field.fields
import test.models


class Migration(migrations.Migration):

    dependencies = [
        ('test', '0002_test_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='question_list',
            field=django_pydantic_field.fields.PydanticSchemaField(config=None, default=[], schema=django_pydantic_field._migration_serializers.GenericContainer(list, (test.models.Question,))),
        ),
    ]
