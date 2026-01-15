from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name' 
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_staff', 'is_superuser']