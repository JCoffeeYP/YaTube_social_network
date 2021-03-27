from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Post, User


def index(request):
    all_posts = Post.objects.all()
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        './posts/index.html',
        {'page': page,
         'paginator': paginator,
         }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    all_posts = group.posts.all()
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group,
         'page': page,
         'paginator': paginator,
         }
    )


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    user_posts = post_author.posts.all()
    post_count = user_posts.count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        './posts/profile.html',
        {'page': page,
         'author': post_author,
         'post_count': post_count,
         }
    )


@login_required
def add_comment(request, username, post_id):
    user_post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = user_post
        comment.author = request.user
        comment.save()
    return redirect('posts:post', username, post_id)


def post_view(request, username, post_id):
    user_post = get_object_or_404(Post, author__username=username, id=post_id)
    post_count = user_post.author.posts.count()
    form = CommentForm(instance=None)
    return render(
        request,
        './posts/post.html',
        {'author': user_post.author,
         'post': user_post,
         'post_count': post_count,
         'comments': user_post.comments.all(),
         'form': form,
         }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('posts:post', username, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    return render(
        request,
        './posts/new_post.html',
        {'post': post,
         'form': form,
         'is_edit': True,
         })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:index')
    return render(request, './posts/new_post.html', {'form': form, })


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)