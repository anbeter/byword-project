import pyphen


dic = pyphen.Pyphen(lang="en_US")


def separate_syllables(word):
    if not word:
        return None

    return dic.inserted(word, ".")