from apps.byword.wordsearch.engine import WordSearchEngine


def generate_grid(wordsearch):
    words = [w.text for w in wordsearch.words.all()]

    engine = WordSearchEngine(
        rows=wordsearch.rows,
        cols=wordsearch.cols
    )

    grid, positions = engine.generate(words)

    wordsearch.grid = grid
    wordsearch.solution = positions
    wordsearch.save()

    # print("GRID:", grid)
    # print("SOLUTION:", positions)

    return grid, positions