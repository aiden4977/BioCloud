from rest_framework import serializers
from .models import JobUniversal


class JobUniversalSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobUniversal
        fields = '__all__'