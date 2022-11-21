import abc
from domain.file import File
from sqlalchemy import insert


class AbstractFileRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_file: File):
        pass


class FileRepository(AbstractFileRepository):
    def __init__(self, session):
        self.session = session

    def add(self, new_file: File):
        sql = insert(
            File
        ).values(

        )

        result = self.session.execute(sql)
        return result.inserted_primary_key[0]