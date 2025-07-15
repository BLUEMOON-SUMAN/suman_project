from django.db import models


class JobPost(models.Model):
    title = models.CharField(max_length=200, verbose_name = '공고 제목')
    description = models.TextField(verbose_name = '공고 내용')
    posted_date = models.DateTimeField(auto_now_add=True, verbose_name ='등록일')

    class Meta:
        ordering = ['-posted_date']
        verbose_name = '채용공고'
        verbose_name_plural = '채용공고'

    def __str__(self):
        return self.title