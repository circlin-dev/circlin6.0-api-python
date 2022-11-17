import abc
from domain.version import Version


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, new_version):
        pass

    @abc.abstractmethod
    def get_one(self, target_version, is_force) -> Version:
        pass

    @abc.abstractmethod
    def get_list(self) -> Version:
        pass

    @abc.abstractmethod
    def update(self, target_version, is_force, type, description) -> Version:
        pass

    @abc.abstractmethod
    def delete(self, target_version) -> Version:
        pass


class VersionRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, version):
        self.session.add(version)

    def get_one(self, target_version, is_force):
        return self.session.query(Version).filter_by(version=target_version, is_force=is_force).first() # .one()은 NoResultFound 에러가 남

    def get_list(self):
        return self.session.query(Version).all()

    def update(self, target_version, is_force, type, description):
        return self.session.query(Version).filter_by(version=target_version.version).update(
            {
                "is_force": is_force,
                "type": type,
                "description": description
            },
            synchronize_session="fetch"
        )

    def delete(self, target_version):
        return self.session.query(Version).filter_by(version=target_version.version).delete(synchronize_session="fetch")


