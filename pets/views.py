from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .serializers import PetSerializer
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer
from .models import Pet
from traits.models import Trait
from groups.models import Group


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:

        trait_name = request.query_params.get('trait')
        if trait_name:
            pets = Pet.objects.filter(traits__name=trait_name)
        else:
            pets = Pet.objects.all()

        self.paginate_queryset(pets, request)

        serializer = PetSerializer(pets, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trait_data = serializer.validated_data.pop("traits")
        group_data = serializer.validated_data.pop("group")
        
        group_object = Group.objects.filter(
            scientific_name__iexact=group_data["scientific_name"]).first()

        if not group_object:
            group_object = Group.objects.create(**group_data)

        pet_object = Pet.objects.create(
            **serializer.validated_data, group=group_object)

        for trait in trait_data:
            trait_object = Trait.objects.filter(
                name__iexact=trait["name"]).first()

            if not trait_object:
                trait_object = Trait.objects.create(**trait)

            pet_object.traits.add(trait_object)

        serializer = PetSerializer(pet_object)

        return Response(serializer.data, status.HTTP_201_CREATED)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        trait_data: list = serializer.validated_data.pop("traits", None)
        group_data: dict = serializer.validated_data.pop("group", None)

        if trait_data:
            new_traits = []
            for trait in trait_data:
                try:
                    trait_update = Trait.objects.get(
                        name__iexact=trait["name"])
                except Trait.DoesNotExist:
                    trait_update = Trait.objects.create(**trait)
                new_traits.append(trait_update)

            pet.traits.set(new_traits)

        if group_data:
            try:
                group_update = Group.objects.get(
                    scientific_name=group_data["scientific_name"])
            except Group.DoesNotExist:
                group_update = Group.objects.create(**group_data)
            pet.group = group_update

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
