from domain.report import Report

import abc
from sqlalchemy import insert, select


class AbstractReportRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user_id: int, new_report: Report):
        pass

    @abc.abstractmethod
    def get_list(self, user_id: int, page_cursor: int, limit: int):
        pass

    @abc.abstractmethod
    def count_number_of_reporting_of_user(self, user_id: int, page_cursor: int, limit: int):
        pass


class ReportRepository(AbstractReportRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user_id: int, new_report: Report):
        sql = insert(
            Report
        ).values(
            user_id=new_report.user_id,
            target_feed_id=new_report.target_feed_id,
            target_user_id=new_report.target_user_id,
            target_mission_id=new_report.target_mission_id,
            target_feed_comment_id=new_report.target_feed_comment_id,
            target_notice_comment_id=new_report.target_notice_comment_id,
            target_mission_comment_id=new_report.target_mission_comment_id,
            reason=new_report.reason
        )
        return self.session.execute(sql)

    def get_list(self, user_id: int, page_cursor: int, limit: int):
        pass

    def count_number_of_reporting_of_user(self, user_id: int, page_cursor: int, limit: int):
        pass
