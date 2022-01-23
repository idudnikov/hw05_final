from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@require_http_methods(["GET"])
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


@require_http_methods(["GET"])
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


@require_http_methods(["GET"])
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    posts_count = page_obj.paginator.count
    context = {
        "author": author,
        "page_obj": page_obj,
        "posts_count": posts_count,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
        context['following'] = following
    return render(request, "posts/profile.html", context)


@require_http_methods(["GET", "POST"])
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user_posts_count = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post=post)
    form = CommentForm()
    context = {
        "post": post,
        "form": form,
        "comments": comments,
        "user_posts_count": user_posts_count,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request):
    groups = Group.objects.all()
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect("posts:profile", request.user)

    context = {"form": form, "groups": groups}
    return render(request, "posts/create_post.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect("posts:post_detail", post_id)

    groups = Group.objects.all()
    is_edit = True
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)

    context = {
        "post_id": post_id,
        "is_edit": is_edit,
        "form": form,
        "groups": groups,
    }
    return render(request, "posts/create_post.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
@require_http_methods(["GET"])
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
@require_http_methods(["GET"])
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:follow_index")


@login_required
@require_http_methods(["GET"])
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:follow_index")
