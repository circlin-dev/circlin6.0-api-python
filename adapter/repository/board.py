from domain.board import Board, BoardFile
from domain.user import User
from domain.file import File

import abc
from sqlalchemy import select, update, insert, desc, and_, case, text, func


class AbstractBoardRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_board: Board) -> Board:
        pass

    @abc.abstractmethod
    def get_one(self, board_id: int) -> Board:
        pass

    @abc.abstractmethod
    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_board(self) -> int:
        pass

    @abc.abstractmethod
    def update(self, board: Board) -> Board:
        pass

    @abc.abstractmethod
    def delete(self, board: Board) -> Board:
        pass


class BoardRepository(AbstractBoardRepository):
    def __init__(self, session):
        self.session = session

    def get_one(self, board_id: int) -> Board:
        sql = select(Board).where(Board.id == board_id)
        result = self.session.execute(sql).scalars().first()

        result.is_show = True if result.is_show == 1 else False

        return result

    def add(self, new_board: Board):
        pass

    def get_list(self, user_id: int, page_cursor: int, limit: int) -> list:
        sql = select(
            Board.id,
            Board.body,
            func.date_format(Board.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            User.id.label('user_id'),
            User.profile_image,
            case(
                (text(f"users.id in (SELECT target_id FROM follows WHERE user_id={user_id})"), 1),
                else_=0
            ).label("followed"),
            User.nickname,
            case(
                (text(f"users.id in (SELECT target_id FROM blocks WHERE user_id={user_id})"), 1),
                else_=0
            ).label("is_blocked"),
            Board.board_category_id,
            case(
                (text(f"{user_id} in (SELECT user_id FROM board_likes WHERE board_id = boards.id)"), 1),
                else_=0
            ).label('liked'),
            Board.is_show,
            func.concat(func.lpad(Board.id, 15, '0')).label('cursor'),
            text(f"""
                IFNULL(
                    JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'order', board_files.order,
                            'file_id', board_files.file_id,
                            'mimeType', files.mime_type,
                            'pathname', files.pathname,
                            'resized', (
                                SELECT IFNULL(
                                    JSON_ARRAYAGG(
                                        JSON_OBJECT(
                                            'mimeType', ff.mime_type,
                                            'pathname', ff.pathname,
                                            'width', ff.width
                                        )
                                    ), JSON_ARRAY()
                                ) FROM files ff WHERE files.id = ff.original_file_id
                            )
                        )
                    ),
                    JSON_ARRAY()
                ) AS images"""),
            text(f"(SELECT COUNT(*) FROM follows f WHERE f.target_id = users.id) AS followers"),  # user.followers
            text(f"(SELECT a.name AS area FROM areas a WHERE a.code = CONCAT(SUBSTRING(users.area_code, 1, 5), '00000') LIMIT 1) AS area"),  # user.area
            text("(SELECT COUNT(*) AS likes_count FROM board_likes bl WHERE bl.board_id = boards.id) AS likes_count"),  # likesCount
            text("(SELECT COUNT(*) AS comments_count FROM board_comments bcm WHERE bcm.board_id = boards.id AND bcm.deleted_at IS NULL) AS comments_count"),  # commentsCount
        ).select_from(
            Board
        ).join(
            User, Board.user_id == User.id
        ).join(
            BoardFile, Board.id == BoardFile.board_id, isouter=True
        ).join(
            File, BoardFile.file_id == File.id, isouter=True
        ).where(
            and_(
                Board.deleted_at == None,
                Board.id < page_cursor
            )
        ).group_by(
            Board.id
        ).order_by(
            desc(Board.id)
        ).limit(limit)
        result = self.session.execute(sql)

        return result

    def count_number_of_board(self) -> int:
        sql = select(func.count(Board.id)).where(Board.deleted_at == None)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def update(self, board: Board):
        sql = update(
            Board
        ).where(
            Board.id == board.id
        ).values(
            body=board.body,
            is_show=board.is_show,
            board_category_id=board.board_category_id
        )
        return self.session.execute(sql)

    def delete(self, board: Board):
        sql = update(Board).where(Board.id == board.id).values(deleted_at=func.now())
        return self.session.execute(sql)
