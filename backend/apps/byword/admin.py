from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.urls import path, reverse
from django.shortcuts import redirect

from django.http import FileResponse, HttpResponse

from django.conf import settings
from django import forms
from django.db.models import Min

import os
import csv
from openpyxl import Workbook

from .models import Lesson, WordSearch, Word, ScrambleWord
from .models import Music, LessonText, Dictionary, DictionaryOccurrence

from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .services.wordsearch import generate_grid
from .services.pdf import generate_pdf
from .services.png import generate_png

from apps.byword.services.lesson import format_lesson_title
from apps.byword.services.dictionary import suggest_translation
from apps.byword.services.wordsearch import generate_grid


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("number", "name")
    ordering = ("number",)
    search_fields = ("name",)

    def musics_count(self, obj):
        return obj.musics.count()
    musics_count.short_description = "Musics"

    def texts_count(self, obj):
        return obj.texts.count()
    texts_count.short_description = "Texts"


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
    list_display = ("name", "rows", "cols", "created_at")
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
    list_display = ('titulo', 'texto_original', 'texto_embaralhado', 'criado_em')
    search_fields = ('titulo', 'texto_original')
    readonly_fields = ('texto_embaralhado', 'criado_em')


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "lesson")
    search_fields = ("title", "author")
    list_filter = ("lesson__number",)

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

class LessonNumberMixin:
    def lesson_number(self, obj):
        return obj.lesson.number if obj.lesson else "-"
    
    lesson_number.short_description = "Lesson"
    lesson_number.admin_order_field = "lesson__number"

@admin.register(LessonText)
class LessonTextAdmin(LessonNumberMixin, admin.ModelAdmin):
    list_display = ("lesson", "lesson_number")
    search_fields = ("lesson",)
    list_filter = ("lesson",)
    ordering = ("lesson__number",)

    def lesson_number(self, obj):
        return obj.lesson.number if obj.lesson else "-"
    lesson_number.short_description = "Lesson"
    lesson_number.admin_order_field = "lesson__number"


class DictionaryOccurrenceInline(admin.TabularInline):
    model = DictionaryOccurrence
    extra = 0

    readonly_fields = ("lesson", "lesson_number", "origin", "content_object")
    ordering = ("lesson__number",)

    def lesson_number(self, obj):
        return obj.lesson.number if obj.lesson else "-"
    can_delete = False
    lesson_number.short_description = "Lesson"
    lesson_number.admin_order_field = "lesson__number"


