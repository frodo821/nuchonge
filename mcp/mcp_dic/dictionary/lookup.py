from typing import Iterable
from pydantic import BaseModel, Field

from mcp_dic.database.sqlite import SQLiteDatabase
from mcp_dic.utils.normalize_str import normalize_str


def first[T](iterable: Iterable[T], default: T | None = None) -> T | None:
  """Return the first element of the iterable or None if empty."""
  try:
    return next(iter(iterable))
  except StopIteration:
    return default


class Inflection(BaseModel):
  form: str = Field(
    ...,
    title='inflection form',
    description=(
      'The inflected form of the word. '
      'For example, "running" for the verb "run".'
    ),
  )
  inflection_type: str = Field(
    ...,
    title='inflection type',
    description=('The type of inflection. '
                 'For example, "past tense/plural/gerund".'),
  )


class Stem(BaseModel):
  id: int = Field(
    ...,
    title='stem id',
    description='The unique identifier for the stem.',
  )
  stem: str = Field(
    ...,
    title='stem',
    description=('The stem of the word. '
                 'For example, "run" for the verb "running".'),
  )
  part_of_speech: str = Field(
    ...,
    title='part of speech',
    description=('The part of speech of the stem. '
                 'For example, "verb" for the verb "run".'),
  )
  part_of_speech_id: int = Field(
    ...,
    title='part of speech id',
    description=(
      'The unique identifier for the part of speech. '
      'For example, "verb" for the verb "run".'
    ),
  )
  phonological_pattern: str = Field(
    ...,
    title='phonological pattern',
    description=('The phonological pattern of the stem. '),
  )
  phonological_pattern_id: int = Field(
    ...,
    title='phonological pattern id',
    description=('The unique identifier for the phonological pattern.'),
  )
  etymology: str = Field(
    ...,
    title='etymology',
    description=(
      'The etymology of the stem. '
      'For example, "from Old English" for the verb "run".'
    ),
  )
  notes: str = Field(
    ...,
    title='notes',
    description=(
      'Additional notes about the stem. '
      'For example, "used in poetry" for the verb "run".'
    ),
  )
  definitions: list[str] = Field(
    ...,
    title='definitions',
    description=(
      'The definitions of the stem. '
      'For example, "to move swiftly" for the verb "run".'
    ),
  )

  inflections: list[Inflection] = Field(
    ...,
    title='inflections',
    description=('The inflections of the stem. '
                 'For example, "running" for the verb "run".'),
  )

  related_stems: list[str] = Field(
    ...,
    title='related stems',
    description=('The related stems of the stem. '
                 'For example, "runner" for the verb "run".'),
  )

  sentences: list[str] = Field(
    ...,
    title='sentences',
    description=(
      'The sentences using the stem. '
      'For example, "He is running." for the verb "run".'
    ),
  )

  def format_inflections(self) -> str:
    if self.part_of_speech_id in [1, 3, 7]:
      return f"""## 曲用表
| 種類 | 曲用形 |
|:---:|:-----:|
{'\n'.join(
          f"| {inflection.inflection_type} | {inflection.form} |"
          for inflection in self.inflections
        )}\n"""

    if self.part_of_speech_id in [2]:
      return f"""## 活用表
| 種類 | 活用形 |
|:---:|:-----:|
{'\n'.join(
          f"| {inflection.inflection_type} | {inflection.form} |"
          for inflection in self.inflections
        )}\n"""

    return ""

  def format_inflections_human_readable(self) -> str:
    if self.part_of_speech_id in [1, 7]:
      cases = {k.inflection_type.split('定')[1] for k in self.inflections}
      numbers = ['単数定', '単数不定', '複数定', '複数不定']

      inflection = {
        case: {
          n: first(i.form for i in self.inflections if i.inflection_type == f'{n}{case}') or '-' for n in numbers
        } for case in cases
      }

      return f"""## 活用表
| 格 | 単数定 | 単数不定 | 複数定 | 複数不定 |
|:---:|:-----:|:-----:|:-----:|:-----:|
{'\n'.join(
          f"| {case} | {
            i.get('単数定', '-')
          } | {
            i.get('単数不定', '-')
          } | {
            i.get('複数定', '-')
          } | {
            i.get('複数不定', '-')
          } |"
          for case, i in inflection.items()
)}
"""
    if self.part_of_speech_id in [3]:
      cases = {k.inflection_type.split('定')[1] for k in self.inflections}
      numbers = ['単数定', '単数不定', '複数定', '複数不定']
      animacy = ['有生', '無生']

      decl_adv = {
        anim: {
          case: {
            n: first(i.form for i in self.inflections if i.inflection_type == f'{anim}{n}{case}') or '-' for n in numbers
          } for case in cases
        } for anim in animacy
      }

      return f"""## 活用表
### 有生名詞修飾

| 格 | 単数定 | 単数不定 | 複数定 | 複数不定 |
|:---:|:-----:|:-----:|:-----:|:-----:|
{'\n'.join(
          f"| {case} | {
            i.get('単数定', '-')
          } | {
            i.get('単数不定', '-')
          } | {
            i.get('複数定', '-')
          } | {
            i.get('複数不定', '-')
          } |"
          for case, i in decl_adv['有生'].items()
)}

### 無生名詞修飾

| 格 | 単数定 | 単数不定 | 複数定 | 複数不定 |
|:---:|:-----:|:-----:|:-----:|:-----:|
{'\n'.join(
          f"| {case} | {
            i.get('単数定', '-')
          } | {
            i.get('単数不定', '-')
          } | {
            i.get('複数定', '-')
          } | {
            i.get('複数不定', '-')
          } |"
          for case, i in decl_adv['無生'].items()
)}
"""
    if self.part_of_speech_id in [2]:
      return f"""## 活用表
| 種類 | 活用形 |
|:---:|:-----:|
{'\n'.join(
          f"| {inflection.inflection_type} | {inflection.form} |"
          for inflection in self.inflections
        )}\n"""

    return ""

  def format_stem(self, *, human_readable: bool = False) -> str:
    return f"""# {self.stem}
## 品詞
{self.part_of_speech} (品詞ID: {self.part_of_speech_id})

## 音韻パターン
{self.phonological_pattern} (音韻パターンID: {self.phonological_pattern_id})

## 語源
{self.etymology if self.etymology else "語源情報なし"}

## 意味

{'\n'.join(f'{nth + 1}. {d}' for nth, d in enumerate(self.definitions)) if self.definitions else "意味情報なし"}

## 関連語
{'\n'.join(f'{nth + 1}. {related_stem}' for nth, related_stem in enumerate(self.related_stems)) if self.related_stems else "関連語情報なし"}

## 例文
{'\n'.join(f'{nth + 1}. {sentence}' for nth, sentence in enumerate(self.sentences)) if self.sentences else "例文情報なし"}

{self.format_inflections_human_readable() if human_readable else self.format_inflections()}
""".strip()


