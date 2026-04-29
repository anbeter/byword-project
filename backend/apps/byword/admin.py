from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django.http import FileResponse, Http404
from django.conf import settings

import os

from .models import WordSearch, Word
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .services.wordsearch import generate_grid
from .services.pdf import generate_pdf
from .services.png import generate_png

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