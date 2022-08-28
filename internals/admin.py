from django.contrib import admin

from internals.models import *


# Register your models here.
class SlotInline(admin.StackedInline):
    model = AppointmentSlots


class DoctorScheduleTemplateSlotsInline(admin.StackedInline):
    model = DoctorScheduleTemplateSlots


class DoctorScheduleAdmin(admin.ModelAdmin):
    inlines = [SlotInline]


class DoctorScheduleTemplateAdmin(admin.ModelAdmin):
    inlines = [DoctorScheduleTemplateSlotsInline]


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    fields = ['hospital', 'review', 'image', 'department', 'useinmarker', 'equipment', 'user']
    raw_id_fields = ('hospital', 'review')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    fields = ('name', 'x', 'y', 'hospital', "rating")
    raw_id_fields = ('hospital',)


@admin.register(Building)
class DepartmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('hospital',)


@admin.register(WorkingTime)
class WorkingTimeAdmin(admin.ModelAdmin):
    pass


class HospitalWorkingTimeAdmin(admin.TabularInline):
    model = HospitalWorkingTime
    raw_id_fields = ('hospital',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    inlines = (HospitalWorkingTimeAdmin,)


@admin.register(Ambulance)
class DepartmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('hospital',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(DepartmentName, )
admin.site.register(Equipment, )

admin.site.register(EquipmentName, )

admin.site.register(Floors, )
admin.site.register(Nurse, )
admin.site.register(NurseReviews, )
admin.site.register(DoctorReviews, )
admin.site.register(DoctorSchedule, DoctorScheduleAdmin)
admin.site.register(DoctorScheduleTemplate, DoctorScheduleTemplateAdmin)
