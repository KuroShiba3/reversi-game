from ..dto import GetValidMovesInputDTO, GetValidMovesOutputDTO

class GetValidMoves:
    def __init__(self, game_repository):
        self.game_repository = game_repository

    def execute(self, input_dto: GetValidMovesInputDTO) -> GetValidMovesOutputDTO:
        game = self.game_repository.find_by_id(input_dto.game_id)
        return game.get_valid_moves()