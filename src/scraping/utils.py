def clean_text(text: str) -> str:
    return text.strip().replace('\n', ' ') if text else ''
