from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from todo.models import Todo


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

    def get_queryset(self):
        queryset = super().get.queryset()
        return queryset.filter(id__lte=50)


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
    fields = ('category', 'title', 'content')

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