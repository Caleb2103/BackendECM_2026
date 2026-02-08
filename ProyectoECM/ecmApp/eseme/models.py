from django.db import models

# Create your models here.
class Zone(models.Model):
    zone_id = models.SmallAutoField(primary_key=True)
    zone_name = models.CharField(max_length=20)

    def __str__(self):
        return self.zone_name
    
class Mode(models.Model):
    mode_id = models.SmallAutoField(primary_key=True)
    mode_name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.mode_name

class Level(models.Model):
    leve_id = models.SmallAutoField(primary_key=True)
    leve_name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.leve_name

class Schedule(models.Model):
    sche_id = models.SmallAutoField(primary_key=True)
    sche_description = models.TextField(blank=True, null=True)
    sche_day = models.SmallIntegerField(blank=True, null=True)
    sche_starttime = models.TimeField(blank=True, null=True)
    sche_endtime = models.TimeField(blank=True, null=True)
    
    def __str__(self):
        return self.sche_description

class Course(models.Model):
    cour_id = models.SmallAutoField(primary_key=True)
    cour_description = models.TextField(blank=True, null=True)
    cour_level = models.ForeignKey('Level', models.DO_NOTHING, db_column='cour_level', blank=True, null=True)
    cour_material = models.TextField(blank=True, null=True)
    alterno = models.TextField(blank=True, null=True)
    cour_status = models.BooleanField(default=True)
    cour_type = models.TextField(blank=True)

    def __str__(self):
        return self.cour_description
        
class Member(models.Model):
    memb_id = models.SmallAutoField(primary_key=True)
    memb_dni = models.TextField()
    memb_typedni = models.CharField(max_length=3, blank=True, null=True)
    memb_name = models.TextField()
    memb_surname = models.TextField()
    memb_mobil = models.TextField()
    memb_role = models.IntegerField(default=1)
    birthdate = models.DateField(blank=True, null=True)
    memb_zone = models.ForeignKey('Zone', models.DO_NOTHING, db_column='memb_zone', blank=True, null=True)

    def __str__(self):
        return self.memb_name
    
    #Definiendo Roles como
    #1: Estudiante --------
    #2: Profesor ----------
    #3: Admin -------------
    
class Period(models.Model):
    peri_id = models.SmallAutoField(primary_key=True)
    peri_description = models.TextField(blank=True, null=True)
    peri_start = models.DateField(blank=True, null=True)
    peri_end = models.DateField(blank=True, null=True)
    peri_status = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.peri_description
        
class Season(models.Model):
    seas_id = models.SmallAutoField(primary_key=True)
    seas_period = models.ForeignKey(Period, models.DO_NOTHING, db_column='seas_period', blank=True, null=True)
    seas_course = models.ForeignKey(Course, models.DO_NOTHING, db_column='seas_course', blank=True, null=True)
    seas_schedule = models.ForeignKey(Schedule, models.DO_NOTHING, db_column='seas_schedule', blank=True, null=True)
    seas_mode = models.ForeignKey(Mode, models.DO_NOTHING, db_column='seas_mode', blank=True, null=True)
    seas_teacher = models.ForeignKey(Member, models.DO_NOTHING, db_column='seas_teacher', blank=True, null=True)
    seas_status = models.BooleanField(blank=True, null=True)
    seas_glosa = models.TextField()
    
    def __str__(self):
        return str(self.seas_id)
    
class Student(models.Model):
    stud_id = models.SmallAutoField(primary_key=True)
    stud_season = models.ForeignKey('Season', models.DO_NOTHING, db_column='stud_season')
    stud_member = models.ForeignKey('Member', models.DO_NOTHING, db_column='stud_member')
    seas_final = models.SmallIntegerField(blank=True, null=True)
    seas_ses01 = models.BooleanField(blank=True, null=True)
    seas_ses02 = models.BooleanField(blank=True, null=True)
    seas_ses03 = models.BooleanField(blank=True, null=True)
    seas_ses04 = models.BooleanField(blank=True, null=True)
    seas_ses05 = models.BooleanField(blank=True, null=True)
    seas_ses06 = models.BooleanField(blank=True, null=True)
    seas_ses07 = models.BooleanField(blank=True, null=True)
    seas_ses08 = models.BooleanField(blank=True, null=True)
    seas_ses09 = models.BooleanField(blank=True, null=True)
    seas_ses10 = models.BooleanField(blank=True, null=True)
    seas_ses11 = models.BooleanField(blank=True, null=True)
    seas_ses12 = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return str(self.stud_id)

class Voucher(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]

    vouc_id = models.SmallAutoField(primary_key=True)
    vouc_member = models.ForeignKey('Member', models.DO_NOTHING, db_column='vouc_member', related_name='vouchers')
    vouc_period = models.ForeignKey('Period', models.DO_NOTHING, db_column='vouc_period', related_name='vouchers')

    # Imagen guardada como bytes en la base de datos
    vouc_image = models.BinaryField()
    vouc_image_name = models.CharField(max_length=255)
    vouc_image_type = models.CharField(max_length=50)  # image/jpeg, image/png

    vouc_operation_number = models.CharField(max_length=50)
    vouc_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    vouc_created_at = models.DateTimeField(auto_now_add=True)
    vouc_updated_at = models.DateTimeField(auto_now=True)
    vouc_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Voucher {self.vouc_operation_number} - {self.vouc_member.memb_name}"

    class Meta:
        ordering = ['-vouc_created_at']
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'