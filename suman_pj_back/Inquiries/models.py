from django.db import models

# Create your models here.

class Inquiry(models.Model) :
    name = models.CharField(max_length = 50, verbose_name = '이름')
    affiliation = models.CharField(max_length = 50, blank = True, null = True, verbose_name = '소속')
    phone = models.CharField(max_length = 20, verbose_name = '연락처' )
    email = models.EmailField(verbose_name = '이메일')
    contect = models.TextField(verbose_name = '문의 내용')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = "접수 시간")
    treatment = models.BooleanField(default=False, verbose_name = '처리 여부')

    class Meta :
        verbose_name = "문의"
        verbose_name_plural = "문의 목록"
        ordering = ['-treatment']

    def __str__(self):
        return f'문의: {self.name} ({self.email})'
    
