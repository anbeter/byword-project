from django.contrib import admin
from .models import StudentProfile, StudentStatusHistory


class StudentStatusHistoryInline(admin.TabularInline):
    model = StudentStatusHistory
    extra = 0
    ordering = ("-start_date",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "enrollment_number", "is_active", "enrollment_date")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = ("is_active",)

    inlines = [StudentStatusHistoryInline]