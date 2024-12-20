from django.core.paginator import Paginator
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.content.models import Post
from apps.content.serializers.comments import CommentSerializer, ListCommentsSerializer
from apps.shared.general import GENERAL_SUCCESS_RESPONSE


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Post.objects.filter(post_type='comment', is_active=True)

    def get_permissions(self):
        return [IsAuthenticated()]

    def create(self, request):
        serializer = CommentSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            comment = Post.objects.get(pk=pk, post_type='comment', is_active=True)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            comment = Post.objects.get(pk=pk, post_type='comment', is_active=True)
            comment.soft_delete(owner=request.user)
            return Response(GENERAL_SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        parent = request.query_params.get('parent')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        comments = Post.objects.filter(
            post_type='comment',
            is_active=True,
            parent_id=parent
        ).order_by('-date_created')

        paginator = Paginator(comments, page_size)
        page_obj = paginator.get_page(page)

        results = ListCommentsSerializer(
            instance=page_obj.object_list,
            many=True
        ).data

        return Response(
            {
                'results': results,
                'pagination': {
                    'total': comments.count(),
                    'page': page_obj.number,
                    'pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            status=status.HTTP_200_OK
        )
