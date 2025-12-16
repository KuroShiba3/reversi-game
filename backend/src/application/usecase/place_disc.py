from ..dto.place_disc import PlaceDiscInputDTO, PlaceDiscOutputDTO
from ...domain.model.position import Position
from ...domain.model.disc import Disc

class PlaceDisc:
    def __init__(self, game_repository):
        self.game_repository = game_repository

    def execute(self, input_dto: PlaceDiscInputDTO) -> PlaceDiscOutputDTO:
        game = self.game_repository.find_by_id(input_dto.game_id)
        disc = Disc[input_dto.disc]
        position = Position(input_dto.position["row"], input_dto.position["col"])
        game.place_disc(position, disc)
        self.game_repository.save(game)
        board_state = [
            {"row": pos.row, "col": pos.col, "disc": disc.name}
            for pos, disc in game.board.cells.items()
        ]
        return PlaceDiscOutputDTO(board_state, game.current_player.name)
