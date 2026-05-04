from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.urls import path
from django.shortcuts import redirect

from django.http import FileResponse, HttpResponse

from django.conf import settings
from django import forms
from django.db.models import Min

import os
import csv
from openpyxl import Workbook

from .models import WordSearch, Word, ScrambleWord
from .models import Music, LessonText, Dictionary, DictionaryOccurrence

from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .services.wordsearch import generate_grid
from .services.pdf import generate_pdf
from .services.png import generate_png
from apps.byword.services.dictionary import suggest_translation


class WordInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        rows = self.instance.rows
        cols = self.instance.cols
        max_size = max(rows, cols)

        for form in self.forms:
            if not form.cleaned_data:
                continue

            word = form.cleaned_data.get('text')

            if word and len(word) > max_size:
                raise ValidationError(
                    f'Palavra "{word}" excede o limite ({max_size}).'
                )

class WordInline(admin.TabularInline):
    model = Word
    formset = WordInlineFormSet
    extra = 1

@admin.register(WordSearch)
class WordSearchAdmin(admin.ModelAdmin):
    inlines = [WordInline]
    list_display = ("id", "name", "rows", "cols", "created_at")
    # list_display = ('name', 'rows', 'cols', 'created_at')
    # change_form_template = "admin/wordsearch_change_form.html"
    change_form_template = "/app/apps/byword/templates/admin/wordsearch_change_form.html"
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:wordsearch_id>/generate-pdf/",
                self.admin_site.admin_view(self.generate_pdf),
                name="wordsearch-generate-pdf",
            ),
            path(
                "<int:wordsearch_id>/generate-png/",
                self.admin_site.admin_view(self.generate_png),
                name="wordsearch-generate-png",
            ),
            path(
                "<int:wordsearch_id>/generate-grid/",
                self.admin_site.admin_view(self.generate_grid),
                name="wordsearch-generate-grid",
            ),
            path(
                "<int:wordsearch_id>/download-pdf/",
                self.admin_site.admin_view(self.download_pdf),
                name="wordsearch-download-pdf",
            ),
            path(
                "<int:wordsearch_id>/download-png/",
                self.admin_site.admin_view(self.download_png),
                name="wordsearch-download-png",
            ),
            path(
                "<int:wordsearch_id>/download-png-solution/",
                self.admin_site.admin_view(self.download_png_solution),
                name="wordsearch-download-png-solution",
            ),
        ]
        return custom_urls + urls

    def generate_grid(self, request, wordsearch_id):
        ws = WordSearch.objects.get(id=wordsearch_id)
        generate_grid(ws)
        self.message_user(request, "Grid gerado com sucesso", messages.SUCCESS)
        return redirect(f"../../{wordsearch_id}/change/")

    def generate_pdf(self, request, wordsearch_id):
        ws = WordSearch.objects.get(id=wordsearch_id)
        generate_pdf(ws)
        self.message_user(request, "PDF gerado com sucesso", messages.SUCCESS)
        return redirect(f"../../{wordsearch_id}/change/")

    def generate_png(self, request, wordsearch_id):
        ws = WordSearch.objects.get(id=wordsearch_id)
        generate_png(ws)
        self.message_user(request, "PNG gerado com sucesso", messages.SUCCESS)
        return redirect(f"../../{wordsearch_id}/change/")

    def download_pdf(self, request, wordsearch_id):
        ws = WordSearch.objects.get(id=wordsearch_id)
        file_path = os.path.join(settings.MEDIA_ROOT, "pdfs", f"{wordsearch_id}.pdf")

        if not os.path.exists(file_path):
            generate_pdf(ws)
            messages.info(request, "PDF não existia e foi gerado automaticamente.")

        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=f"{wordsearch_id}.pdf")

    def download_png(self, request, wordsearch_id):
        ws = WordSearch.objects.get(id=wordsearch_id)
        file_path = os.path.join(settings.MEDIA_ROOT, "png", f"{wordsearch_id}.png")

        if not os.path.exists(file_path):
            generate_png(ws)
            messages.info(request, "PNG não existia e foi gerado automaticamente.")

        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=f"{wordsearch_id}.png")
    
    def download_png_solution(self, request, wordsearch_id):
        filepath = f"media/png/{wordsearch_id}s.png"

        if not os.path.exists(filepath):
            self.message_user(
                request,
                "Gere o PNG antes de baixar a solução.",
                messages.ERROR
            )
            return redirect(f"../../{wordsearch_id}/change/")

        return FileResponse(open(filepath, "rb"), as_attachment=True)
    


