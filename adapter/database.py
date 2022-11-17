from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.pool import NullPool

# db configuration
user = 'circlin'
password = 'circlinDev2019!'
host = 'circlin-app.cse1vltsv4xu.ap-northeast-2.rds.amazonaws.com'
port = 3306
scheme = 'circlin'
charset = 'utf8mb4'  # for emoji recognition

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{scheme}?charset={charset}',
                       encoding='utf-8',
                       # max_overflow=0,
                       convert_unicode=True,
                       poolclass=NullPool)

# DATABASE session은 sqlalchemy query 스타일에 상관없이 둘 다 되니, 각 세션의 작동 원리 차이를 알아보고 결정하자.
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
db_session = Session(engine, future=True)
