from django.contrib import admin
from .models import FinancialStatus, Payment


@admin.register(FinancialStatus)
class FinancialStatusAdmin(admin.ModelAdmin):
    list_display = ("student", "reference_month", "status", "start_date", "end_date")
    list_filter = ("status",)
    autocomplete_fields = ["student"]
    ordering = ("-reference_month",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "payment_date", "payment_method", "status")
    list_filter = ("payment_method", "status")
    autocomplete_fields = ["student", "class_obj"]

"""class ClassPriceInline(admin.TabularInline):
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

    inlines = [ClassPriceInline, EnrollmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "class_obj", "status", "start_date", "end_date")
    list_filter = ("status", "class_obj")
    autocomplete_fields = ["student", "class_obj"]"""