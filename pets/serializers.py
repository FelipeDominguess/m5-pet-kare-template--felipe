from groups.serializers import GroupSerializer
from pets.models import SEX_CHOICES, Pet
from traits.serializers import TraitSerializer
from rest_framework import serializers
from groups.models import Group
from traits.models import Trait


class PetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(choices=SEX_CHOICES.choices, default=SEX_CHOICES.NOT_INFORMED)
    group = GroupSerializer()
    traits = TraitSerializer(many=True)

    def to_internal_value(self, data):
        if "age" in data and isinstance(data["age"], str):
            data["age"] = int(data["age"])

        return super().to_internal_value(data)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'age', 'weight', 'sex', 'group', 'traits']
