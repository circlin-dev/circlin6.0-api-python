from adapter.repository.report import AbstractReportRepository
from domain.report import Report
from helper.function import failed_response


def report(user_id: int, target: str, target_id: int, reason: str, report_repo: AbstractReportRepository) -> dict:
    if target == 'feedId':
        new_report: Report = Report(
            id=None,
            user_id=user_id,
            reason=reason,
            target_feed_id=target_id
        )
        report_repo.add(user_id, new_report)
    elif target == 'userId':
        new_report: Report = Report(
            id=None,
            user_id=user_id,
            reason=reason,
            target_user_id=target_id
        )
        report_repo.add(user_id, new_report)
    elif target == 'missionId':
        new_report: Report = Report(
            id=None,
            user_id=user_id,
            reason=reason,
            target_mission_id=target_id
        )
        report_repo.add(user_id, new_report)
    elif target == 'feedCommentId':
        new_report: Report = Report(
            id=None,
            user_id=user_id,
            reason=reason,
            target_feed_comment_id=target_id
        )
        report_repo.add(user_id, new_report)
    elif target == 'noticeCommentId':
        new_report: Report = Report(
            id=None,
            user_id=user_id,
            reason=reason,
            target_notice_comment_id=target_id
        )
        report_repo.add(user_id, new_report)
    elif target == 'missionCommentId':
        new_report: Report = Report(
            id=None,
            user_id=user_id,
            reason=reason,
            target_mission_comment_id=target_id
        )
        report_repo.add(user_id, new_report)
    else:
        error_message = f"신고 대상이 올바르지 않습니다({target})."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result

    return {'result': True}
