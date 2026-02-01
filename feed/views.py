from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Case, When, IntegerField, F

from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from .services import build_comment_tree


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer


class PostDetailView(APIView):
    def get(self, request, post_id):
        post = Post.objects.select_related("author").get(id=post_id)

        comments = (
            Comment.objects
            .filter(post=post)
            .select_related("author")
        )

        tree = build_comment_tree(comments)

        def serialize_comment(c):
            return {
                "id": c.id,
                "author": c.author.username,
                "content": c.content,
                "children": [
                    serialize_comment(ch)
                    for ch in getattr(c, "children_cached", [])
                ],
            }

        return Response({
            "id": post.id,
            "author": post.author.username,
            "content": post.content,
            "comments": [serialize_comment(c) for c in tree],
        })


class CreateCommentView(APIView):
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data)


class LikePostView(APIView):
    @transaction.atomic
    def post(self, request, post_id):
        try:
            Like.objects.create(user=request.user, post_id=post_id)
        except IntegrityError:
            return Response({"detail": "Already liked"}, status=400)

        return Response({"status": "ok"})


class LeaderboardView(APIView):
    def get(self, request):
        since = timezone.now() - timedelta(hours=24)

        post_likes = (
            Like.objects
            .filter(created_at__gte=since, post__isnull=False)
            .values(user_id=F("post__author"))
            .annotate(total=Sum(
                Case(When(id__isnull=False, then=5), output_field=IntegerField())
            ))
        )

        comment_likes = (
            Like.objects
            .filter(created_at__gte=since, comment__isnull=False)
            .values(user_id=F("comment__author"))
            .annotate(total=Sum(
                Case(When(id__isnull=False, then=1), output_field=IntegerField())
            ))
        )

        scores = {}

        for row in post_likes:
            scores[row["user_id"]] = scores.get(row["user_id"], 0) + row["total"]

        for row in comment_likes:
            scores[row["user_id"]] = scores.get(row["user_id"], 0) + row["total"]

        top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

        return Response(top5)