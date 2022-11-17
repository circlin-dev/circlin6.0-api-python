from . import api
from adapter.database import db_session
from adapter.orm import version_mappers
from adapter.repository.version import VersionRepository
from domain.version import Version
from flask import request
import json
from sqlalchemy.orm import clear_mappers


@api.route('/latest_version', methods=['GET'])
def get_latest_version():
    version_mappers()
    repo = VersionRepository(db_session)
    data = repo.get_one(target_version='5.5.89', is_force=1)
    entries = dict(id=data.id,
                   created_at=data.created_at.strftime('%Y/%m/%d'),
                   updated_at=data.updated_at.strftime('%Y/%m/%d'),
                   version=data.version,
                   type=data.type,
                   description=data.description,
                   is_force=data.is_force) if data is not None else {}
    clear_mappers()

    return json.dumps(entries, ensure_ascii=False), 200


@api.route('/versions', methods=['GET'])
def get_all_versions():
    version_mappers()
    repo = VersionRepository(db_session)
    data = repo.get_list()
    entries = [dict(id=version.id,
                    created_at=None if version.created_at is None else version.created_at.strftime('%Y/%m/%d'),
                    updated_at=None if version.updated_at is None else version.updated_at.strftime('%Y/%m/%d'),
                    version=version.version,
                    type=version.type,
                    description=version.description,
                    is_force=version.is_force) for version in data]
    clear_mappers()

    return json.dumps(entries, ensure_ascii=False), 200


@api.route('/new_version', methods=['POST'])
def add_latest_version():
    params = json.loads(request.get_data())
    return json.dumps({'params': params}, ensure_ascii=False), 200
    # version_mappers()
    # repo = VersionRepository(db_session)
    # new_version = Version(
    #     version='5.5.93',
    # )
    # repo.add(new_version)
    # db_session.commit()
    # clear_mappers()
    #
    # return json.dumps({'result': True}, ensure_ascii=False), 200


@api.route('/delete_version')
def delete_version():
    version_mappers()
    repo = VersionRepository(db_session)
    target_version = Version(
        version='7.6',
    )
    repo.delete(target_version)
    db_session.commit()
    clear_mappers()

    return json.dumps({'result': True}, ensure_ascii=False), 200


@api.route('/update_version')
def update_version():
    version_mappers()
    repo = VersionRepository(db_session)
    target_version = Version(version='5.5.60')
    repo.update(target_version, is_force=1, type='코드푸쉬', description='월드비전 인증서 화질 개선 (실패)')
    db_session.commit()
    clear_mappers()

    return json.dumps({'result': True}, ensure_ascii=False), 200
