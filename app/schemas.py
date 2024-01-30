from datetime import datetime

from pydantic import BaseModel, validator


class TournamentSchema(BaseModel):
    name: str
    date_start: datetime
    date_end: datetime

    @validator('date_end')
    def validate_date_end(cls, v, values):
        if 'date_start' in values and v <= values['date_start']:
            raise ValueError('date_end deve ser maior do que date_start')
        return v


class TournamentSchemaResponse(TournamentSchema):
    id: int
    name: str
    date_start: datetime
    date_end: datetime
