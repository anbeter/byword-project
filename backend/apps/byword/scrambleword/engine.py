import random
import re


def embaralhar_palavras(texto: str):
    padrao = r'"([^"]+)"|(\S+)'  
    palavras_embaralhadas = []

    for match in re.finditer(padrao, texto):
        grupo = match[1] if match[1] is not None else match[2]

        if match[1] is not None:
            sub_palavras = grupo.split()
            sub_embaralhadas = []

            for sub in sub_palavras:
                letras = list(sub)
                random.shuffle(letras)
                sub_embaralhadas.append(''.join(letras))

            palavras_embaralhadas.append(' '.join(sub_embaralhadas))
        else:
            letras = list(grupo)
            random.shuffle(letras)
            palavras_embaralhadas.append(''.join(letras))

    return palavras_embaralhadas


def embaralhar_texto(texto: str) -> str:
    return ' '.join(embaralhar_palavras(texto))