class FirstLessonFilter(SimpleListFilter):
    title = "First Lesson"
    parameter_name = "first_lesson"

    def lookups(self, request, model_admin):
        from apps.byword.models import DictionaryOccurrence

        lessons = (
            DictionaryOccurrence.objects
            .values_list("lesson__number", flat=True)
            .distinct()
            .order_by("lesson__number")
        )

        return [(str(l), f"Lesson {l}") for l in lessons]


    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            first_lesson=Min("occurrences__lesson__number")
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

    actions = [
        "translate_missing",
        "export_dictionary_csv",
        "export_dictionary_xlsx",
        "create_scramble_from_words",
        "create_wordsearch_from_words",
        "rebuild_dictionary_from_lessons"
    ]

    def rebuild_dictionary_from_lessons(modeladmin, request, queryset):
        from apps.byword.services.dictionary import sync_dictionary

        for lt in LessonText.objects.all().order_by("lesson__number"):
            sync_dictionary(
                old_text="",
                new_text=lt.text,
                instance=lt,
                origin="lesson_text",
                lesson=lt.lesson
            )

        modeladmin.message_user(request, "Dictionary rebuilt from all lessons.")

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
            occ = obj.occurrences.order_by("lesson__number").first()

            first_lesson = occ.lesson.number if occ else ""
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
            occ = obj.occurrences.order_by("lesson__number").first()

            first_lesson = occ.lesson.number if occ else ""
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
        return qs.annotate(first_lesson=Min("occurrences__lesson__number"))

    ordering = ("verb_en",)

    inlines = [DictionaryOccurrenceInline]

    def first_occurrence(self, obj):
        if obj.first_lesson:
            occ = next(
                (o for o in obj.occurrences.all() if o.lesson.number == obj.first_lesson),
                None
            )
            if occ:
                return f"{occ.lesson.number} ({occ.origin})"
        return "-"
    
    first_occurrence.admin_order_field = "first_lesson"
    
    first_occurrence.short_description = "First occurrence"


    def create_scramble_from_words(modeladmin, request, queryset):
        # from apps.scrambleword.models import ScrambleWord  # ajuste se necessário

        if not queryset.exists():
            modeladmin.message_user(request, "No words selected.", level="error")
            return

        # pegar lição (menor ocorrência)
        queryset = queryset.annotate(                                                                                                       
            first_lesson=Min("occurrences__lesson__number")
        )

        lesson = min([
            obj.first_lesson for obj in queryset if obj.first_lesson
        ])
        lesson_obj = Lesson.objects.filter(number=lesson).first()                                                                                                           
        words = [obj.verb_en for obj in queryset]

        text = " ".join(words)

        scramble = ScrambleWord.objects.create(
            titulo=format_lesson_title(lesson_obj) or "Scramble",
            texto_original=text
        )

        messages.success(request, "ScrambleWord criado com sucesso.")
        url = reverse(
            f"admin:{scramble._meta.app_label}_{scramble._meta.model_name}_change",
            args=[scramble.id]
        )

        return redirect(url)
        
    

    create_scramble_from_words.short_description = "Create ScrambleWords from selection"

    def create_wordsearch_from_words(modeladmin, request, queryset):
        if not queryset.exists():
            modeladmin.message_user(request, "No words selected.", level="error")
            return

        # 🔹 limitar quantidade de palavras
        unique_words = set(obj.verb_en.strip().lower() for obj in queryset)
        total_words = len(unique_words)

        if total_words < 3 or total_words > 23:
            modeladmin.message_user(
                request,
                f"Select between 3 and 22 word (currently: {total_words}).",
                level="error"
            )
            return

        queryset = queryset.annotate(
            first_lesson=Min("occurrences__lesson__number")
        )

        lessons = [obj.first_lesson for obj in queryset if obj.first_lesson]

        if not lessons:
            modeladmin.message_user(request, "No lesson found.", level="error")
            return

        if len(set(lessons)) > 1:
            modeladmin.message_user(
                request,
                "Select words from only one lesson.",
                level="error"
            )
            return

        lesson = min(lessons)
        lesson_obj = Lesson.objects.filter(number=lesson).first()

        # 🔹 cria WordSearch
        wordsearch = WordSearch.objects.create(
            name=f"Lesson {lesson}",
            lesson=lesson_obj
        )

        # 🔹 cria Words
        seen = set()
        words_to_create = []

        for obj in queryset:
            word = obj.verb_en.strip().upper()

            if word in seen:
                continue
            seen.add(word)

            words_to_create.append(
                Word(
                    wordsearch=wordsearch,
                    text=word.upper()
                )
            )

        Word.objects.bulk_create(words_to_create)

        # 🔥 AQUI É O PONTO PRINCIPAL
        # wordsearch.generate_grid()
        generate_grid(wordsearch)
        wordsearch.save(update_fields=["grid", "solution"])

        url = reverse(
            f"admin:{wordsearch._meta.app_label}_{wordsearch._meta.model_name}_change",
            args=[wordsearch.id]
        )

        messages.success(request, "WordSearch criado com sucesso.")

        return redirect(url)
        

    search_fields = ("verb_en", "translation")

    # first_lesson.short_description = "First Lesson"
    # search_fields = ("verb_en", "translation")
    # readonly_fields = ("content_type", "object_id", "content_object", "created_at")
    # ordering = ("lesson_number", "verb_en",)
    list_per_page = 100
    list_filter = (FirstLessonFilter,)

