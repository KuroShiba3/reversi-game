from ...domain.repository.game_repository import GameRepository
from ...domain.model.game import Game
from ..dto.start_game import StartGameOutputDTO

class StartGame:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self) -> StartGameOutputDTO:
        new_game = Game.create()
        await self._game_repository.save(new_game)

        board_state = [
            {"row": pos.row, "col": pos.col, "disc": disc.name}
            for pos, disc in new_game.board.cells.items()
        ]

        return StartGameOutputDTO(
            str(new_game.id),
            board_state,
            new_game.current_player.name,
            new_game.status.value
        )