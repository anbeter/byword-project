import os
from PIL import Image, ImageDraw, ImageFont


CELL_SIZE = 40
FONT_SIZE = 18
MARGIN = 20
RIGHT_PANEL_WIDTH = 220


def generate_png(wordsearch):
    os.makedirs("media/png", exist_ok=True)

    base_name = str(wordsearch.id)

    grid = wordsearch.grid
    rows = len(grid)
    cols = len(grid[0])

    # =========================
    # FONTES
    # =========================
    font = ImageFont.load_default()

    # =========================
    # WORD LIST
    # =========================
    words = [w.text for w in wordsearch.words.all()]

    # =========================
    # DIMENSÕES
    # =========================
    grid_width = cols * CELL_SIZE
    grid_height = rows * CELL_SIZE

    width = grid_width + RIGHT_PANEL_WIDTH + (MARGIN * 3)
    height = grid_height + 120  # espaço título

    # =========================================================
    # 📄 HELPER PARA DESENHAR BASE
    # =========================================================
    def create_base_image():
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # 🔥 título
        draw.text(
            (width // 2 - 100, 20),
            wordsearch.name,
            fill="black",
            font=font
        )

        # 🔥 word list
        x_offset = grid_width + MARGIN * 2
        y_offset = 60

        draw.text(
            (x_offset, y_offset),
            "Word List:",
            fill="black",
            font=font
        )

        y_offset += 30

        for w in words:
            draw.text(
                (x_offset, y_offset),
                w,
                fill="black",
                font=font
            )
            y_offset += 20

        return img, draw

    # =========================================================
    # 📄 PNG 1 - PUZZLE
    # =========================================================
    img1, draw1 = create_base_image()

    for r in range(rows):
        for c in range(cols):
            x = c * CELL_SIZE + MARGIN
            y = r * CELL_SIZE + 80

            draw1.rectangle(
                [x, y, x + CELL_SIZE, y + CELL_SIZE],
                outline="black"
            )

            draw1.text(
                (x + 12, y + 10),
                grid[r][c],
                fill="black",
                font=font
            )

    puzzle_path = f"media/png/{base_name}.png"
    img1.save(puzzle_path)

    # =========================================================
    # 📄 PNG 2 - SOLUTION
    # =========================================================
    highlight = set()

    for word in wordsearch.solution:
        for r, c in word["positions"]:
            highlight.add((r, c))

    img2, draw2 = create_base_image()

    for r in range(rows):
        for c in range(cols):
            x = c * CELL_SIZE + MARGIN
            y = r * CELL_SIZE + 80

            if (r, c) in highlight:
                draw2.rectangle(
                    [x, y, x + CELL_SIZE, y + CELL_SIZE],
                    fill="yellow",
                    outline="black"
                )
            else:
                draw2.rectangle(
                    [x, y, x + CELL_SIZE, y + CELL_SIZE],
                    outline="black"
                )

            draw2.text(
                (x + 12, y + 10),
                grid[r][c],
                fill="black",
                font=font
            )

    solution_path = f"media/png/{base_name}s.png"
    img2.save(solution_path)

    return {
        "puzzle": puzzle_path,
        "solution": solution_path
    }