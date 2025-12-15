from ...domain.repository.game_repository import IGameRepository
from ...domain.model.game import Game

class StartGame:
    def __init__(self, game_repository: IGameRepository):
        self.game_repository = game_repository

    def execute(self):
        game = Game.create()
        return self.game_repository.save(game)