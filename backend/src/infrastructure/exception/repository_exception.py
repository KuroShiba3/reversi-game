from .base import InfrastructureException


class RepositoryException(InfrastructureException):
    """リポジトリ操作のエラー

    データベースの読み書き中にエラーが発生した場合に発生。
    """

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"リポジトリエラー ({operation}): {str(original_error)}")
