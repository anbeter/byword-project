import os
from PIL import Image, ImageDraw, ImageFont

CELL_SIZE = 50
FONT_SIZE = 22
MARGIN = 20
RIGHT_PANEL_WIDTH = 220

INTERSECTION_COLOR = "purple"
EXCESS_COLOR = "gray"

WORD_COLORS = [
    "yellow", "lightblue", "lightgreen", "pink", "orange",
    "lavender", "beige", "khaki", "cyan", "aquamarine",
    "coral", "gold", "lightgray", "salmon", "turquoise",
    "violet", "wheat", "limegreen", "skyblue", "thistle",
]

# GRID_LINE_COLOR ="black" | "#BBBBBB" #linhas do grid mais claras   #DDDDDD #bem claras
GRID_LINE_COLOR = "#BBBBBB"

grid_top = 40

def generate_png(wordsearch):
    os.makedirs("media/png", exist_ok=True)

    base_name = str(wordsearch.id)

    grid = wordsearch.grid
    rows = len(grid)
    cols = len(grid[0])

    # =========================
    # FONTES
    # =========================
    try:
        font_grid = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font_word = ImageFont.truetype("DejaVuSans.ttf", 20)
        font_word_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except:
        font_grid = ImageFont.load_default()
        font_title = font_grid
        font_word = font_grid
        font_word_title = font_grid

    # =========================
    # WORD LIST
    # =========================
    # words = sorted([w.text for w in wordsearch.words.all()])
    words = sorted([w.text.upper() for w in wordsearch.words.all()])

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

    for item in wordsearch.solution:
        word = item["word"].upper()
        for r, c in item["positions"]:
            cell_map.setdefault((r, c), []).append(word.upper())

    # =========================
    # DIMENSÕES
    # =========================
    grid_width = cols * CELL_SIZE
    grid_height = rows * CELL_SIZE

    width = grid_width + RIGHT_PANEL_WIDTH + (MARGIN * 3)
    height = grid_height + 120

    # =========================================================
    # 📄 BASE
    # =========================================================
    def create_base_image(solution_mode=False):
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # 🔥 título centralizado no GRID (não na imagem inteira)
        grid_center_x = MARGIN + (grid_width // 2)

        # draw.text(
        #     (grid_center_x, 30),
        #     wordsearch.name,
        #     fill="black",
        #     font=font_title,
        #     anchor="mm"
        # )

        grid_top = 40

        x_offset = grid_width + MARGIN * 2
        y_offset = grid_top

        draw.text(
            (x_offset, y_offset),
            "Word List:",
            fill="black",
            font=font_word_title
        )

        y_offset += 30

        for w in words:
            if solution_mode:
                color = word_color_map[w]
                draw.rectangle(
                    [x_offset - 5, y_offset - 2, x_offset + 140, y_offset + 20],
                    fill=color
                )

            draw.text(
                (x_offset, y_offset),
                w,
                fill="black",
                font=font_word
            )

            y_offset += 24

        return img, draw

    # =========================================================
    # 📄 PNG 1 - PUZZLE
    # =========================================================
    img1, draw1 = create_base_image(solution_mode=False)

    for r in range(rows):
        for c in range(cols):
            x = c * CELL_SIZE + MARGIN
            y = r * CELL_SIZE + grid_top

            draw1.rectangle(
                [x, y, x + CELL_SIZE, y + CELL_SIZE],
                outline=GRID_LINE_COLOR     ##BBBBBB
            )

            letter = grid[r][c]

            bbox = draw1.textbbox((0, 0), letter, font=font_grid)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            draw1.text(
                (x + (CELL_SIZE - w) / 2, y + (CELL_SIZE - h) / 2),
                letter,
                fill="black",
                font=font_grid
            )

    puzzle_path = f"media/png/{base_name}.png"
    img1.save(puzzle_path)

    # =========================================================
    # 📄 PNG 2 - SOLUTION
    # =========================================================
    img2, draw2 = create_base_image(solution_mode=True)

    for r in range(rows):
        for c in range(cols):
            x = c * CELL_SIZE + MARGIN
            y = r * CELL_SIZE + grid_top

            cell_words = cell_map.get((r, c), [])

            if cell_words:
                if len(cell_words) == 1:
                    # color = word_color_map[cell_words[0]]
                    color = word_color_map.get(cell_words[0], EXCESS_COLOR)
                else:
                    color = INTERSECTION_COLOR

                draw2.rectangle(
                    [x, y, x + CELL_SIZE, y + CELL_SIZE],
                    fill=color,
                    outline=GRID_LINE_COLOR
                )
            else:
                draw2.rectangle(
                    [x, y, x + CELL_SIZE, y + CELL_SIZE],
                    outline=GRID_LINE_COLOR
                )

            letter = grid[r][c]

            bbox = draw2.textbbox((0, 0), letter, font=font_grid)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            draw2.text(
                (x + (CELL_SIZE - w) / 2, y + (CELL_SIZE - h) / 2),
                letter,
                fill="black",
                font=font_grid
            )

    solution_path = f"media/png/{base_name}s.png"
    img2.save(solution_path)

    return {
        "puzzle": puzzle_path,
        "solution": solution_path
    }