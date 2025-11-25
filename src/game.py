from typing import List, Literal, Tuple
import random
import copy

from src.llm_wrapper import LLMModel
from src.schemas import (
    Results, 
    Code, 
    Choice, 
    Teams, 
    TeamWords, 
    LeftTeamWords, 
    RoundTeamData,
    Round,
    TeamData,
    PlayerData
)
from src.tools import indicate_secret_code, choose_words
from src.prompts import (
    captain_system_prompt, 
    guesser_system_prompt, 
    captain_round_message, 
    guesser_round_message
)
from src.words import WORDS



class Board:

    words: List[str]
    first_team_color: Literal["red", "blue"]
    second_team_color: Literal["red", "blue"]
    team_words: TeamWords
    left_team_words: LeftTeamWords
    known_words: List[str] # TODO: remove, Not used

    def __init__(self, words: List[str] = [w.lower() for w in WORDS]):
        self._set_up_board(words)
        return
    
    def _set_up_board(self, words: List[str]) -> None:
        self.words: List[str] = self.generate_game_words(words)
        self._set_teams_order()
        self._split_team_words()
        return

    def _set_teams_order(self) -> None:
        team_order = random.sample(["red", "blue"], 2)
        self.first_team_color: Literal["red", "blue"] = team_order[0]
        self.second_team_color: Literal["red", "blue"] = team_order[1]
        return
    
    def generate_game_words(self, words: List[str]) -> List[str]:
        return random.sample(words, 25)
    
    def _split_team_words(self):

        if self.first_team_color == "red":
            red_words = self.words[:9]
            blue_words = self.words[9:17]
        else:
            blue_words = self.words[:9]
            red_words = self.words[9:17]

        team_words = TeamWords(
            red = red_words,
            blue = blue_words,
            neutral = self.words[17:-1],
            black =  self.words[-1]
        )
        self.team_words: TeamWords = copy.deepcopy(team_words)
        self.left_team_words: LeftTeamWords = LeftTeamWords(
            red = team_words["red"],
            blue = team_words["blue"],
            neutral = team_words["neutral"],
            black = team_words["black"],
            left_words = copy.deepcopy(self.words),
            known = []
        )
        self.known_words: List[str] = []
        return

    def remove_guessed_word(self, word: str, group: str) -> None:
        self.left_team_words[group].remove(word)
        self.left_team_words["left_words"].remove(word)
        self.left_team_words["known"].append(word)
        return
     


class Player:

    name: str
    role: Literal["captain", "guesser"]
    temperature: float
    seed: int | None
    tools: List
    model: LLMModel
    team: Literal["red", "blue"]
    model_name: str

    def __init__(
            self, 
            name: str,
            model: LLMModel,
            tools: List,
            role: Literal["captain", "guesser"]
        ) -> None:
        self.name: str = name
        self.role: Literal["captain", "guesser"] = role
        self.model: LLMModel = model
        self.temperature: float = self.model.temperature
        self.seed: int | None = self.model.seed
        self.tools: List = tools
        self.model_name: str = self.model.model_name
        return
    
    def set_team(self, color: Literal["red", "blue"]) -> None:
        self.team = color
        return
    

class Captain(Player):

    name: str
    role: Literal["captain", "guesser"]
    temperature: float
    seed: int | None
    tools: List
    model: LLMModel
    team: Literal["red", "blue"]
    model_name: str

    def __init__(
            self, 
            name: str,
            model: LLMModel,
            tools: List = [indicate_secret_code],
            role: Literal["captain"] = "captain",
        ) -> None:
        super().__init__(
            name,  
            model,
            tools,
            role
        )
    
    def say_secret_code(
            self, 
            game_history, 
            red_words, 
            blue_words, 
            neutral_words, 
            black_word
        ) -> tuple[Code, str]:

        # system_prompt = {
        #     "role": "system", 
        #     "content": captain_system_prompt
        # }

        # round_message = {
        #     "role": "user", 
        #     "content": captain_round_message.format(
        #         team_color=self.team, 
        #         game_history=game_history,
        #         red_words=red_words,
        #         blue_words=blue_words,
        #         neutral_words=neutral_words,
        #         black_word=black_word
        #     )
        # }

        # response = ollama.chat(
        #     model=self.model_name,
        #     messages=[system_prompt, round_message], # TODO: add messages
        #     tools=self.tools,
        #     options={"temperature": self.temperature, "seed": self.seed}
        # )
        msg = captain_round_message.format(
                team_color=self.team, 
                game_history=game_history,
                red_words=red_words,
                blue_words=blue_words,
                neutral_words=neutral_words,
                black_word=black_word
            )
        system_prompt = dict(role="system", content=captain_system_prompt)
        round_message = dict(role="user", content=msg)
        response = self.model.chat([system_prompt, round_message])
        args = response.tool_call.args
        return Code(
            word=args["word"], 
            number=args["number"], 
            justification=args["justification"],
            words_related=args["words_related"]
        ), msg
    

class Guesser(Player):

    name: str
    role: Literal["captain", "guesser"]
    temperature: float
    seed: int | None
    tools: List
    model: LLMModel
    team: Literal["red", "blue"]
    model_name: str

    def __init__(
            self, 
            name: str,
            model: LLMModel,
            tools: List = [choose_words],
            role: Literal["guesser"] = "guesser"
        ) -> None:
        super().__init__(
            name, 
            model, 
            tools,
            role
        )

    def choose_words(self, game_history, words, secret_code: Tuple) -> tuple[Choice, str]:

        # system_prompt = {
        #     "role": "system", 
        #     "content": guesser_system_prompt
        # }

        # round_message = {
        #     "role": "user", 
        #     "content": guesser_round_message.format(
        #         team_color=self.team, 
        #         game_history=game_history,
        #         words=words,
        #         secret_code=secret_code
        #     )
        # }

        # response = ollama.chat(
        #     model=self.model_name,
        #     messages=[system_prompt, round_message], # TODO: add messages
        #     tools=self.tools,
        #     options={"temperature": self.temperature, "seed": self.seed}
        # )
        msg = guesser_round_message.format(
                team_color=self.team, 
                game_history=game_history,
                words=words,
                secret_code=secret_code
            )
        system_prompt = dict(role="system", content=guesser_system_prompt)
        round_message = dict(role="user", content=msg)
        response = self.model.chat([system_prompt, round_message])
        return Choice(
            words = response.tool_call.args["words"],
            justification = response.tool_call.args["justification"]
        ), msg


class Team:

    color: Literal["red", "blue"]
    players: List[Captain | Guesser]
    captain: Captain
    guesser: Guesser

    def __init__(
            self, 
            color: Literal["blue", "red"],
            players: List[Captain | Guesser]
        ) -> None:
        self.color: Literal["blue", "red"] = color
        self.players: List[Captain | Guesser] = players
        self.captain, self.guesser = self.get_players_role()
        self.set_players_teams()
        return
    
    def set_players_teams(self):
        for player in self.players:
            player.set_team(self.color)
    
    def get_players_role(self) -> List[Captain | Guesser]:
        if self.players[0].role == "captain":
            return self.players
        else:
            return self.players[::-1]
    
    @staticmethod
    def get_opposite_team_color(color: Literal["blue", "red"]) -> Literal["red", "blue"]:
        return {"red": "blue", "blue": "red"}[color]


class SecretCodeGame:

    team_blue: Team
    team_red: Team
    board: Board
    round: int
    game_over: bool
    game_history: List
    winner_team: Literal["red", "blue"]

    def __init__(
            self,
            team_blue: Team,
            team_red: Team,
            board: Board
    ):
        self.team_blue: Team = team_blue
        self.team_red: Team = team_red
        self.board: Board = board
        self.round: int = 0
        self.game_over: bool = False
        self.game_history: List = []
        return
    
    def get_teams_order(self) -> List[Team]:
        teams = {
            "red": self.team_red,
            "blue": self.team_blue
        }
        first_team = teams[self.board.first_team_color]
        second_team = teams[self.board.second_team_color]
        return [first_team, second_team]
    
    def play(self) -> None:
        total_rounds_info = []
        while not self.game_over:
            # print("\n\n\nGame History")
            # print(self.game_history)
            self.game_history.append(f"\n**Round {self.round}**")
            first_team, second_team = self.get_teams_order()
            first_team_round_info = self._play_round(first_team)
            second_team_round_info = self._play_round(second_team)
            self.round += 1
            round_info = Round(
                round = self.round,
                blue_team = first_team_round_info if first_team.color == "blue" else second_team_round_info,
                red_team = second_team_round_info if second_team.color == "red" else first_team_round_info
            )
            # round_info = {
            #     "round": self.round,
            #         "teams": {
            #             first_team.color: first_team_round_info,
            #             second_team.color: second_team_round_info
            #         }
            # }
            total_rounds_info.append(round_info)
        self.save_results(total_rounds_info)
        return
    
    def _play_round(self, team: Team) -> RoundTeamData:
        secret_code, captain_prompt = team.captain.say_secret_code(
            game_history="\n".join(self.game_history),
            red_words=self.board.left_team_words["red"],
            blue_words=self.board.left_team_words["blue"],
            neutral_words=self.board.left_team_words["neutral"],
            black_word=self.board.team_words["black"]
        )
        guesser_choice, guesser_prompt = team.guesser.choose_words(
            game_history="\n".join(self.game_history),
            words=self.board.left_team_words["left_words"],
            secret_code=(secret_code.word, secret_code.number)
        ) # TODO: chosen words validation

        msg = f"""Team {team.color} turn.
            Captain said the following secret code: {secret_code.word}, {secret_code.number}."""
        
        self.game_history.append(
            msg
        )

        # print("\nCode:", secret_code)
        # print("\nChoice:", guesser_choice)

        self._evaluate_guessed_words(guesser_choice.words, team)
        return RoundTeamData(
            secret_code = secret_code,
            guesser_choice = guesser_choice,
            captain_prompt = captain_prompt,
            guesser_prompt = guesser_prompt
        )
            
    def _evaluate_guessed_words(self, guessed_words: List[str], team: Team):
        opposite_team_color: Literal["red", "blue"] = team.get_opposite_team_color(team.color)
        for word in guessed_words:
            # TODO: save chosen word if previous word was correct: valid_words.append(word)

            if word.lower() in self.board.left_team_words["black"]:
                self.game_over = True
                self.winner_team: Literal["red", "blue"] = opposite_team_color
                break

            elif word.lower() in self.board.left_team_words[team.color]:
                self.board.remove_guessed_word(word.lower(), team.color)
                self.game_history.append(
                    f"""{team.color} team Guesser chooses the word '{word}' which belongs to the group '{team.color}'"""
                )
                if len(self.board.left_team_words[team.color]) == 0:
                    self.game_over = True
                    self.winner_team: Literal["red", "blue"] = team.color
                    break

            elif word.lower() in self.board.left_team_words[opposite_team_color]:
                self.board.remove_guessed_word(word.lower(), opposite_team_color)
                self.game_history.append(
                    f"""{team.color} team Guesser chooses the word '{word}' which belongs to the group '{opposite_team_color}'"""
                )
                break
            
            elif word.lower() in self.board.left_team_words["neutral"]:
                self.board.remove_guessed_word(word.lower(), "neutral")
                self.game_history.append(
                    f"""{team.color} team Guesser chooses the word '{word}' which belongs to the group 'neutral'"""
                )
                break

            else:
                raise Exception("Guessed word does not exist")
        
    def save_results(self, rounds_info: List[Round]) -> None:
        self.results = Results(
            words = self.board.team_words,
            team_order = [self.board.first_team_color, self.board.second_team_color],
            teams = Teams(
                blue = TeamData(
                    captain = PlayerData(
                        model_name = self.team_blue.captain.model_name,
                        temperature = self.team_blue.captain.temperature,
                        seed = self.team_blue.captain.seed
                    ),
                    guesser = PlayerData(
                        model_name = self.team_blue.guesser.model_name,
                        temperature = self.team_blue.guesser.temperature,
                        seed = self.team_blue.guesser.seed
                    ),
                ),
                red = TeamData(
                    captain = PlayerData(
                        model_name = self.team_red.captain.model_name,
                        temperature = self.team_red.captain.temperature,
                        seed = self.team_red.captain.seed
                    ),
                    guesser = PlayerData(
                        model_name = self.team_red.guesser.model_name,
                        temperature = self.team_red.guesser.temperature,
                        seed = self.team_red.guesser.seed
                    )
                ),
            ),
            num_rounds = self.round,
            rounds_info = rounds_info,
            winner_team = self.winner_team
        )
        # self.results = {
        #     "words": self.board.words,
        #     "team_order": [self.board.first_team_color, self.board.second_team_color],
        #     "teams": {
        #         "blue": {
        #             "captain":{
        #                 "model_name": self.team_blue.captain.name,
        #                 "temperature": self.team_blue.captain.temperature,
        #                 "seed": self.team_blue.captain.seed
        #             },
        #             "guesser":{
        #                 "model_name": self.team_blue.guesser.name,
        #                 "temperature": self.team_blue.guesser.temperature,
        #                 "seed": self.team_blue.guesser.seed
        #             }
        #         },
        #         "red":{
        #             "captain":{
        #                 "model_name": self.team_red.captain.name,
        #                 "temperature": self.team_red.captain.temperature,
        #                 "seed": self.team_red.captain.seed
        #             },
        #             "guesser":{
        #                 "model_name": self.team_red.guesser.name,
        #                 "temperature": self.team_red.guesser.temperature,
        #                 "seed": self.team_red.guesser.seed
        #             }
        #         },
        #     },
        #     "num_rounds": self.round,
        #     "rounds": rounds_info,
        #     "winner_team": self.winner_team
        # }
        return