from rest_framework import serializers
from apps.shared.models import CustomTypes


class CustomTypesSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomTypes
        fields = ['id', 'name', 'description', 'category', 'category_name']

    def get_category_name(self, obj):
        return obj.get_category_name()
