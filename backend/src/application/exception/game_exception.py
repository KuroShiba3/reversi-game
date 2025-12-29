from .base import ApplicationException


class GameNotFoundException(ApplicationException):
    """ゲームが見つからない場合

    リポジトリからゲームを取得しようとしたが、指定されたIDのゲームが存在しない場合に発生。
    """

    def __init__(self, game_id: str):
        self.game_id = game_id
        super().__init__(f"ゲームが見つかりません: {game_id}")
