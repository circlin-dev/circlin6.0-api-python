import abc
from domain.board import BoardImage
from sqlalchemy import insert


class AbstractBoardImageRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_board_image: BoardImage):
        pass


class BoardImageRepository(AbstractBoardImageRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_board_image: BoardImage):
        sql = insert(
            BoardImage
        ).values(
            board_id=new_board_image.board_id,
            order=new_board_image.order,
            path=new_board_image.path,
            file_name=new_board_image.file_name,
            mime_type=new_board_image.mime_type,
            size=new_board_image.size,
            width=new_board_image.width,
            height=new_board_image.height,
            original_file_id=new_board_image.original_file_id
        )
        self.session.execute(sql)
