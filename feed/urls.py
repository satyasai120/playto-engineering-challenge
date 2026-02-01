from django.urls import path
from .views import (
    PostViewSet,
    PostDetailView,
    CreateCommentView,
    LikePostView,
    LeaderboardView,
)

urlpatterns = [
    # Posts
    path("posts/", PostViewSet.as_view({"get": "list"}), name="post-list"),

    # Post detail with nested comments
    path("posts/<int:post_id>/", PostDetailView.as_view(), name="post-detail"),

    # Create comment
    path("comments/", CreateCommentView.as_view(), name="create-comment"),

    # Like a post
    path("posts/<int:post_id>/like/", LikePostView.as_view(), name="like-post"),

    # Leaderboard
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
]