from django.shortcuts import render
from django.db import transaction
from sistema_buap_api.serializers import *
from sistema_buap_api.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.http import Http404 

class MateriasAll(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        es_admin = Administradores.objects.filter(user=request.user).exists()
        es_maestro = Maestros.objects.filter(user=request.user).exists()

        if es_admin or es_maestro:
            materias = Materias.objects.all().order_by("nrc").select_related('profesor__user')
            return Response(MateriaSerializer(materias, many=True).data, 200)
        return Response({"detail": "No autorizado"}, 403)

class MateriasExists(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        nrc = request.GET.get("nrc")
        if not nrc:
            return Response({"error": "Parámetro NRC requerido"}, status=400)
        
        exists = Materias.objects.filter(nrc=nrc).exists()
        if exists:
            return Response({"exists": True}, status=200)
        return Response({"exists": False}, status=200)


class MateriasView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        if not Administradores.objects.filter(user=request.user).exists():
             return Response({"detail": "Solo admin"}, 403)
        
        if Materias.objects.filter(nrc=request.data.get("nrc")).exists():
            return Response({"error": "El NRC ya existe"}, 400)

        serializer = MateriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, 201)
        return Response(serializer.errors, 400)

    def get(self, request):
        nrc = request.GET.get("nrc")
        if not nrc:
             return Response({"error": "Parámetro NRC requerido"}, status=400)
             
        materia = get_object_or_404(Materias, nrc=nrc)
        return Response(MateriaSerializer(materia).data, 200)

    # Editar
    @transaction.atomic
    def put(self, request):
        if not Administradores.objects.filter(user=request.user).exists(): return Response(status=403)
        materia = get_object_or_404(Materias, nrc=request.data.get("nrc")) 
        serializer = MateriaSerializer(materia, data=request.data, partial=True) # partial=True permite actualizar solo algunos campos
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, 200)
        return Response(serializer.errors, 400)

    @transaction.atomic
    def delete(self, request):
        if not Administradores.objects.filter(user=request.user).exists(): return Response(status=403)
        nrc = request.GET.get("nrc")
        if not nrc:
             return Response({"error": "Parámetro NRC requerido"}, status=400)
             
        materia = get_object_or_404(Materias, nrc=nrc)
        materia.delete()
        return Response(status=204)