from rest_framework import serializers
from .models import Season, Student, Member, Course, Voucher
import base64
import re

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'
        depth = 1
        
class StudentDeclarativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    stud_member_id = serializers.IntegerField(write_only=True)
    stud_season_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Student
        fields = ['stud_id', 'stud_member', 'stud_season', 'stud_member_id', 'stud_season_id', 'seas_final',
                  'seas_ses01','seas_ses02','seas_ses03','seas_ses04','seas_ses05','seas_ses06','seas_ses07',
                  'seas_ses08','seas_ses09','seas_ses10','seas_ses11','seas_ses12']
        depth = 2
        
class StudentPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        
class MemberGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        depth = 2
        
class MemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['cour_id', 'cour_description', 'cour_level', 'cour_material',
                  'alterno', 'cour_status', 'cour_type']

class VoucherCreateSerializer(serializers.ModelSerializer):
    # Campo para recibir base64 desde el frontend
    vouc_image = serializers.CharField(write_only=True)

    class Meta:
        model = Voucher
        fields = ['vouc_id', 'vouc_member', 'vouc_period', 'vouc_image', 'vouc_operation_number', 'vouc_status', 'vouc_comment']
        read_only_fields = ['vouc_id', 'vouc_status']

    def validate_vouc_image(self, value):
        """
        Valida y procesa imagen en base64
        Formato esperado: "data:image/jpeg;base64,/9j/4AAQ..." o solo el base64
        """
        try:
            # Detectar si tiene el prefijo data:image
            if value.startswith('data:image'):
                # Extraer tipo MIME y base64
                match = re.match(r'data:(image/\w+);base64,(.+)', value)
                if not match:
                    raise serializers.ValidationError("Formato de imagen base64 inválido.")

                mime_type = match.group(1)
                base64_data = match.group(2)
            else:
                # Asumir que es base64 puro
                base64_data = value
                mime_type = 'image/jpeg'  # Default

            # Validar tipo MIME
            valid_types = ['image/jpeg', 'image/jpg', 'image/png']
            if mime_type not in valid_types:
                raise serializers.ValidationError(f"Formato no permitido. Solo: JPG, PNG")

            # Decodificar base64
            try:
                image_bytes = base64.b64decode(base64_data)
            except Exception:
                raise serializers.ValidationError("Error al decodificar base64.")

            # Validar tamaño (1MB)
            max_size = 1 * 1024 * 1024
            if len(image_bytes) > max_size:
                size_mb = len(image_bytes) / 1024 / 1024
                raise serializers.ValidationError(f"Archivo muy grande. Máximo: 1MB. Actual: {size_mb:.2f}MB")

            # Retornar diccionario con datos procesados
            return {
                'bytes': image_bytes,
                'mime_type': mime_type,
                'size': len(image_bytes)
            }

        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"Error procesando imagen: {str(e)}")

    def validate_vouc_operation_number(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("El número de operación es requerido.")
        return value.strip()

    def create(self, validated_data):
        # Extraer datos de imagen procesados
        image_data = validated_data.pop('vouc_image')

        # Generar nombre de archivo
        operation_number = validated_data.get('vouc_operation_number')
        extension = 'jpg' if 'jpeg' in image_data['mime_type'] else 'png'
        filename = f"voucher_{operation_number}.{extension}"

        # Crear voucher con imagen en bytes
        voucher = Voucher.objects.create(
            vouc_image=image_data['bytes'],
            vouc_image_name=filename,
            vouc_image_type=image_data['mime_type'],
            **validated_data
        )

        return voucher

class VoucherPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ['vouc_status', 'vouc_comment']

class VoucherGetSerializer(serializers.ModelSerializer):
    # Campo computado para URL de imagen
    vouc_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Voucher
        exclude = ['vouc_image']  # Excluir bytes de la respuesta
        depth = 2

    def get_vouc_image_url(self, obj):
        """Retorna la URL para obtener la imagen"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/ecm/vouchers/image/{obj.vouc_id}')
        return f'/ecm/vouchers/image/{obj.vouc_id}'