def load_inflections(
  stem_id: int,
  db: SQLiteDatabase,
) -> list[Inflection]:
  results = db.select(
    """
SELECT
  inflections.form AS form,
  inflection_types.name AS inflection_type
FROM
  inflections
LEFT JOIN
  inflection_types ON inflections.inflection_type_id = inflection_types.id
WHERE
  inflections.stem_id = ?
    """,
    [stem_id],
  )

  return [
    Inflection(
      form=row['form'],
      inflection_type=row['inflection_type'],
    ) for row in results
  ]


def load_definitions(
  stem_id: int,
  db: SQLiteDatabase,
) -> list[str]:
  results = db.select(
    """
SELECT
  definitions.definition AS definition
FROM
  definitions
WHERE
  definitions.stem_id = ?
    """,
    [stem_id],
  )

  return [row['definition'] for row in results]


def load_sentences(
  stem_id: int,
  db: SQLiteDatabase,
) -> list[str]:
  results = db.select(
    """
SELECT
  sentences.original_text AS sentence
FROM
  sentences
WHERE
  sentences.stem_id = ?
    """,
    [stem_id],
  )

  return [row['sentence'] for row in results]


def lookup_stem_by_id(
  stem_id: int,
  db: SQLiteDatabase,
) -> Stem | None:
  results = db.select(
    """
SELECT
  stems.id AS stem_id,
  stems.stem AS stem,
  stems.part_of_speech_id AS part_of_speech_id,
  parts_of_speech.name AS part_of_speech,
  stems.phonological_pattern_id AS phonological_pattern_id,
  phonological_patterns.name AS phonological_pattern,
  stems.etymology AS etymology,
  stems.notes AS notes
FROM
  stems
LEFT JOIN
  parts_of_speech ON stems.part_of_speech_id = parts_of_speech.id
LEFT JOIN
  phonological_patterns ON stems.phonological_pattern_id = phonological_patterns.id
WHERE
  stems.id = ?
    """,
    [stem_id],
  )

  if not results:
    return None

  row = results[0]

  return Stem(
    id=row['stem_id'],
    stem=row['stem'],
    part_of_speech=row['part_of_speech'],
    part_of_speech_id=row['part_of_speech_id'],
    phonological_pattern=row['phonological_pattern'],
    phonological_pattern_id=row['phonological_pattern_id'],
    etymology=row['etymology'],
    notes=row['notes'],
    definitions=load_definitions(
      row['stem_id'],
      db,
    ),
    inflections=load_inflections(
      row['stem_id'],
      db,
    ),
    related_stems=[],
    sentences=[],
  )


