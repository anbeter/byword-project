from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import Class, BlockedSchedule, ClassPrice, Enrollment
from .models import ClassSchedule, WeeklyScheduleProxy

# from .services.schedule_service import get_weekly_schedule
from apps.core.choices import DayOfWeek
from .services.schedule_service import get_weekly_schedule_grid

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
    grid, times, occupied = get_weekly_schedule_grid()

    # days = [(d.value, d.label) for d in DayOfWeek]
    days = [(d.value, d.label) for d in DayOfWeek if d.value != 1]

    context = {
        **admin.site.each_context(request),
        "grid": grid,
        "times": times,
        "days": days,
        "occupied": occupied,
    }

    return TemplateResponse(request, "admin/academic/schedule_grid.html", context)


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



class ScheduleAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect("admin:academic-schedule")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(WeeklyScheduleProxy)
class WeeklyScheduleAdmin(admin.ModelAdmin):

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("academic.view_classschedule")

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect("admin:academic-schedule")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "class_obj",
        "day_of_week",
        "start_time",
        "duration_minutes",
        "end_time",
        "is_active",
    )

    list_filter = ("day_of_week", "is_active", "class_obj")
    autocomplete_fields = ["class_obj"]

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        day = request.GET.get("day")
        
        time = request.GET.get("time")

        if day:
            initial["day_of_week"] = int(day)

        if time:
            initial["start_time"] = time

        # sugestão padrão
        initial.setdefault("duration_minutes", 60)

        return initial