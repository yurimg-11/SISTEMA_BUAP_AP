from django.db.models import *
from django.db import transaction
from sistema_buap_api.serializers import UserSerializer
from sistema_buap_api.serializers import *
from sistema_buap_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from rest_framework.views import APIView # Importamos APIView
from django.shortcuts import get_object_or_404

class AlumnosAll(APIView): # Cambiamos a APIView
    # Verificar si el usuario esta autenticado
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # QUITAMOS EL FILTRO user__is_active = 1 para ver todos los alumnos.
        alumnos = Alumnos.objects.all().order_by("id") 
        lista = AlumnoSerializer(alumnos, many=True).data
        
        return Response(lista, 200)
    
class AlumnosView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    #Obtener alumno por ID
    # TODO: Agregar obtención de alumno por ID
    @transaction.atomic 
    def get(self, request, *args, **kwargs):    
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        alumno_data = AlumnoSerializer(alumno).data
        return Response(alumno_data, 200)   
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Create a profile for the user
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con ID: ": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos del alumno
    # TODO: Agregar actualización de alumnos
    @transaction.atomic
    def put(self, request, *args, **kwargs):        
        alumno = get_object_or_404(Alumnos, id=request.data.get("id"))
        user = alumno.user

        # Actualizar datos del usuario
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.username = request.data.get("email", user.username)
        user.save()

        # Actualizar datos del alumno
        alumno.matricula = request.data.get("matricula", alumno.matricula)
        alumno.curp = request.data.get("curp", alumno.curp).upper()
        alumno.rfc = request.data.get("rfc", alumno.rfc).upper()
        alumno.fecha_nacimiento = request.data.get("fecha_nacimiento", alumno.fecha_nacimiento)
        alumno.edad = request.data.get("edad", alumno.edad)
        alumno.telefono = request.data.get("telefono", alumno.telefono)
        alumno.ocupacion = request.data.get("ocupacion", alumno.ocupacion)
        alumno.save()

        return Response({"Alumno actualizado con ID: ": alumno.id }, 200)   
    
    # Eliminar alumno con delete (Borrar realmente)
    # TODO: Agregar eliminación de alumnos
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            user = alumno.user
            alumno.delete()
            user.delete()
            return Response({"details":"Alumno eliminado"},200)
        except Exception as e:
            return Response({"details":"Error al eliminar alumno: "+str(e)},400)