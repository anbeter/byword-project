from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse

from .models import Class, BlockedSchedule, ClassPrice, Enrollment, ClassSchedule
from .services.schedule_service import get_weekly_schedule
from apps.core.choices import DayOfWeek


class ClassScheduleInline(admin.TabularInline):
    model = ClassSchedule
    extra = 0
    fields = (
        "day_of_week",
        "start_time",
        "duration_minutes",
        "end_time",
        "is_active",
    )
    readonly_fields = ("end_time",)
    ordering = ("day_of_week", "start_time")


class ClassPriceInline(admin.TabularInline):
    model = ClassPrice
    extra = 0
    ordering = ("-start_date",)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ["student"]
    ordering = ("-start_date",)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    search_fields = ("name",)

    inlines = [
        ClassScheduleInline, 
        ClassPriceInline, 
        EnrollmentInline
    ]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "class_obj", "status", "start_date", "end_date")
    list_filter = ("status", "class_obj")
    autocomplete_fields = ["student", "class_obj"]


class AcademicAdminSite(admin.AdminSite):
    site_header = "Academic Admin"


admin_site = admin.site  # reutilizando o padrão


def weekly_schedule_view(request):
    schedule = get_weekly_schedule()

    days = [
        (day.value, day.label)
        for day in DayOfWeek
    ]

    context = {
        **admin_site.each_context(request),
        "schedule": schedule,
        "days": days,
    }

    return TemplateResponse(request, "admin/academic/schedule.html", context)


admin_site = admin.site
original_get_urls = admin_site.get_urls

def custom_get_urls():
    urls = original_get_urls()
    custom_urls = [
        path(
            "academic/schedule/",
            admin_site.admin_view(weekly_schedule_view),
            name="academic-schedule",
        ),
    ]
    return custom_urls + urls


admin_site.get_urls = custom_get_urls

@admin.register(BlockedSchedule)
class BlockedScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "day_of_week",
        "start_time",
        "duration_minutes",
        "is_active",
        "reason",
    )

    list_filter = ("day_of_week", "is_active")
    ordering = ("day_of_week", "start_time")

