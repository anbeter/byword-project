from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import WordSearch, ScrambleWord
from .serializers import WordSearchSerializer, ScrambleWordSerializer

from .services.wordsearch import generate_grid
from .services.pdf import generate_pdf
from .services.png import generate_png



def ensure_generated(wordsearch):
    if not wordsearch.grid or not wordsearch.solution:
        grid, solution = generate_grid(wordsearch)
        return grid, solution
    return wordsearch.grid, wordsearch.solution


class WordSearchViewSet(viewsets.ModelViewSet):
    queryset = WordSearch.objects.all()
    serializer_class = WordSearchSerializer

    # =========================================================
    # 🧩 GERAR GRID
    # =========================================================
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        wordsearch = self.get_object()

        try:
            grid, solution = generate_grid(wordsearch)

            return Response(
                {
                    "grid": grid,
                    "solution": solution
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    # =========================================================
    # 📄 GERAR PDF
    # =========================================================
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        wordsearch = self.get_object()

        # if not wordsearch.grid:
        #     return Response(
        #         {"error": "Gere o grid primeiro"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        try:
            ensure_generated(wordsearch)
            filename = generate_pdf(wordsearch)

            return Response(
                {
                    "pdf_url": f"/media/pdfs/{filename}"
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # =========================================================
    # 🖼️ GERAR PNG (PUZZLE + SOLUÇÃO)
    # =========================================================
    @action(detail=True, methods=['post'])
    def generate_png(self, request, pk=None):
        wordsearch = self.get_object()

        # if not wordsearch.grid:
        #     return Response(
        #         {"error": "Gere o grid primeiro"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        try:
            ensure_generated(wordsearch)
            files = generate_png(wordsearch)

            return Response(
                {
                    "puzzle_png": f"/media/png/{wordsearch.id}.png",
                    "solution_png": f"/media/png/{wordsearch.id}s.png",
                    "files": files
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScrambleWordViewSet(viewsets.ModelViewSet):
    queryset = ScrambleWord.objects.all().order_by('-criado_em')
    serializer_class = ScrambleWordSerializer