@admin.register(ScrambleWord)
class ScrambleWordAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'texto_original', 'texto_embaralhado', 'criado_em')
    search_fields = ('titulo', 'texto_original')
    readonly_fields = ('texto_embaralhado', 'criado_em')


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "number_lesson")
    search_fields = ("title", "author")
    list_filter = ("number_lesson",)

    readonly_fields = ("lyrics_spaces",)


# =========================
# LessonText
# =========================

class LessonTextAdminForm(forms.ModelForm):
    class Meta:
        model = LessonText
        fields = "__all__"
        widgets = {
            "text": forms.Textarea(attrs={"rows": 20, "cols": 220}),
        }

@admin.register(LessonText)
class LessonTextAdmin(admin.ModelAdmin):
    list_display = ("title", "number_lesson")
    search_fields = ("title", "text")
    list_filter = ("number_lesson",)
    ordering = ("number_lesson",)


class DictionaryOccurrenceInline(admin.TabularInline):
    model = DictionaryOccurrence
    extra = 0
    readonly_fields = (
        "origin",
        "number_lesson",
        "content_type",
        "object_id",
        "created_at",
    )

    can_delete = False
    ordering = ("number_lesson",)


class FirstLessonFilter(SimpleListFilter):
    title = "First Lesson"
    parameter_name = "first_lesson"

    def lookups(self, request, model_admin):
        from apps.byword.models import DictionaryOccurrence

        lessons = (
            DictionaryOccurrence.objects
            .values_list("number_lesson", flat=True)
            .distinct()
            .order_by("number_lesson")
        )

        return [(str(l), f"Lesson {l}") for l in lessons]


    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            first_lesson=Min("occurrences__number_lesson")
        )

        value = self.value()

        if value:
            return queryset.filter(first_lesson=int(value))

        return queryset

# =========================
# DICTIONARY
# =========================
@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = (
        "verb_en",
        "translation",
        "first_occurrence",
        "created_at",
    )

    actions = ["translate_missing","export_dictionary_csv","export_dictionary_xlsx"]

    def translate_missing(self, request, queryset):
        count = 0

        for obj in queryset:
            if not obj.translation:
                translation = suggest_translation(obj.verb_en)

                if translation:
                    obj.translation = translation
                    obj.save()
                    count += 1

        self.message_user(
            request,
            f"{count} words translated.",
            messages.SUCCESS
        )

    translate_missing.short_description = "Translate missing words"

    def export_dictionary_xlsx(modeladmin, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "Dictionary"

        # header
        ws.append([
            "Word",
            "Translation",
            "First Lesson",
            "Origin",
        ])

        for obj in queryset:
            occ = obj.occurrences.order_by("number_lesson").first()

            first_lesson = occ.number_lesson if occ else ""
            origin = occ.origin if occ else ""

            ws.append([
                obj.verb_en,
                obj.translation,
                first_lesson,
                origin,
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        filename = f'dictionary_{request.GET.get("first_lesson", "all")}.xlsx'
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response

    export_dictionary_xlsx.short_description = "Export XLSX (filtered)"

    def export_dictionary_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type="text/csv")
        filename = f"dictionary_lesson_{request.GET.get('first_lesson', 'all')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)

        # header
        writer.writerow([
            "Word",
            "Translation",
            "First Lesson",
            "Origin",
        ])

        for obj in queryset:
            # pegar primeira ocorrência
            occ = obj.occurrences.order_by("number_lesson").first()

            first_lesson = occ.number_lesson if occ else ""
            origin = occ.origin if occ else ""

            writer.writerow([
                obj.verb_en,
                obj.translation,
                first_lesson,
                origin,
            ])

        return response

    export_dictionary_csv.short_description = "Export CSV (filtered)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(first_lesson=Min("occurrences__number_lesson"))

    ordering = ("verb_en",)

    inlines = [DictionaryOccurrenceInline]

    def first_occurrence(self, obj):
        # occ = obj.occurrences.order_by("number_lesson").first()
        # if not occ:
        #     return "-"
        # return f"{occ.number_lesson} ({occ.origin})"
        if obj.first_lesson:
            occ = obj.occurrences.filter(number_lesson=obj.first_lesson).first()
            if occ:
                return f"{occ.number_lesson} ({occ.origin})"
        return "-"
    
    first_occurrence.admin_order_field = "first_lesson"
    
    first_occurrence.short_description = "First occurrence"

    search_fields = ("verb_en", "translation")

    # first_lesson.short_description = "First Lesson"
    # search_fields = ("verb_en", "translation")
    # readonly_fields = ("content_type", "object_id", "content_object", "created_at")
    # ordering = ("number_lesson", "verb_en",)
    list_per_page = 100
    list_filter = (FirstLessonFilter,)

