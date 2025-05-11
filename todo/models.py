# todo / models.py

from django.contrib.auth import get_user_model # 추가된 부분
from django.db import models


User = get_user_model() # 추가된 부분

# todo 라는 클래스로 django의 models.Model을 상속받고, todo는 django ORM 통해 DB와 자동연결.
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 추가된 부분
    title = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):               # __str__(문자열 메소드)로 객체를 문자열로 표현할때 title 필드의 값을 보여주도록 만듬
        return self.title


class Comment(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}: {self.message}'