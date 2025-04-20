from unicodedata import normalize


def normalize_str(s: str) -> str:
  return normalize('NFKD', s).replace('ç', 'ç')
