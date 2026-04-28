import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT


def generate_pdf(wordsearch):
    filename = f"{wordsearch.id}.pdf"
    filepath = os.path.join("media/pdfs", filename)

    os.makedirs("media/pdfs", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    # =========================================================
    # 📄 PAGE 1 - CAÇA-PALAVRAS (SEM RESPOSTA)
    # =========================================================
    elements.append(Paragraph(wordsearch.name, styles['Title']))
    elements.append(Spacer(1, 15))

    puzzle_grid = wordsearch.grid

    table1 = Table(puzzle_grid)

    table1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))

    words = [w.text for w in wordsearch.words.all()]
    word_list_text = "<b>Word List:</b><br/>" + "<br/>".join(words)
    word_style = ParagraphStyle(
        name="WordList",
        parent=styles["Normal"],
        alignment=TA_LEFT,
        leading=14
    )
    word_list = Paragraph(word_list_text, word_style)
    # word_list = Paragraph(word_list_text, styles['Normal'])


    layout = Table(
        [
            [table1, word_list]
        ],
        colWidths=[330, 230]
    )

    layout.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 40),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (0, 0), 10),
        ('RIGHTPADDING', (0, 0), (0, 0), 10),
    ]))


    elements.append(layout)

    # quebra de página
    elements.append(PageBreak())

    # =========================================================
    # 📄 PAGE 2 - SOLUÇÃO (COM DESTAQUE)
    # =========================================================

    solution_grid = wordsearch.grid

    # 🔥 monta conjunto de posições que fazem parte das palavras
    highlight = set()

    for word in wordsearch.solution:
        for r, c in word["positions"]:
            highlight.add((r, c))

    table2 = Table(solution_grid)

    style = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]

    # 🔥 aplica destaque apenas nas letras das palavras
    for r in range(len(solution_grid)):
        for c in range(len(solution_grid[r])):
            if (r, c) in highlight:
                style.append(
                    ('BACKGROUND', (c, r), (c, r), colors.yellow)
                )

    table2.setStyle(TableStyle(style))

    elements.append(table2)

    # =========================================================
    # 📄 LISTA DE PALAVRAS
    # =========================================================
    elements.append(Spacer(1, 20))

    words = [w.text for w in wordsearch.words.all()]

    elements.append(Paragraph("Palavras:", styles['Heading2']))
    elements.append(Paragraph(", ".join(words), styles['Normal']))

    doc.build(elements)

    return filename