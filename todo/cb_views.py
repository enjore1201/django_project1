from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from todo.forms import CommentForm
from todo.models import Todo, Comment


class TodoListView(LoginRequiredMixin, ListView):
    queryset = Todo.objects.all()
    template_name = "todo/todo_list.html"
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )
        return queryset




class TodoDetailView(LoginRequiredMixin, DetailView):
    model = Todo
    template_name = 'todo/todo_info.html'
    queryset = Todo.objects.all().prefetch_related('comments', 'comments__user')

    # def get_queryset(self):
    #     #     queryset = super().get.queryset()
    #     #     return queryset.filter(id__lte=50)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise Http404("해당 To Do를 조회할 권한이 없습니다.")
        return obj

    def get_context_data(self, **kwargs):
        comments = self.object.comments.order_by('-created_at')
        paginator = Paginator(comments, 5)
        context = {
            'todo': self.object.__dict__,
            'comment_form': CommentForm(),
            'page_obj':  paginator.get_page(self.request.GET.get('page'))
        }
        return context

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    template_name = 'todo/todo_create.html'
    fields = ('title', 'description', 'is_completed')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('cbv_todo_list')


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    template_name = 'todo/todo_update.html'
    fields = ( 'title', 'content', 'decription', 'is_completed')

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('cbv_todo_list')

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['message']
    pk_url_kwarg = 'todo_id'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.todo = Todo.objects.get(id=self.kwargs['todo_id'])
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('cbv_todo_info', kwargs={'pk': self.kwargs['todo_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['message']

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise Http404("해당 댓글을 수정할 권한이 없습니다.")
        return obj

    def get_success_url(self):
        return reverse_lazy('cbv_todo_info', kwargs={'pk': self.object.todo.id})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise Http404("해당 댓글을 삭제할 권한이 없습니다.")
        return obj

    def get_success_url(self):
        return reverse_lazy('cbv_todo_info', kwargs={'pk': self.object.todo.id})