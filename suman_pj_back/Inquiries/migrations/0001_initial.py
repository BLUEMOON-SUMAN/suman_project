# Generated by Django 5.2.4 on 2025-07-14 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='이름')),
                ('affiliation', models.CharField(blank=True, max_length=50, null=True, verbose_name='소속')),
                ('phone', models.CharField(max_length=20, verbose_name='연락처')),
                ('email', models.EmailField(max_length=254, verbose_name='이메일')),
                ('contect', models.TextField(verbose_name='문의 내용')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='접수 시간')),
                ('treatment', models.BooleanField(default=False, verbose_name='처리 여부')),
            ],
            options={
                'verbose_name': '문의',
                'verbose_name_plural': '문의 목록',
                'ordering': ['-created_at'],
            },
        ),
    ]
