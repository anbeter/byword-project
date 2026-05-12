import re
import random


def replace_marked_words(
    original_text,
    markers="**",
    char="_",
    multiplication=3,
    sum_f=2,
):
    """
    Substitui palavras entre marcadores por caracteres repetidos.
    Exemplo:
    replace_marked_words("The *earth* is beautiful","**","_",3,2)
    ->
    The _________________ is beautiful
    """

    if len(markers) != 2:
        raise ValueError(
            "markers must contain exactly 2 characters"
        )

    start_marker = re.escape(markers[0])
    end_marker = re.escape(markers[1])

    pattern = rf"{start_marker}(.*?){end_marker}"

    def repl(match):
        content = match.group(1).strip()
        total = (
            len(content) * multiplication
        ) + sum_f
        return char * total

    return re.sub(pattern, repl, original_text)

def clean_text(text, markers="**"):
    """
    Remove apenas os marcadores do texto.
    Exemplo:
    clean_text("The *earth* is beautiful!")
    ->
    The earth is beautiful!
    """

    if len(markers) != 2:
        raise ValueError(
            "markers must contain exactly 2 characters"
        )

    start_marker = re.escape(markers[0])
    end_marker = re.escape(markers[1])

    pattern = rf"{start_marker}(.*?){end_marker}"

    return re.sub(pattern,r"\1",text)

def generate_scrambled_hints(text):
    hints = re.findall(
        r"\*(.*?)\*",
        text
    )
    random.shuffle(hints)
    return " | ".join(hints)