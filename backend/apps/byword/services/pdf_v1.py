import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf(wordsearch):
    os.makedirs("media/pdfs", exist_ok=True)

    filename = f"{wordsearch.id}.pdf"
    filepath = os.path.join("media/pdfs", filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter)

    styles = getSampleStyleSheet()

    # 🔥 estilos customizados
    title_style = ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=1,  # center
        fontSize=22,
        spaceAfter=20,
    )

    wordlist_title_style = ParagraphStyle(
        name="WordListTitle",
        parent=styles["Heading2"],
        spaceAfter=10,
    )

    word_style = ParagraphStyle(
        name="Word",
        parent=styles["Normal"],
        fontSize=12,
        leading=14,
    )

    elements = []

    # =========================
    # DADOS
    # =========================
    grid = wordsearch.grid
    solution = wordsearch.solution
    words = sorted([w.text for w in wordsearch.words.all()])

    # =========================
    # HELPER GRID
    # =========================
    def build_table(grid_data, highlight=False):
        table_data = []
        solution_cells = set()

        if highlight and solution:
            for w in solution:
                for (r, c) in w["positions"]:
                    solution_cells.add((r, c))

        for r, row in enumerate(grid_data):
            new_row = []
            for c, cell in enumerate(row):
                if (r, c) in solution_cells:
                    new_row.append(
                        Paragraph(f'<b><font color="black">{cell}</font></b>', styles["Normal"])
                    )
                else:
                    new_row.append(cell)
            table_data.append(new_row)

        table = Table(
            table_data,
            colWidths=[20] * len(grid_data[0]),
            rowHeights=[20] * len(grid_data)
        )

        style = [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 14),  # 🔥 letras maiores
        ]

        if highlight:
            for r, c in solution_cells:
                style.append(("BACKGROUND", (c, r), (c, r), colors.yellow))

        table.setStyle(TableStyle(style))

        return table

    # =========================
    # HELPER WORD LIST
    # =========================
    def build_word_list():
        word_elements = []

        word_elements.append(Paragraph("<b>Word List:</b>", wordlist_title_style))

        for w in words:
            word_elements.append(Paragraph(w, word_style))

        return word_elements

    # =========================
    # HELPER PÁGINA
    # =========================
    def build_page(grid_data, highlight=False):
        page = []

        # título
        page.append(Paragraph(wordsearch.name, title_style))
        page.append(Spacer(1, 10))

        grid_table = build_table(grid_data, highlight)

        word_list = build_word_list()

        # 🔥 layout lado a lado
        layout = Table([
            [grid_table, word_list]
        ], colWidths=[300, 120])  # ajuste fino aqui

        layout.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        page.append(layout)

        return page

    # =========================
    # PÁGINA 1 (NORMAL)
    # =========================
    elements.extend(build_page(grid, highlight=False))

    elements.append(PageBreak())

    # =========================
    # PÁGINA 2 (SOLUÇÃO)
    # =========================
    elements.extend(build_page(grid, highlight=True))

    # =========================
    # BUILD
    # =========================
    doc.build(elements)

    return filename