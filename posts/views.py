from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from yatube.settings import POST_ON_PAGE
from .forms import PostCreateForm, CommentForm
from .models import Post, Group, User, Follow


def index(request):
    posts = Post.objects.all().select_related('group')
    paginator = Paginator(posts, POST_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    paginator = Paginator(posts, POST_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostCreateForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    count_posts = profile.posts.count()

    posts = profile.posts.all()
    paginator = Paginator(posts, POST_ON_PAGE)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    followed = False
    if request.user.is_authenticated:
        followed = Follow.objects.filter(user=request.user,
                                         author=profile)

    followers = profile.following.count()
    followings = profile.follower.count()

    return render(request, 'profile.html',
                  {'profile': profile, 'count_posts': count_posts,
                   'page': page,
                   'paginator': paginator,
                   'followed': followed,
                   'followers': followers,
                   'followings': followings})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    profile = post.author
    count_posts = profile.posts.count()

    form = CommentForm(None)

    return render(request, 'post.html', {'post': post, 'profile': profile,
                                         'comments': comments, 'form': form,
                                         'count_posts': count_posts})


@login_required
def edit_post(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    profile = post.author

    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)

    form = PostCreateForm(request.POST or None, files=request.FILES or None,
                          instance=post)

    if form.is_valid():
        form.save()
        return redirect('post', username=request.user.username,
                        post_id=post_id)

    return render(
        request, 'edit_post.html', {'form': form, 'post': post},
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id,
                                         author__username=username)
        comment.save()

    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POST_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html",
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)
