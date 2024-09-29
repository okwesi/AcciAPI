from rest_framework import serializers
from apps.shared.models import CustomTypes


class CustomTypesSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomTypes
        fields = ['id', 'name', 'description', 'category', 'category_name']

    def validate_name(self, value):
        print(value)
        if CustomTypes.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError("An active object with this name already exists.")
        inactive_obj = CustomTypes.objects.filter(name=value, is_active=False).first()
        if inactive_obj:
            return value
        return value

    def get_category_name(self, obj):
        return obj.get_category_name()
