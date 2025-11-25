from typing import List, TypedDict, Literal, Dict, Any, Optional
from pydantic import BaseModel


class TeamWords(TypedDict):
    red: List[str]
    blue: List[str]
    neutral: List[str]
    black: str


class LeftTeamWords(TypedDict):
    red: List[str]
    blue: List[str]
    neutral: List[str]
    black: str
    left_words: List[str]
    known: List[str]


class Code(BaseModel):
    word: str
    number: int
    justification: str
    words_related: List[str]


class Choice(BaseModel):
    words: List[str]
    justification: str


class PlayerData(BaseModel):
    model_name: str
    temperature: float
    seed: int | None


class TeamData(BaseModel):
    captain: PlayerData
    guesser: PlayerData


class Teams(BaseModel):
    blue: TeamData
    red: TeamData


class RoundTeamData(BaseModel):
    secret_code: Code
    guesser_choice: Choice
    captain_prompt: Optional[str]
    guesser_prompt: Optional[str]


class Round(BaseModel):
    round: int
    blue_team: RoundTeamData
    red_team: RoundTeamData


class Results(BaseModel):
    words: TeamWords
    team_order: List[Literal["red", "blue"]]
    teams: Teams
    num_rounds: int
    rounds_info: List[Round]
    winner_team: Literal["red", "blue"]


class ToolCall(BaseModel):
    tool_name: str
    args: Dict[str, Any]


class LLMMessage(BaseModel):
    model_name: str
    content: Optional[str]
    tool_call: Optional[ToolCall]