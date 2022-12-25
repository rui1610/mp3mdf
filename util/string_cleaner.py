import re


def clean_song_name(text: str):
    result = text
    # Remove anything with "official video"
    result = result.lower()
    result = result.replace("(official video)", "")

    # Remove anything that is a whitespace
    pattern = re.compile(r'\s+')
    result = re.sub(pattern, ' ', result)

    # result = re.sub(r'[^a-zA-Z0-9 ]', '', result)

    result = result.replace('  ', ' ')
    result = result.strip()
    return result
