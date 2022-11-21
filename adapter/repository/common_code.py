from domain.common_code import CommonCode
from sqlalchemy import select, update, delete, insert, desc, and_, case, text, func
import abc


class AbstractCommonCodeRepository(abc.ABC):
    @abc.abstractmethod
    def get_content_by_large_category(self, large_category: str) -> dict:
        pass


class CommonCodeRepository(AbstractCommonCodeRepository):
    def __init__(self, session):
        self.session = session

    def get_content_by_large_category(self, large_category: str) -> dict:
        sql = select(
            CommonCode.ctg_sm,
            CommonCode.content_ko
        ).where(
            CommonCode.ctg_lg == large_category
        )

        result = self.session.execute(sql)

        small_category_and_message = {}
        for data in result:
            small_category_and_message[data[0]] = data[1]

        return small_category_and_message