def lookup_stem(
  stem: str,
  db: SQLiteDatabase,
) -> list[Stem]:
  stem = normalize_str(stem)

  results = db.select(
    """SELECT
  stems.id AS stem_id,
  stems.stem AS stem,
  stems.part_of_speech_id AS part_of_speech_id,
  parts_of_speech.name AS part_of_speech,
  stems.phonological_pattern_id AS phonological_pattern_id,
  phonological_patterns.name AS phonological_pattern,
  stems.etymology AS etymology,
  stems.notes AS notes
FROM
  stems
LEFT JOIN
  parts_of_speech ON stems.part_of_speech_id = parts_of_speech.id
LEFT JOIN
  phonological_patterns ON stems.phonological_pattern_id = phonological_patterns.id
WHERE
  stems.stem = ?""",
    [stem],
  )

  if not results:
    return []

  return [
    Stem(
      id=row['stem_id'],
      stem=row['stem'],
      part_of_speech=row['part_of_speech'],
      part_of_speech_id=row['part_of_speech_id'],
      phonological_pattern=row['phonological_pattern'],
      phonological_pattern_id=row['phonological_pattern_id'],
      etymology=row['etymology'],
      notes=row['notes'],
      definitions=load_definitions(
        row['stem_id'],
        db,
      ),
      inflections=load_inflections(
        row['stem_id'],
        db,
      ),
      related_stems=[],
      sentences=[],
    ) for row in results
  ]


def lookup_stem_by_surface_form(
  surface_form: str,
  db: SQLiteDatabase,
) -> list[Stem]:
  form = normalize_str(surface_form)

  stem_ids = db.select(
    """
SELECT
  inflections.stem_id AS stem_id
FROM
  inflections
WHERE
  inflections.form = ?
    """,
    [form],
  )

  if not stem_ids:
    return []

  stem_ids = [row['stem_id'] for row in stem_ids]

  stems = []

  for stem_id in stem_ids:
    stem = lookup_stem_by_id(
      stem_id,
      db,
    )

    if stem:
      stems.append(stem)

  return stems


def get_inflection_by_type(
  stem: str,
  inflection_types: list[str],
  db: SQLiteDatabase,
) -> list[str]:
  stem = normalize_str(stem)

  like_query = ' AND '.join(
    f"(inflection_types.name LIKE '%{i}%')" for i in (
      inflection_type.replace(
        "'",
        "",
      ).replace(
        '%',
        '',
      ) for inflection_type in inflection_types
    )
  )

  where = ' AND '.join([
    *([like_query] if like_query else []),
    'stems.stem = :stem',
  ])

  query = f"""
SELECT
  inflections.form AS form,
  inflection_types.name AS inflection_type
FROM
  inflections
JOIN
  stems ON inflections.stem_id = stems.id
JOIN
  inflection_types ON inflections.inflection_type_id = inflection_types.id
WHERE
  {where}
""".strip()

  results = db.select(
    query,
    {'stem': stem},
  )

  return [f"{row['inflection_type']}: {row['form']}" for row in results]
