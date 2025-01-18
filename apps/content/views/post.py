from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.content.models import Post, UserInteraction
from apps.content.serializers.post import ListPostsSerializer, PostSerializer, AdminListPostsSerializer
from apps.shared.general import GENERAL_SUCCESS_RESPONSE
from apps.shared.literals import CREATE_POST, DELETE_POST, UPDATE_POST
from apps.shared.utils.permissions import UserPermission


class PostViewSet(viewsets.GenericViewSet):
    queryset = Post.objects.all()

    def get_permissions(self):
        permissions = {
            'create': CREATE_POST,
            'update': UPDATE_POST,
            'destroy': DELETE_POST,
        }
        user_permission = permissions.get(self.action, None)
        if user_permission:
            return [IsAuthenticated(), UserPermission(user_permission)]
        return [IsAuthenticated()]

    def create(self, request):
        serializer = PostSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk, is_active=True, post_type='feed')
            serializer = PostSerializer(post, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk, is_active=True, post_type='feed')
            post.soft_delete(owner=request.user)
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        user = request.user
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        query = request.query_params.get('query')
        branch = request.query_params.get('branch', "").lower()

        posts = Post.objects.filter(is_active=True, post_type='feed')
        if branch == "true":
            posts = posts.filter(branch=request.user.branch)

        if query:
            posts = posts.filter(
                Q(content__icontains=query)
            )
        posts = posts.annotate(
            is_favorite=Exists(
                UserInteraction.objects.filter(
                    post=OuterRef('pk'),
                    user=user,
                    interaction_type='favorite'
                )
            ),
            liked=Exists(
                UserInteraction.objects.filter(
                    post=OuterRef('pk'),
                    user=user,
                    interaction_type='like'
                )
            )
        ).order_by('-date_created')

        paginator = Paginator(posts, page_size)
        page_obj = paginator.get_page(page)

        results = ListPostsSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': posts.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None):
        user = request.user
        try:
            post = Post.objects.filter(pk=pk, is_active=True, post_type='feed').annotate(
                is_favorite=Exists(
                    UserInteraction.objects.filter(
                        post=OuterRef('pk'),
                        user=user,
                        interaction_type='favorite'
                    )
                ),
                liked=Exists(
                    UserInteraction.objects.filter(
                        post=OuterRef('pk'),
                        user=user,
                        interaction_type='like'
                    )
                )
            ).order_by('-date_created').first()
            serializer = ListPostsSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='admin-list')
    def admin_list(self, request):
        user = request.user
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        query = request.query_params.get('query')
        branch = request.user.branch

        posts = Post.objects.filter(is_active=True, post_type='feed', branch=branch)

        if query:
            posts = posts.filter(
                Q(content__icontains=query)
            )

        paginator = Paginator(posts, page_size)
        page_obj = paginator.get_page(page)

        results = AdminListPostsSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': posts.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )
