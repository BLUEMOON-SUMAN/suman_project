from django.db import models

class FAQ(models.Model) :
    question = models.TextField(verbose_name = '질문')
    answer = models.TextField(verbose_name = '대답')
    category = models.CharField(max_length=50, blank=True, null = True, verbose_name = '카테고리')
    is_published = models.BooleanField(default=True, verbose_name='공개 여부')
    
    class Meta :
        verbose_name = '자주하는 질문'
        verbose_name_plural = '질문 목록'

    
    