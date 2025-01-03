from rest_framework import serializers
from traits.models import Trait

class TraitSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    trait_name = serializers.CharField(source="name")