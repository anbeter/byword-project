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
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# 🎨 CONFIGURAÇÕES
# =========================
CELL_SIZE = 22

INTERSECTION_COLOR = colors.purple
EXCESS_COLOR = colors.grey

WORD_COLORS = [
    colors.yellow,
    colors.lightblue,
    colors.lightgreen,
    colors.pink,
    colors.orange,
    colors.lavender,
    colors.beige,
    colors.khaki,
    colors.cyan,
    colors.aquamarine,
    colors.coral,
    colors.gold,
    colors.lightgrey,
    colors.salmon,
    colors.turquoise,
    colors.violet,
    colors.wheat,
    colors.limegreen,
    colors.skyblue,
    colors.thistle,
]


# =========================
# 📄 MAIN
# =========================
def generate_pdf(wordsearch):
    filename = f"{wordsearch.id}.pdf"
    filepath = os.path.join("media/pdfs", filename)

    os.makedirs("media/pdfs", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    # =========================
    # 🧠 DADOS
    # =========================
    grid = wordsearch.grid
    solution = wordsearch.solution
    words = sorted([w.text.upper() for w in wordsearch.words.all()])

    # =========================
    # 🎨 MAPEAR CORES DAS PALAVRAS
    # =========================
    word_color_map = {}

    for i, word in enumerate(words):
        if i < len(WORD_COLORS):
            word_color_map[word] = WORD_COLORS[i]
        else:
            word_color_map[word] = EXCESS_COLOR

    # =========================
    # 🧠 MAPEAR CÉLULAS → PALAVRAS
    # =========================
    cell_map = {}

    for item in solution:
        word = item["word"].upper()
        for r, c in item["positions"]:
            cell_map.setdefault((r, c), []).append(word)

    # =========================
    # 🔧 FUNÇÃO GRID
    # =========================
    def build_table(grid_data, highlight=False):
        table = Table(
            grid_data,
            colWidths=[CELL_SIZE] * len(grid_data[0]),
            rowHeights=[CELL_SIZE] * len(grid_data)
        )

        style = [
            ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 14),
        ]

        if highlight:
            for (r, c), words_here in cell_map.items():
                if len(words_here) == 1:
                    color = word_color_map.get(words_here[0], EXCESS_COLOR)
                else:
                    color = INTERSECTION_COLOR

                style.append(("BACKGROUND", (c, r), (c, r), color))

        table.setStyle(TableStyle(style))
        return table

    # =========================
    # 📝 WORD LIST (COM CORES)
    # =========================
    def build_word_list(colored=False):
        data = [["Word List"]]

        for word in words:
            data.append([word])

        table = Table(data, colWidths=[140])

        style = [
            # 🔥 título sem fundo
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (0, 0), 12),
            ("BOTTOMPADDING", (0, 0), (0, 0), 10),
            ("LINEBELOW", (0, 0), (0, 0), 1, colors.black),

            # 🔥 palavras
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("FONTSIZE", (0, 1), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ]

        # 🎨 aplicar cor por palavra
        if colored:
            for i, word in enumerate(words, start=1):
                bg = word_color_map[word]
                style.append(("BACKGROUND", (0, i), (0, i), bg))

        table.setStyle(TableStyle(style))
        return table

    # =========================
    # 📄 PÁGINA 1 (PUZZLE)
    # =========================
    elements.append(Paragraph(f"<b>{wordsearch.name}</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    layout1 = Table([
        [build_table(grid, highlight=False), build_word_list(colored=False)]
    ], colWidths=[340, 150])#colWidths=[grid_width + 10, 150]   #colWidths=[340, 150]

    elements.append(layout1)

    elements.append(PageBreak())

    # =========================
    # 📄 PÁGINA 2 (SOLUÇÃO)
    # =========================
    elements.append(Paragraph(f"<b>{wordsearch.name} - Solution</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    layout2 = Table([
        [build_table(grid, highlight=True), build_word_list(colored=True)]
    ], colWidths=[340, 150])

    elements.append(layout2)

    # =========================
    # 🚀 BUILD
    # =========================
    doc.build(elements)

    return filename