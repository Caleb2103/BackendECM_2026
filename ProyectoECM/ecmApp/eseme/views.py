from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Student, Member, Course, Season, Zone, Period, Voucher
from .serializers import *
from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# ----------------------- STUDENT VIEWS ----------------------- #
class StudentSeasonsAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Student.objects.filter(stud_member__memb_id=user_id)

class StudentCoursesAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        
        queryset = Student.objects.filter(stud_member__memb_id=user_id)
        queryset = queryset.filter(seas_final__gt = 13)
        queryset = queryset.order_by('stud_season__seas_course__cour_level')
        return queryset
    
class StudentListAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    
class TeacherListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        current_teacher = self.kwargs.get('teacher')
        seasons_of_current_teacher = Season.objects.filter(seas_teacher__memb_id=current_teacher)
        students = Student.objects.filter(stud_season__in=seasons_of_current_teacher)
        return students

class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentPutSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def get(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class StudentCreateAPIView(generics.CreateAPIView):
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        return Student.objects.all()
    
    def create(self, request):
        data_new = request.data

        data_new['stud_member_id'] = data_new.get('stud_id')
        data_new['stud_season_id'] = data_new.get('seas_id')
        
        serializer = self.get_serializer(data=data_new)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)

class StudentCreateDeclarativaAPIView(generics.CreateAPIView):
    serializer_class = StudentDeclarativaSerializer

    def create(self, request, *args, **kwargs):
        cursos_data = request.data.get('cursos', [])
        member_id = request.data.get('member_id')

        for curso_data in cursos_data:
            seas_id = Season.objects.filter(seas_course=curso_data['cour_id']).values_list('seas_id', flat=True).first()
            if not seas_id:
                continue

            student_data = {
                'stud_season': seas_id,
                'stud_member': member_id,
                'seas_final': 17,
            }

            serializer = self.get_serializer(data=student_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        return Response(status=status.HTTP_201_CREATED)

# ----------------------- MEMBER VIEWS ----------------------- #
class MemberListAPIView(generics.ListAPIView):
    serializer_class = MemberGetSerializer
        
    def get_queryset(self):
        queryset = Member.objects.all()
        name = self.request.query_params.get('name', None)
        
        if name:
            queryset = queryset.filter(Q(memb_name__icontains=name) | Q(memb_surname__icontains=name))
        
        return queryset

class MemberCreateAPIView(generics.CreateAPIView):
    serializer_class = MemberCreateSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        zone_name = data.get('memb_zone', None)

        if zone_name is not None:
            try:
                zone = Zone.objects.get(zone_name=zone_name)
                data['memb_zone'] = zone.zone_id
            except Zone.DoesNotExist:
                return Response({"error": "Zone does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")  # Registro de depuración
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------- COURSE VIEWS ----------------------- #
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# ----------------------- SEASON VIEWS ----------------------- #
class SeasonListAPIView(generics.ListAPIView):
    serializer_class = SeasonSerializer
    
    def get_queryset(self):
        queryset = Season.objects.all()
        user_id = self.kwargs['user']
        
        queryset = queryset.filter(seas_period__peri_status=True)
        
        return queryset.exclude(student__stud_member=user_id)

# ----------------------- USER VIEWS ----------------------- #
class LoginAPIView(generics.ListAPIView):
    serializer_class = MemberGetSerializer
    
    def get_queryset(self):
        dni_param = self.kwargs.get('dni')
        if dni_param:
            queryset = Member.objects.filter(memb_dni=dni_param)
            if queryset.exists():
                return queryset
            else:
                raise NotFound("Member not found with the provided DNI.", status=status.HTTP_404_NOT_FOUND)
        else:
            raise NotFound("DNI parameter is missing in the URL.", status=400)

# ----------------------- VOUCHER VIEWS ----------------------- #
class VoucherCreateAPIView(generics.CreateAPIView):
    serializer_class = VoucherCreateSerializer

    def create(self, request, *args, **kwargs):
        # Validar campos requeridos
        required_fields = ['vouc_member', 'vouc_period', 'vouc_image', 'vouc_operation_number']
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response(
                {"error": "Campos requeridos faltantes", "missing_fields": missing_fields},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que Member existe
        try:
            member_id = request.data.get('vouc_member')
            Member.objects.get(memb_id=member_id)
        except Member.DoesNotExist:
            return Response(
                {"error": f"El miembro con ID {member_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar que Period existe y está activo
        try:
            period_id = request.data.get('vouc_period')
            period = Period.objects.get(peri_id=period_id)
            if not period.peri_status:
                return Response(
                    {"error": "El periodo seleccionado no está activo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Period.DoesNotExist:
            return Response(
                {"error": f"El periodo con ID {period_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear voucher
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Voucher creado exitosamente", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "Error en la validación", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )


class VoucherListAPIView(generics.ListAPIView):
    serializer_class = VoucherGetSerializer

    def get_queryset(self):
        queryset = Voucher.objects.all()

        # Filtros opcionales por query params
        member_id = self.request.query_params.get('member_id', None)
        if member_id:
            queryset = queryset.filter(vouc_member__memb_id=member_id)

        period_id = self.request.query_params.get('period_id', None)
        if period_id:
            queryset = queryset.filter(vouc_period__peri_id=period_id)

        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(vouc_status=status_filter)

        return queryset


class VoucherDetailAPIView(generics.RetrieveAPIView):
    serializer_class = VoucherGetSerializer
    queryset = Voucher.objects.all()
    lookup_field = 'pk'


def voucher_image_view(request, voucher_id):
    """
    Vista para servir imágenes de vouchers desde la base de datos.
    Retorna la imagen como HttpResponse con el Content-Type apropiado.
    """
    voucher = get_object_or_404(Voucher, vouc_id=voucher_id)

    # Crear respuesta HTTP con la imagen
    response = HttpResponse(voucher.vouc_image, content_type=voucher.vouc_image_type)

    # Agregar header para nombre de archivo
    response['Content-Disposition'] = f'inline; filename="{voucher.vouc_image_name}"'

    return response

