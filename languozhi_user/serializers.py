# users/serializers.py
from rest_framework import serializers
from .models import LGZUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LGZUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'password_hash': {'write_only': True},
                        "is_superuser": {'write_only': True},'groups': {'write_only': True},
                        "user_permissions": {'write_only': True}}

    def create(self, validated_data):
        print("validated_data:", validated_data)
        user = LGZUser.objects.create_user(**validated_data)
        return user
