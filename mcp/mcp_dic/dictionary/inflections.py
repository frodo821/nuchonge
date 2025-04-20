from typing import Literal
from pydantic import BaseModel, Field, RootModel


class Conjugations(BaseModel):
  type: Literal['conjugations'] = Field(
    ...,
    title='conjugations',
    description='The type of the entry.',
  )

  indicative_future_imperfect_1st_singular: str | None = Field(
    ...,
    title='直説法未来時制非完了相一人称単数',
    alias='直説法未来時制非完了相一人称単数',
  )
  indicative_future_imperfect_2nd_singular: str | None = Field(
    ...,
    title='直説法未来時制非完了相二人称単数',
    alias='直説法未来時制非完了相二人称単数',
  )
  indicative_future_imperfect_3rd_singular: str | None = Field(
    ...,
    title='直説法未来時制非完了相三人称単数',
    alias='直説法未来時制非完了相三人称単数',
  )
  indicative_future_imperfect_1st_plural: str | None = Field(
    ...,
    title='直説法未来時制非完了相一人称複数',
    alias='直説法未来時制非完了相一人称複数',
  )
  indicative_future_imperfect_2nd_plural: str | None = Field(
    ...,
    title='直説法未来時制非完了相二人称複数',
    alias='直説法未来時制非完了相二人称複数',
  )
  indicative_future_imperfect_3rd_plural: str | None = Field(
    ...,
    title='直説法未来時制非完了相三人称複数',
    alias='直説法未来時制非完了相三人称複数',
  )
  indicative_future_perfect_1st_singular: str | None = Field(
    ...,
    title='直説法未来時制完遂相一人称単数',
    alias='直説法未来時制完遂相一人称単数',
  )
  indicative_future_perfect_2nd_singular: str | None = Field(
    ...,
    title='直説法未来時制完遂相二人称単数',
    alias='直説法未来時制完遂相二人称単数',
  )
  indicative_future_perfect_3rd_singular: str | None = Field(
    ...,
    title='直説法未来時制完遂相三人称単数',
    alias='直説法未来時制完遂相三人称単数',
  )
  indicative_future_perfect_1st_plural: str | None = Field(
    ...,
    title='直説法未来時制完遂相一人称複数',
    alias='直説法未来時制完遂相一人称複数',
  )
  indicative_future_perfect_2nd_plural: str | None = Field(
    ...,
    title='直説法未来時制完遂相二人称複数',
    alias='直説法未来時制完遂相二人称複数',
  )
  indicative_future_perfect_3rd_plural: str | None = Field(
    ...,
    title='直説法未来時制完遂相三人称複数',
    alias='直説法未来時制完遂相三人称複数',
  )
  indicative_future_consequential_1st_singular: str | None = Field(
    ...,
    title='直説法未来時制結果状態相一人称単数',
    alias='直説法未来時制結果状態相一人称単数',
  )
  indicative_future_consequential_2nd_singular: str | None = Field(
    ...,
    title='直説法未来時制結果状態相二人称単数',
    alias='直説法未来時制結果状態相二人称単数',
  )
  indicative_future_consequential_3rd_singular: str | None = Field(
    ...,
    title='直説法未来時制結果状態相三人称単数',
    alias='直説法未来時制結果状態相三人称単数',
  )
  indicative_future_consequential_1st_plural: str | None = Field(
    ...,
    title='直説法未来時制結果状態相一人称複数',
    alias='直説法未来時制結果状態相一人称複数',
  )
  indicative_future_consequential_2nd_plural: str | None = Field(
    ...,
    title='直説法未来時制結果状態相二人称複数',
    alias='直説法未来時制結果状態相二人称複数',
  )
  indicative_future_consequential_3rd_plural: str | None = Field(
    ...,
    title='直説法未来時制結果状態相三人称複数',
    alias='直説法未来時制結果状態相三人称複数',
  )
  indicative_future_preparative_1st_singular: str | None = Field(
    ...,
    title='直説法未来時制準備相一人称単数',
    alias='直説法未来時制準備相一人称単数',
  )
  indicative_future_preparative_2nd_singular: str | None = Field(
    ...,
    title='直説法未来時制準備相二人称単数',
    alias='直説法未来時制準備相二人称単数',
  )
  indicative_future_preparative_3rd_singular: str | None = Field(
    ...,
    title='直説法未来時制準備相三人称単数',
    alias='直説法未来時制準備相三人称単数',
  )
  indicative_future_preparative_1st_plural: str | None = Field(
    ...,
    title='直説法未来時制準備相一人称複数',
    alias='直説法未来時制準備相一人称複数',
  )
  indicative_future_preparative_2nd_plural: str | None = Field(
    ...,
    title='直説法未来時制準備相二人称複数',
    alias='直説法未来時制準備相二人称複数',
  )
  indicative_future_preparative_3rd_plural: str | None = Field(
    ...,
    title='直説法未来時制準備相三人称複数',
    alias='直説法未来時制準備相三人称複数',
  )
  indicative_future_inchoative_1st_singular: str | None = Field(
    ...,
    title='直説法未来時制起動相一人称単数',
    alias='直説法未来時制起動相一人称単数',
  )
  indicative_future_inchoative_2nd_singular: str | None = Field(
    ...,
    title='直説法未来時制起動相二人称単数',
    alias='直説法未来時制起動相二人称単数',
  )
  indicative_future_inchoative_3rd_singular: str | None = Field(
    ...,
    title='直説法未来時制起動相三人称単数',
    alias='直説法未来時制起動相三人称単数',
  )
  indicative_future_inchoative_1st_plural: str | None = Field(
    ...,
    title='直説法未来時制起動相一人称複数',
    alias='直説法未来時制起動相一人称複数',
  )
  indicative_future_inchoative_2nd_plural: str | None = Field(
    ...,
    title='直説法未来時制起動相二人称複数',
    alias='直説法未来時制起動相二人称複数',
  )
  indicative_future_inchoative_3rd_plural: str | None = Field(
    ...,
    title='直説法未来時制起動相三人称複数',
    alias='直説法未来時制起動相三人称複数',
  )
  indicative_future_terminative_1st_singular: str | None = Field(
    ...,
    title='直説法未来時制終結相一人称単数',
    alias='直説法未来時制終結相一人称単数',
  )
  indicative_future_terminative_2nd_singular: str | None = Field(
    ...,
    title='直説法未来時制終結相二人称単数',
    alias='直説法未来時制終結相二人称単数',
  )
  indicative_future_terminative_3rd_singular: str | None = Field(
    ...,
    title='直説法未来時制終結相三人称単数',
    alias='直説法未来時制終結相三人称単数',
  )
  indicative_future_terminative_1st_plural: str | None = Field(
    ...,
    title='直説法未来時制終結相一人称複数',
    alias='直説法未来時制終結相一人称複数',
  )
  indicative_future_terminative_2nd_plural: str | None = Field(
    ...,
    title='直説法未来時制終結相二人称複数',
    alias='直説法未来時制終結相二人称複数',
  )
  indicative_future_terminative_3rd_plural: str | None = Field(
    ...,
    title='直説法未来時制終結相三人称複数',
    alias='直説法未来時制終結相三人称複数',
  )
  indicative_past_imperfect_1st_singular: str | None = Field(
    ...,
    title='直説法過去時制非完了相一人称単数',
    alias='直説法過去時制非完了相一人称単数',
  )
  indicative_past_imperfect_2nd_singular: str | None = Field(
    ...,
    title='直説法過去時制非完了相二人称単数',
    alias='直説法過去時制非完了相二人称単数',
  )
  indicative_past_imperfect_3rd_singular: str | None = Field(
    ...,
    title='直説法過去時制非完了相三人称単数',
    alias='直説法過去時制非完了相三人称単数',
  )
  indicative_past_imperfect_1st_plural: str | None = Field(
    ...,
    title='直説法過去時制非完了相一人称複数',
    alias='直説法過去時制非完了相一人称複数',
  )
  indicative_past_imperfect_2nd_plural: str | None = Field(
    ...,
    title='直説法過去時制非完了相二人称複数',
    alias='直説法過去時制非完了相二人称複数',
  )
  indicative_past_imperfect_3rd_plural: str | None = Field(
    ...,
    title='直説法過去時制非完了相三人称複数',
    alias='直説法過去時制非完了相三人称複数',
  )
  indicative_past_perfect_1st_singular: str | None = Field(
    ...,
    title='直説法過去時制完遂相一人称単数',
    alias='直説法過去時制完遂相一人称単数',
  )
  indicative_past_perfect_2nd_singular: str | None = Field(
    ...,
    title='直説法過去時制完遂相二人称単数',
    alias='直説法過去時制完遂相二人称単数',
  )
  indicative_past_perfect_3rd_singular: str | None = Field(
    ...,
    title='直説法過去時制完遂相三人称単数',
    alias='直説法過去時制完遂相三人称単数',
  )
  indicative_past_perfect_1st_plural: str | None = Field(
    ...,
    title='直説法過去時制完遂相一人称複数',
    alias='直説法過去時制完遂相一人称複数',
  )
  indicative_past_perfect_2nd_plural: str | None = Field(
    ...,
    title='直説法過去時制完遂相二人称複数',
    alias='直説法過去時制完遂相二人称複数',
  )
  indicative_past_perfect_3rd_plural: str | None = Field(
    ...,
    title='直説法過去時制完遂相三人称複数',
    alias='直説法過去時制完遂相三人称複数',
  )
  indicative_past_consequential_1st_singular: str | None = Field(
    ...,
    title='直説法過去時制結果状態相一人称単数',
    alias='直説法過去時制結果状態相一人称単数',
  )
  indicative_past_consequential_2nd_singular: str | None = Field(
    ...,
    title='直説法過去時制結果状態相二人称単数',
    alias='直説法過去時制結果状態相二人称単数',
  )
  indicative_past_consequential_3rd_singular: str | None = Field(
    ...,
    title='直説法過去時制結果状態相三人称単数',
    alias='直説法過去時制結果状態相三人称単数',
  )
  indicative_past_consequential_1st_plural: str | None = Field(
    ...,
    title='直説法過去時制結果状態相一人称複数',
    alias='直説法過去時制結果状態相一人称複数',
  )
  indicative_past_consequential_2nd_plural: str | None = Field(
    ...,
    title='直説法過去時制結果状態相二人称複数',
    alias='直説法過去時制結果状態相二人称複数',
  )
  indicative_past_consequential_3rd_plural: str | None = Field(
    ...,
    title='直説法過去時制結果状態相三人称複数',
    alias='直説法過去時制結果状態相三人称複数',
  )
  indicative_past_preparative_1st_singular: str | None = Field(
    ...,
    title='直説法過去時制準備相一人称単数',
    alias='直説法過去時制準備相一人称単数',
  )
  indicative_past_preparative_2nd_singular: str | None = Field(
    ...,
    title='直説法過去時制準備相二人称単数',
    alias='直説法過去時制準備相二人称単数',
  )
  indicative_past_preparative_3rd_singular: str | None = Field(
    ...,
    title='直説法過去時制準備相三人称単数',
    alias='直説法過去時制準備相三人称単数',
  )
  indicative_past_preparative_1st_plural: str | None = Field(
    ...,
    title='直説法過去時制準備相一人称複数',
    alias='直説法過去時制準備相一人称複数',
  )
  indicative_past_preparative_2nd_plural: str | None = Field(
    ...,
    title='直説法過去時制準備相二人称複数',
    alias='直説法過去時制準備相二人称複数',
  )
  indicative_past_preparative_3rd_plural: str | None = Field(
    ...,
    title='直説法過去時制準備相三人称複数',
    alias='直説法過去時制準備相三人称複数',
  )
  indicative_past_inchoative_1st_singular: str | None = Field(
    ...,
    title='直説法過去時制起動相一人称単数',
    alias='直説法過去時制起動相一人称単数',
  )
  indicative_past_inchoative_2nd_singular: str | None = Field(
    ...,
    title='直説法過去時制起動相二人称単数',
    alias='直説法過去時制起動相二人称単数',
  )
  indicative_past_inchoative_3rd_singular: str | None = Field(
    ...,
    title='直説法過去時制起動相三人称単数',
    alias='直説法過去時制起動相三人称単数',
  )
  indicative_past_inchoative_1st_plural: str | None = Field(
    ...,
    title='直説法過去時制起動相一人称複数',
    alias='直説法過去時制起動相一人称複数',
  )
  indicative_past_inchoative_2nd_plural: str | None = Field(
    ...,
    title='直説法過去時制起動相二人称複数',
    alias='直説法過去時制起動相二人称複数',
  )
  indicative_past_inchoative_3rd_plural: str | None = Field(
    ...,
    title='直説法過去時制起動相三人称複数',
    alias='直説法過去時制起動相三人称複数',
  )
  indicative_past_terminative_1st_singular: str | None = Field(
    ...,
    title='直説法過去時制終結相一人称単数',
    alias='直説法過去時制終結相一人称単数',
  )
  indicative_past_terminative_2nd_singular: str | None = Field(
    ...,
    title='直説法過去時制終結相二人称単数',
    alias='直説法過去時制終結相二人称単数',
  )
  indicative_past_terminative_3rd_singular: str | None = Field(
    ...,
    title='直説法過去時制終結相三人称単数',
    alias='直説法過去時制終結相三人称単数',
  )
  indicative_past_terminative_1st_plural: str | None = Field(
    ...,
    title='直説法過去時制終結相一人称複数',
    alias='直説法過去時制終結相一人称複数',
  )
  indicative_past_terminative_2nd_plural: str | None = Field(
    ...,
    title='直説法過去時制終結相二人称複数',
    alias='直説法過去時制終結相二人称複数',
  )
  indicative_past_terminative_3rd_plural: str | None = Field(
    ...,
    title='直説法過去時制終結相三人称複数',
    alias='直説法過去時制終結相三人称複数',
  )
  indicative_present_imperfect_1st_singular: str | None = Field(
    ...,
    title='直説法現在時制非完了相一人称単数',
    alias='直説法現在時制非完了相一人称単数',
  )
  indicative_present_imperfect_2nd_singular: str | None = Field(
    ...,
    title='直説法現在時制非完了相二人称単数',
    alias='直説法現在時制非完了相二人称単数',
  )
  indicative_present_imperfect_3rd_singular: str | None = Field(
    ...,
    title='直説法現在時制非完了相三人称単数',
    alias='直説法現在時制非完了相三人称単数',
  )
  indicative_present_imperfect_1st_plural: str | None = Field(
    ...,
    title='直説法現在時制非完了相一人称複数',
    alias='直説法現在時制非完了相一人称複数',
  )
  indicative_present_imperfect_2nd_plural: str | None = Field(
    ...,
    title='直説法現在時制非完了相二人称複数',
    alias='直説法現在時制非完了相二人称複数',
  )
  indicative_present_imperfect_3rd_plural: str | None = Field(
    ...,
    title='直説法現在時制非完了相三人称複数',
    alias='直説法現在時制非完了相三人称複数',
  )
  indicative_present_perfect_1st_singular: str | None = Field(
    ...,
    title='直説法現在時制完遂相一人称単数',
    alias='直説法現在時制完遂相一人称単数',
  )
  indicative_present_perfect_2nd_singular: str | None = Field(
    ...,
    title='直説法現在時制完遂相二人称単数',
    alias='直説法現在時制完遂相二人称単数',
  )
  indicative_present_perfect_3rd_singular: str | None = Field(
    ...,
    title='直説法現在時制完遂相三人称単数',
    alias='直説法現在時制完遂相三人称単数',
  )
  indicative_present_perfect_1st_plural: str | None = Field(
    ...,
    title='直説法現在時制完遂相一人称複数',
    alias='直説法現在時制完遂相一人称複数',
  )
  indicative_present_perfect_2nd_plural: str | None = Field(
    ...,
    title='直説法現在時制完遂相二人称複数',
    alias='直説法現在時制完遂相二人称複数',
  )
  indicative_present_perfect_3rd_plural: str | None = Field(
    ...,
    title='直説法現在時制完遂相三人称複数',
    alias='直説法現在時制完遂相三人称複数',
  )
  indicative_present_consequential_1st_singular: str | None = Field(
    ...,
    title='直説法現在時制結果状態相一人称単数',
    alias='直説法現在時制結果状態相一人称単数',
  )
  indicative_present_consequential_2nd_singular: str | None = Field(
    ...,
    title='直説法現在時制結果状態相二人称単数',
    alias='直説法現在時制結果状態相二人称単数',
  )
  indicative_present_consequential_3rd_singular: str | None = Field(
    ...,
    title='直説法現在時制結果状態相三人称単数',
    alias='直説法現在時制結果状態相三人称単数',
  )
  indicative_present_consequential_1st_plural: str | None = Field(
    ...,
    title='直説法現在時制結果状態相一人称複数',
    alias='直説法現在時制結果状態相一人称複数',
  )
  indicative_present_consequential_2nd_plural: str | None = Field(
    ...,
    title='直説法現在時制結果状態相二人称複数',
    alias='直説法現在時制結果状態相二人称複数',
  )
  indicative_present_consequential_3rd_plural: str | None = Field(
    ...,
    title='直説法現在時制結果状態相三人称複数',
    alias='直説法現在時制結果状態相三人称複数',
  )
  indicative_present_preparative_1st_singular: str | None = Field(
    ...,
    title='直説法現在時制準備相一人称単数',
    alias='直説法現在時制準備相一人称単数',
  )
  indicative_present_preparative_2nd_singular: str | None = Field(
    ...,
    title='直説法現在時制準備相二人称単数',
    alias='直説法現在時制準備相二人称単数',
  )
  indicative_present_preparative_3rd_singular: str | None = Field(
    ...,
    title='直説法現在時制準備相三人称単数',
    alias='直説法現在時制準備相三人称単数',
  )
  indicative_present_preparative_1st_plural: str | None = Field(
    ...,
    title='直説法現在時制準備相一人称複数',
    alias='直説法現在時制準備相一人称複数',
  )
  indicative_present_preparative_2nd_plural: str | None = Field(
    ...,
    title='直説法現在時制準備相二人称複数',
    alias='直説法現在時制準備相二人称複数',
  )
  indicative_present_preparative_3rd_plural: str | None = Field(
    ...,
    title='直説法現在時制準備相三人称複数',
    alias='直説法現在時制準備相三人称複数',
  )
  indicative_present_inchoative_1st_singular: str | None = Field(
    ...,
    title='直説法現在時制起動相一人称単数',
    alias='直説法現在時制起動相一人称単数',
  )
  indicative_present_inchoative_2nd_singular: str | None = Field(
    ...,
    title='直説法現在時制起動相二人称単数',
    alias='直説法現在時制起動相二人称単数',
  )
  indicative_present_inchoative_3rd_singular: str | None = Field(
    ...,
    title='直説法現在時制起動相三人称単数',
    alias='直説法現在時制起動相三人称単数',
  )
  indicative_present_inchoative_1st_plural: str | None = Field(
    ...,
    title='直説法現在時制起動相一人称複数',
    alias='直説法現在時制起動相一人称複数',
  )
  indicative_present_inchoative_2nd_plural: str | None = Field(
    ...,
    title='直説法現在時制起動相二人称複数',
    alias='直説法現在時制起動相二人称複数',
  )
  indicative_present_inchoative_3rd_plural: str | None = Field(
    ...,
    title='直説法現在時制起動相三人称複数',
    alias='直説法現在時制起動相三人称複数',
  )
  indicative_present_terminative_1st_singular: str | None = Field(
    ...,
    title='直説法現在時制終結相一人称単数',
    alias='直説法現在時制終結相一人称単数',
  )
  indicative_present_terminative_2nd_singular: str | None = Field(
    ...,
    title='直説法現在時制終結相二人称単数',
    alias='直説法現在時制終結相二人称単数',
  )
  indicative_present_terminative_3rd_singular: str | None = Field(
    ...,
    title='直説法現在時制終結相三人称単数',
    alias='直説法現在時制終結相三人称単数',
  )
  indicative_present_terminative_1st_plural: str | None = Field(
    ...,
    title='直説法現在時制終結相一人称複数',
    alias='直説法現在時制終結相一人称複数',
  )
  indicative_present_terminative_2nd_plural: str | None = Field(
    ...,
    title='直説法現在時制終結相二人称複数',
    alias='直説法現在時制終結相二人称複数',
  )
  indicative_present_terminative_3rd_plural: str | None = Field(
    ...,
    title='直説法現在時制終結相三人称複数',
    alias='直説法現在時制終結相三人称複数',
  )


class AdjectiveDeclensions(BaseModel):
  type: Literal['adjective'] = Field(
    ...,
    title='adjective',
    description='The type of the entry.',
  )


class NounDeclensions(BaseModel):
  type: Literal['noun'] = Field(
    ...,
    title='noun',
    description='The type of the entry.',
  )


class Inflections(RootModel[Conjugations | AdjectiveDeclensions | NounDeclensions]):
  pass
