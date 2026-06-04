import requests


def fetch_pronunciation(word):
    try:
        response = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        phonetics = data[0].get("phonetics", [])

        for item in phonetics:
            text = item.get("text")

            if text:
                return text

    except Exception:
        pass

    return None