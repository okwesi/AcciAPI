from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Exists, F, OuterRef
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.content.models import Post, UserInteraction
from apps.content.serializers.user_interactions import FavoriteSerializer, LikeSerializer, \
    ListFavoritesSerializer, ShareSerializer
from apps.transaction.models import PaymentTransaction


class UserInteractionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'post_id'

    def get_permissions(self):
        return [IsAuthenticated()]

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def like(self, request):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.validated_data['post']
            like = UserInteraction().set_like(request.user, post)
            message = 'Liked' if like else "Unliked"
            return Response({'results': message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def share(self, request):
        serializer = ShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data['post']
        post.shares = F('shares') + 1
        post.save(update_fields=['shares'])
        return Response({'results': 'Shared'}, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def favorite(self, request):
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.validated_data['post']
            favorite = UserInteraction().set_favorite(request.user, post)
            message = 'Added to Favorites' if favorite else 'Removed from Favorite'
            return Response({'results': message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def list_favorites(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        user_favorites = (Post.objects.filter(
            is_active=True,
            post_type='feed',
            interactions__user=request.user,
            interactions__interaction_type='favorite'
        ).annotate(
            liked=Exists(
                UserInteraction.objects.filter(
                    post=OuterRef('pk'),
                    user=request.user,
                    interaction_type='like'
                )
            )
        ).distinct().order_by('-date_created'))

        paginator = Paginator(user_favorites, page_size)
        page_obj = paginator.get_page(page)

        results = ListFavoritesSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': user_favorites.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='activity-summary')
    def user_activity_summary(self, request):
        user = request.user

        # Count liked posts
        liked_posts = UserInteraction.objects.filter(
            user=user,
            interaction_type='like'
        ).count()

        # Count comments made
        comments_made = UserInteraction.objects.filter(
            user=user,
            interaction_type='comment'
        ).count()

        # Count payments made
        payments_made = PaymentTransaction.objects.filter(
            user=user
        ).count()

        # Prepare response
        data = {
            'liked_posts': liked_posts,
            'comments_made': comments_made,
            'payments_made': payments_made
        }

        return Response(data, status=200)
