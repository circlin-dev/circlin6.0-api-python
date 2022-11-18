import abc
from domain.board import BoardFile
from sqlalchemy import insert


class AbstractBoardFileRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, order: int, new_board_id: int, new_file_id: int):
        pass


class BoardFileRepository(AbstractBoardFileRepository):
    def __init__(self, session):
        self.session = session

    def add(self, order: int, new_board_id: int, new_file_id: int):
        sql = insert(
            BoardFile
        ).values(
            board_id=new_board_id,
            order=order,
            file_id=new_file_id,
        )
        self.session.execute(sql)