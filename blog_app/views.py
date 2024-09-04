from django.shortcuts import redirect
from django.urls import reverse_lazy

from blog_app.forms import PostForm
from blog_app.models import Post
from django.utils import timezone

from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# function based views
# 90 % CRUD
# class based views


class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        posts = Post.objects.filter(published_at__isnull=False).order_by(
            "-published_at"
        )
        return posts


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        post = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=False)
        return post


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = Post.objects.filter(published_at__isnull=True).order_by(
            "-published_at"
        )
        return queryset


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "draft_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=True)
        return queryset


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy("post-list")

    def form_valid(self, form):
        messages.success(self.request, "Post was deleted successfully.")
        return super().form_valid(form)


# class PostDeleteView(LoginRequiredMixin, View):
#     def get(self, request, pk):
#         post = Post.objects.get(pk=pk)
#         post.delete()
#         return redirect("post-list")


class DraftPublishView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk, published_at__isnull=True)
        post.published_at = timezone.now()
        post.save()
        messages.success(self.request, "Post was published successfully.")
        return redirect("post-detail", pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm
    # success_url = reverse_lazy("post-list")

    def get_success_url(self) -> str:
        return reverse_lazy("draft-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_success_url(self):
        post = self.get_object()
        if post.published_at:
            return reverse_lazy("post-detail", kwargs={"pk": post.pk})
        else:
            return reverse_lazy("draft-detail", kwargs={"pk": post.pk})
