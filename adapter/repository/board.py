from adapter.orm import areas, blocks, board_comments, board_images, follows
from domain.board import Board, BoardImage, BoardLike
from domain.user import User

import abc
from sqlalchemy import select, update, insert, desc, and_, case, text, func


class AbstractBoardRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_board: Board) -> int:
        pass

    @abc.abstractmethod
    def get_one(self, board_id: int, user_id: int) -> Board:
        pass

    @abc.abstractmethod
    def get_list(self, user_id: int, category_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_board(self, category_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_list_by_user(self, target_user_id: int, category_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_board_of_user(self, target_user_id: int, category_id: int) -> int:
        pass

    @abc.abstractmethod
    def get_list_of_following_users(self, target_user_id: int, category_id: int, page_cursor: int, limit: int) -> list:
        pass

    @abc.abstractmethod
    def count_number_of_board_of_following_users(self, target_user_id: int, category_id: int) -> int:
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

    def add(self, new_board: Board) -> int:
        sql = insert(
            Board
        ).values(
            user_id=new_board.user_id,
            board_category_id=new_board.board_category_id,
            body=new_board.body,
            is_show=new_board.is_show
        )
        result = self.session.execute(sql)
        return result.inserted_primary_key[0]

    def get_one(self, board_id: int, user_id: int) -> Board:
        # subqueries
        area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)
        block_targets = select(blocks.c.target_id).where(blocks.c.user_id == user_id)
        comments_count = select(
            func.count(board_comments.c.id)
        ).where(and_(
            board_comments.c.board_id == Board.id,
            board_comments.c.deleted_at == None
        ))
        follower_count = select(func.count(follows.c.id)).where(follows.c.target_id == User.id)
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
        likes_count = select(func.count(BoardLike.id)).where(BoardLike.board_id == Board.id)

        sql = select(
            Board.id,
            Board.body,
            func.date_format(Board.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            User.id.label('user_id'),
            User.profile_image,
            case((User.id.in_(followings), 1), else_=0).label("followed"),
            User.nickname,
            case((User.id.in_(block_targets), 1), else_=0).label("is_blocked"),
            Board.board_category_id,
            case((text(f"{user_id} in (SELECT user_id FROM board_likes WHERE board_id = boards.id)"), 1), else_=0).label('liked'),
            Board.is_show,
            Board.deleted_at,
            func.ifnull(
                func.json_arrayagg(
                    func.json_object(
                        'order', BoardImage.order,
                        'mimeType', BoardImage.mime_type,
                        'pathname', BoardImage.path,
                        'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                                    'mimeType', bi.mime_type,
                                    'pathname', bi.path,
                                    'width', bi.width
                                    )), JSON_ARRAY()) FROM board_images bi WHERE bi.original_file_id = board_images.id)""")
                    )
                ),
                func.json_array()
            ).label('images'),
            follower_count.label('followers'),
            area.label('area'),
            likes_count.label('likes_count'),
            comments_count.label('comments_count')
        ).select_from(
            Board
        ).join(
            User, Board.user_id == User.id
        ).join(
            BoardImage, Board.id == BoardImage.board_id, isouter=True
        ).where(
            and_(
                Board.id == board_id,
                Board.deleted_at == None,
                BoardImage.original_file_id == None
            )
        ).group_by(
            Board.id
        ).order_by(
            desc(BoardImage.order)
        )
        result = self.session.execute(sql).first()
        return result

    def get_list(self, user_id: int, category_id: int, page_cursor: int, limit: int) -> list:
        condition = and_(
            Board.deleted_at == None,
            Board.id < page_cursor,
            BoardImage.original_file_id == None
        ) if category_id == 0 else \
            and_(
                Board.deleted_at == None,
                Board.id < page_cursor,
                BoardImage.original_file_id == None,
                Board.board_category_id == category_id
            )
        # subqueries
        area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)
        block_targets = select(blocks.c.target_id).where(blocks.c.user_id == user_id)
        comments_count = select(
            func.count(board_comments.c.id)
        ).where(and_(
            board_comments.c.board_id == Board.id,
            board_comments.c.deleted_at == None
        ))
        follower_count = select(func.count(follows.c.id)).where(follows.c.target_id == User.id)
        followings = select(follows.c.target_id).where(follows.c.user_id == user_id)
        likes_count = select(func.count(BoardLike.id)).where(BoardLike.board_id == Board.id)

        sql = select(
            Board.id,
            Board.body,
            func.date_format(Board.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            User.id.label('user_id'),
            User.profile_image,
            case((User.id.in_(followings), 1), else_=0).label("followed"),
            User.nickname,
            case((User.id.in_(block_targets), 1), else_=0).label("is_blocked"),
            Board.board_category_id,
            case((text(f"{user_id} in (SELECT user_id FROM board_likes WHERE board_id = boards.id)"), 1), else_=0).label('liked'),
            Board.is_show,
            func.concat(func.lpad(Board.id, 15, '0')).label('cursor'),
            func.ifnull(
                func.json_arrayagg(
                    func.json_object(
                        'order', BoardImage.order,
                        'mimeType', BoardImage.mime_type,
                        'pathname', BoardImage.path,
                        'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                                    'mimeType', bi.mime_type,
                                    'pathname', bi.path,
                                    'width', bi.width
                                    )), JSON_ARRAY()) FROM board_images bi WHERE bi.original_file_id = board_images.id)""")
                    )
                ),
                func.json_array()
            ).label('images'),
            follower_count.label('followers'),
            area.label('area'),
            likes_count.label('likes_count'),
            comments_count.label('comments_count'),
        ).select_from(
            Board
        ).join(
            User, Board.user_id == User.id
        ).join(
            BoardImage, Board.id == BoardImage.board_id, isouter=True
        ).where(
            condition
        ).group_by(
            Board.id
        ).order_by(
            desc(Board.id),
            desc(BoardImage.order)
        ).limit(limit)
        result = self.session.execute(sql)

        return result

    def count_number_of_board(self, category_id: int) -> int:
        condition = and_(
            Board.deleted_at == None,
        ) if category_id == 0 else \
            and_(
                Board.deleted_at == None,
                Board.board_category_id == category_id
            )

        sql = select(func.count(Board.id)).where(condition)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_list_by_user(self, target_user_id: int, category_id: int, page_cursor: int, limit: int) -> list:
        condition = and_(
            Board.user_id == target_user_id,
            Board.deleted_at == None,
            BoardImage.original_file_id == None,
            Board.id < page_cursor,
        ) if category_id == 0 else \
            and_(
                Board.user_id == target_user_id,
                Board.board_category_id == category_id,
                Board.deleted_at == None,
                BoardImage.original_file_id == None,
                Board.id < page_cursor,
            )
        # subqueries
        area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)
        block_targets = select(blocks.c.target_id).where(blocks.c.user_id == target_user_id)
        comments_count = select(
            func.count(board_comments.c.id)
        ).where(and_(
            board_comments.c.board_id == Board.id,
            board_comments.c.deleted_at == None
        ))
        follower_count = select(func.count(follows.c.id)).where(follows.c.target_id == User.id)
        followings = select(follows.c.target_id).where(follows.c.user_id == target_user_id)
        likes_count = select(func.count(BoardLike.id)).where(BoardLike.board_id == Board.id)

        sql = select(
            Board.id,
            Board.body,
            func.date_format(Board.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            User.id.label('user_id'),
            User.profile_image,
            case((User.id.in_(followings), 1), else_=0).label("followed"),
            User.nickname,
            case((User.id.in_(block_targets), 1), else_=0).label("is_blocked"),
            Board.board_category_id,
            case((text(f"{target_user_id} in (SELECT user_id FROM board_likes WHERE board_id = boards.id)"), 1), else_=0).label('liked'),
            Board.is_show,
            func.concat(func.lpad(Board.id, 15, '0')).label('cursor'),
            func.ifnull(
                func.json_arrayagg(
                    func.json_object(
                        'order', BoardImage.order,
                        'mimeType', BoardImage.mime_type,
                        'pathname', BoardImage.path,
                        'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                                    'mimeType', bi.mime_type,
                                    'pathname', bi.path,
                                    'width', bi.width
                                    )), JSON_ARRAY()) FROM board_images bi WHERE bi.original_file_id = board_images.id)""")
                    )
                ),
                func.json_array()
            ).label('images'),
            follower_count.label('followers'),
            area.label('area'),
            likes_count.label('likes_count'),
            comments_count.label('comments_count'),
        ).select_from(
            Board
        ).join(
            User, Board.user_id == User.id
        ).join(
            BoardImage, Board.id == BoardImage.board_id, isouter=True
        ).where(
            condition
        ).group_by(
            Board.id
        ).order_by(
            desc(Board.id),
            desc(BoardImage.order)
        ).limit(limit)
        result = self.session.execute(sql)

        return result

    def count_number_of_board_of_user(self, target_user_id: int, category_id: int) -> int:
        condition = and_(
            Board.user_id == target_user_id,
            Board.deleted_at == None,
        ) if category_id == 0 else \
            and_(
                Board.user_id == target_user_id,
                Board.board_category_id == category_id,
                Board.deleted_at == None,
            )
        sql = select(func.count(Board.id)).where(condition)
        total_count = self.session.execute(sql).scalar()
        return total_count

    def get_list_of_following_users(self, target_user_id: int, category_id: int, page_cursor: int, limit: int) -> list:
        # subqueries
        area = select(areas.c.name).where(areas.c.code == func.concat(func.substring(User.area_code, 1, 5), '00000')).limit(1)
        block_targets = select(blocks.c.target_id).where(blocks.c.user_id == target_user_id)
        comments_count = select(
            func.count(board_comments.c.id)
        ).where(and_(
            board_comments.c.board_id == Board.id,
            board_comments.c.deleted_at == None
        ))
        follower_count = select(func.count(follows.c.id)).where(follows.c.target_id == User.id)
        followings = select(follows.c.target_id).where(follows.c.user_id == target_user_id)
        likes_count = select(func.count(BoardLike.id)).where(BoardLike.board_id == Board.id)
        condition = and_(
            Board.user_id.in_(followings),
            Board.deleted_at == None,
            BoardImage.original_file_id == None,
            Board.id < page_cursor,
        ) if category_id == 0 else \
            and_(
                Board.user_id.in_(followings),
                Board.board_category_id == category_id,
                Board.deleted_at == None,
                BoardImage.original_file_id == None,
                Board.id < page_cursor,
            )

        sql = select(
            Board.id,
            Board.body,
            func.date_format(Board.created_at, '%Y/%m/%d %H:%i:%s').label('created_at'),
            User.id.label('user_id'),
            User.profile_image,
            case((User.id.in_(followings), 1), else_=0).label("followed"),
            User.nickname,
            case((User.id.in_(block_targets), 1), else_=0).label("is_blocked"),
            Board.board_category_id,
            case((text(f"{target_user_id} in (SELECT user_id FROM board_likes WHERE board_id = boards.id)"), 1), else_=0).label('liked'),
            Board.is_show,
            func.concat(func.lpad(Board.id, 15, '0')).label('cursor'),
            func.ifnull(
                func.json_arrayagg(
                    func.json_object(
                        'order', BoardImage.order,
                        'mimeType', BoardImage.mime_type,
                        'pathname', BoardImage.path,
                        'resized', text(f"""(SELECT IFNULL(JSON_ARRAYAGG(JSON_OBJECT(
                                    'mimeType', bi.mime_type,
                                    'pathname', bi.path,
                                    'width', bi.width
                                    )), JSON_ARRAY()) FROM board_images bi WHERE bi.original_file_id = board_images.id)""")
                    )
                ),
                func.json_array()
            ).label('images'),
            follower_count.label('followers'),
            area.label('area'),
            likes_count.label('likes_count'),
            comments_count.label('comments_count'),
        ).select_from(
            Board
        ).join(
            User, Board.user_id == User.id
        ).join(
            BoardImage, Board.id == BoardImage.board_id, isouter=True
        ).where(
            condition
        ).group_by(
            Board.id
        ).order_by(
            desc(Board.id),
            desc(BoardImage.order)
        ).limit(limit)
        result = self.session.execute(sql)

        return result

    def count_number_of_board_of_following_users(self, target_user_id: int, category_id: int) -> int:
        followings = select(follows.c.target_id).where(follows.c.user_id == target_user_id)
        condition = and_(
            Board.user_id.in_(followings),
            Board.deleted_at == None,
        ) if category_id == 0 else \
            and_(
                Board.user_id.in_(followings),
                Board.board_category_id == category_id,
                Board.deleted_at == None,
            )
        sql = select(func.count(Board.id)).where(condition)
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
