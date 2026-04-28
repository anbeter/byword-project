import random
import string


DIRECTIONS = [
    (0, 1),    # →
    (1, 0),    # ↓
    (1, 1),    # ↘
    (-1, 1),   # ↗
    (0, -1),   # ←
    (-1, 0),   # ↑
    (-1, -1),  # ↖
    (1, -1)    # ↙
]


class WordSearchEngine:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.word_positions = []

    def generate(self, words):
        words = list(words)

        # 🔥 prioriza palavras maiores
        words.sort(key=len, reverse=True)

        solution = []

        for word in words:
            positions = self._place_word(word)

            if not positions:
                raise Exception(f'Não foi possível posicionar a palavra: {word}')

            solution.append({
                "word": word,
                "positions": positions
            })

        self._fill_empty()

        return self.grid, self.word_positions

    # 🔧 tenta posicionar palavra
    def _place_word(self, word, max_attempts=100):
        for _ in range(max_attempts):
            direction = random.choice(DIRECTIONS)

            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)

            if self._can_place(word, row, col, direction):
                positions = self._apply_word(word, row, col, direction)
                return positions

        return None

    # 🔍 valida se cabe
    def _can_place(self, word, row, col, direction):
        dr, dc = direction

        for i, char in enumerate(word):
            r = row + dr * i
            c = col + dc * i

            # fora do grid
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return False

            existing = self.grid[r][c]

            # conflito (mas permite mesma letra)
            if existing is not None and existing != char:
                return False

        return True

    # ✍️ escreve no grid
    def _apply_word(self, word, row, col, direction):
        dr, dc = direction
        positions = []

        for i, char in enumerate(word):
            r = row + dr * i
            c = col + dc * i
            self.grid[r][c] = char
            positions.append((r, c))
        
        self.word_positions.append({
            "word": word,
            "positions": positions
        })
        return positions
    

    # 🔤 preenche espaços vazios
    def _fill_empty(self):
        letters = string.ascii_uppercase  # 🔥 SEM ACENTO

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    self.grid[r][c] = random.choice(letters)