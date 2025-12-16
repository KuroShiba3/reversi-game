from ...domain.repository.game_repository import IGameRepository
from ...domain.model.game import Game
from ..dto.start_game import StartGameOutputDTO

class StartGame:
    def __init__(self, game_repository: IGameRepository):
        self.game_repository = game_repository

    def execute(self):
        new_game = Game.create()
        new_game = self.game_repository.save(new_game)
        board_state = [
            {"row": pos.row, "col": pos.col, "disc": disc.name}
            for pos, disc in new_game.board.cells.items()
        ]
        return StartGameOutputDTO(str(new_game.id), board_state, new_game.current_player.name)