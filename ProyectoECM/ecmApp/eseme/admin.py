from django.contrib import admin
from eseme.models import Zone, Level, Period, Course, Schedule, Season, Mode, Member, Student, Voucher
from django.utils.html import format_html

# Register your models here.
admin.site.register(Zone)
admin.site.register(Level)
admin.site.register(Course)
admin.site.register(Schedule)
admin.site.register(Season)
admin.site.register(Mode)
admin.site.register(Member)
admin.site.register(Student)
admin.site.register(Period)

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['vouc_id', 'vouc_operation_number', 'vouc_member', 'vouc_period', 'vouc_status', 'image_preview', 'vouc_created_at']
    list_filter = ['vouc_status', 'vouc_created_at', 'vouc_period']
    search_fields = ['vouc_operation_number', 'vouc_member__memb_name', 'vouc_member__memb_surname', 'vouc_member__memb_dni']
    readonly_fields = ['vouc_created_at', 'vouc_updated_at', 'image_preview_large']
    ordering = ['-vouc_created_at']

    fieldsets = (
        ('Información del Voucher', {
            'fields': ('vouc_operation_number', 'vouc_image_name', 'vouc_status', 'image_preview_large')
        }),
        ('Relaciones', {
            'fields': ('vouc_member', 'vouc_period')
        }),
        ('Comentarios', {
            'fields': ('vouc_comment',)
        }),
        ('Auditoría', {
            'fields': ('vouc_created_at', 'vouc_updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['aprobar_vouchers', 'rechazar_vouchers']

    def image_preview(self, obj):
        """Miniatura pequeña para la lista"""
        if obj.vouc_id:
            return format_html('<img src="/ecm/vouchers/image/{}" style="max-height: 50px; max-width: 100px;" />', obj.vouc_id)
        return "Sin imagen"
    image_preview.short_description = "Vista Previa"

    def image_preview_large(self, obj):
        """Vista previa grande para el detalle"""
        if obj.vouc_id:
            return format_html('<img src="/ecm/vouchers/image/{}" style="max-width: 400px;" />', obj.vouc_id)
        return "Sin imagen"
    image_preview_large.short_description = "Imagen del Voucher"

    def aprobar_vouchers(self, request, queryset):
        updated = queryset.update(vouc_status='Aprobado')
        self.message_user(request, f'{updated} voucher(s) aprobado(s).')
    aprobar_vouchers.short_description = "Aprobar vouchers seleccionados"

    def rechazar_vouchers(self, request, queryset):
        updated = queryset.update(vouc_status='Rechazado')
        self.message_user(request, f'{updated} voucher(s) rechazado(s).')
    rechazar_vouchers.short_description = "Rechazar vouchers seleccionados"

