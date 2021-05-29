from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы',
                             help_text='Введите название группы')
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст записи',
                            help_text='Введите текст записи')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name='posts', blank=True, null=True,
                              verbose_name='Группа',
                              help_text='Выберите группу для записи')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']
        get_latest_by = 'pub_date'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', blank=True,
                             null=False, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments', blank=True,
                               null=False)
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Введите комментарий')
    created = models.DateTimeField('date published', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower', blank=True,
                             null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following', blank=True,
                               null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique following')
        ]
