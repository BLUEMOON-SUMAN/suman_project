from django.db import models

class Category(models.Model) :
    name =models.CharField(max_length=50, unique = True, verbose_name = '카테고리명')
    order = models.IntegerField(default = 0, verbose_name = '정렬 순서')

    class Meta :
        ordering = ['order', 'name']
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리 목록'

    def __str__(self) :
        return self.name

    
class FAQ(models.Model) :
    question = models.TextField(verbose_name = '질문')
    answer = models.TextField(verbose_name = '대답')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null = True, blank = True, verbose_name = '카테고리')
    is_published = models.BooleanField(default=True, verbose_name='공개 여부')
    
    class Meta :
        verbose_name = '자주하는 질문'
        verbose_name_plural = '질문 목록'
