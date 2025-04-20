from pydantic import BaseModel, Field

from mcp_dic.dictionary.inflections import Inflections


class DictionaryEntry(BaseModel):
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
                 'For example, "動詞" for the verb "run".'),
  )
  phonological_pattern: str = Field(
    ...,
    title='phonological pattern name',
    description=('The phonological pattern name of the stem. '),
  )
  etymology: str = Field(
    ...,
    title='etymology',
    description=('The etymology of the stem. '),
  )
  notes: str = Field(
    ...,
    title='notes',
    description=('Additional notes about the stem. '),
  )
  inflections: Inflections = Field(
    ...,
    title='inflections',
    description=('The inflections of the stem. '),
  )
  definitions: list[str] = Field(
    ...,
    title='definitions',
    description=(
      'The definitions of the stem. '
      'For example, "to move swiftly on foot" for the verb "run".'
    ),
  )
  sentences: list[str] = Field(
    ...,
    title='sentences',
    description=(
      'Example sentences using the stem. '
      'For example, "I run every morning." for the verb "run".'
    ),
  )
