from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class TournamentSchema(BaseModel):
    name: str
    date_start: datetime
    date_end: datetime

    @validator('date_end', pre=True, always=True)
    def validate_date_end(cls, v, values):

        if 'date_start' in values:
            data_dt1 = datetime.fromisoformat(str(v))
            if data_dt1 < values['date_start']:
                raise ValueError('date_end must be greater than date_start')
        return v


class TournamentSchemaResponse(TournamentSchema):
    id: int
    name: str
    date_start: datetime
    date_end: datetime


class CompetitorSchema(BaseModel):
    names: List[str]


class MatchSchema(BaseModel):
    competitor_1_id: str
    competitor_2_id: Optional[str]
    winner: Optional[str]
    state: str
    round: int


class MatchTournamentRound(BaseModel):
    round_name: str
    matches: List[MatchSchema]


class MatchTournamentSchema(BaseModel):
    rounds: List[MatchTournamentRound]


class WinnerRegistrationSchema(BaseModel):
    name: str
