from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class LatestVersion:
    version: str
    is_force: int


class Version:
    def __init__(self, version: str or None):
        self.version = version

    def is_latest(self, target_version: LatestVersion) -> bool:
        return self.version == target_version.version
