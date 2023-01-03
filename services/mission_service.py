from adapter.repository.feed import AbstractFeedRepository
from adapter.repository.mission import AbstractMissionRepository
from adapter.repository.mission_category import AbstractMissionCategoryRepository
from adapter.repository.mission_comment import AbstractMissionCommentRepository
from adapter.repository.mission_notice import AbstractMissionNoticeRepository
from adapter.repository.mission_rank import AbstractMissionRankRepository
from adapter.repository.mission_stat import AbstractMissionStatRepository
from domain.mission import MissionCategory
from helper.constant import INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT
from helper.function import failed_response

import json


def get_missions_by_category(user_id: int, category_id: int or None, page_cursor: int, limit: int, sort: str, mission_repo: AbstractMissionRepository, mission_stat_repo: AbstractMissionStatRepository):
    missions = mission_repo.get_list_by_category(user_id, category_id, page_cursor, limit, sort)
    entries = [dict(
        id=mission.id,
        title=mission.title,
        category=json.loads(mission.category),
        description=mission.description,
        thumbnail=mission.thumbnail_image,
        createdAt=mission.created_at,
        startedAt=mission.started_at,
        endedAt=mission.ended_at,
        reserveStartedAt=mission.reserve_started_at,
        status=mission.status,
        reserveEndedAt=mission.reserve_ended_at,
        type=mission.mission_type if mission.mission_type is not None else 'normal',
        producer=json.loads(mission.producer),
        bookmarkedUsersProfile=[
            dict(
                id=user.id,
                gender=user.gender,
                profile=user.profile_image,
                nickname=user.nickname,
            )
            for user in mission_repo.get_participants(mission.id, user_id, INITIAL_ASCENDING_PAGE_CURSOR, INITIAL_PAGE_LIMIT)[-2:]
            if user.id not in [json.loads(mission.producer)['id'], 4340, 2]
        ],
        bookmarksCount=mission.bookmarks_count,
        bookmarked=True if mission_stat_repo.get_one_excluding_ended(user_id, mission.id) else False,
        commentsCount=mission.comments_count,
        missionProducts=json.loads(mission.mission_products) if mission.mission_products is not None else [],  # mission.refund_products와 쿼리가 달라 결과값의 데이터 형태가 다르다.
        refundProducts=json.loads(mission.refund_products) if json.loads(mission.refund_products)[0]['id'] is not None else [],
        bookmarkLimit=mission.user_limit,
        hasPlayground=True if mission.has_playground == 1 else False,
        cursor=mission.cursor
    ) for mission in missions] if missions is not None else []

    return entries


def count_number_of_mission_by_category(category_id: int, mission_repo: AbstractMissionRepository):
    total_count = mission_repo.count_number_of_mission_by_category(category_id)
    return total_count


def get_mission_detail_by_id(mission_id: int, user_id: int, mission_repo: AbstractMissionRepository, mission_stat_repo: AbstractMissionStatRepository):
    mission_detail_data = mission_repo.get_detail(mission_id, user_id)

    if mission_detail_data.id is None:
        error_message = f"상세 페이지가 존재하지 않거나, 제작자에 의해 삭제된 미션입니다."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        entry = dict(
            id=mission_detail_data.id,
            title=mission_detail_data.title,
            description=mission_detail_data.description,
            thumbnail=mission_detail_data.thumbnail_image,
            type=mission_detail_data.mission_type if mission_detail_data.mission_type is not None else 'normal',
            bookmarkLimit=mission_detail_data.user_limit,
            myFeedsCount=mission_detail_data.my_feeds_count,
            createdAt=mission_detail_data.created_at,
            startedAt=mission_detail_data.started_at,
            endedAt=mission_detail_data.ended_at,
            images=json.loads(mission_detail_data.images) if json.loads(mission_detail_data.images)[0]['id'] is not None else [],
            producer=json.loads(mission_detail_data.producer),
            status=mission_detail_data.status,
            missionProducts=json.loads(mission_detail_data.mission_products) if mission_detail_data.mission_products is not None else [],  # introduce.refund_products와 쿼리가 달라 결과값의 데이터 형태가 다르다.
            refundProducts=json.loads(mission_detail_data.refund_products) if json.loads(mission_detail_data.refund_products)[0]['id'] is not None else [],
            bookmarked=True if mission_stat_repo.get_one_excluding_ended(user_id, mission_detail_data.id) else False,
        )
        return {'result': True, 'data': entry}


def get_mission_introduce(mission_id: int, user_id: int, mission_repo: AbstractMissionRepository, mission_stat_repo: AbstractMissionStatRepository) -> dict:
    introduce = mission_repo.get_introduce(mission_id)

    if introduce.introduce_id is None:
        error_message = f"소개 페이지가 존재하지 않는 미션입니다."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        entry = dict(
            id=introduce.id,
            title=introduce.title,
            description=introduce.description,
            thumbnail=introduce.thumbnail_image,
            type=introduce.mission_type if introduce.mission_type is not None else 'normal',
            bookmarkLimit=introduce.user_limit,
            bookmarkAvailableWhileOngoing=True if introduce.late_bookmarkable == 1 else False,
            createdAt=introduce.created_at,
            startedAt=introduce.started_at,
            endedAt=introduce.ended_at,
            reserveStartedAt=introduce.reserve_started_at,
            reserveEndedAt=introduce.reserve_ended_at,
            introVideo=introduce.intro_video,
            logo=introduce.logo_image,
            enterCode=json.loads(introduce.enter_code) if json.loads(introduce.enter_code)['code'] is not None else None,
            images=json.loads(introduce.images) if json.loads(introduce.images)[0]['id'] is not None else [],
            producer=json.loads(introduce.producer),
            status=introduce.status,
            missionProducts=json.loads(introduce.mission_products) if introduce.mission_products is not None else [],  # introduce.refund_products와 쿼리가 달라 결과값의 데이터 형태가 다르다.
            refundProducts=json.loads(introduce.refund_products) if json.loads(introduce.refund_products)[0]['id'] is not None else [],
            bookmarked=True if mission_stat_repo.get_one_excluding_ended(user_id, introduce.id) else False,
        )
        return {'result': True, 'data': entry}


def get_mission_playground(mission_id: int, user_id: int, mission_repo: AbstractMissionRepository, mission_stat_repo: AbstractMissionStatRepository) -> dict:
    playground = mission_repo.get_playground(mission_id, user_id)

    if playground.id is None:
        error_message = f"랜선 운동장이 존재하지 않는 미션입니다."
        result = failed_response(error_message)
        result['status_code'] = 400
        return result
    else:
        entry = dict(
            type=playground.mission_type,
            status=playground.status,
            backgroundImage=playground.background_image,
            ground=dict(
                symbolImage=playground.ground_symbol_image,
                progress=dict(
                    image=dict(
                        initial=playground.ground_progress_initial_image,
                        progressed=playground.ground_progress_progressed_image,
                        achieved=playground.ground_progress_achieved_image,
                    ),
                    type=playground.ground_progress_type,
                    goal=playground.ground_progress_goal,
                    title=playground.ground_progress_title,
                    value=playground.ground_progress_value,
                    scale=playground.ground_progress_scale,
                ),
                dashboard=dict(
                    center=dict(
                        title=playground.ground_dashboard_center_title,
                        value=playground.ground_dashboard_center_value
                    ),
                    right=dict(
                        title=playground.ground_dashboard_right_title,
                        value=playground.ground_dashboard_right_value
                    )
                ),
                banner=dict(
                    bannerImage=playground.banner_image,
                    type=playground.banner_type,
                    link=playground.banner_link,
                ),
                dday=dict(
                    title='',
                    value='',
                ),
                cheeringPhrase='',
            ),
            myRecord=dict(
                progress=dict(
                    symbolImage=playground.record_symbol_image,
                    image=dict(
                        before=playground.daily_image_before_completed,
                        completed=playground.daily_image_after_completed,
                    ),
                    totalSuccessCount=playground.total_success_count,
                    type=playground.record_progress_type,
                ),
                dashboard=dict(
                    left=dict(
                        title=playground.record_dashboard_left_title,
                        value=playground.record_dashboard_left_value
                    ),
                    center=dict(
                        title=playground.record_dashboard_center_title,
                        value=playground.record_dashboard_center_value
                    ),
                    right=dict(
                        title=playground.record_dashboard_right_title,
                        value=playground.record_dashboard_right_value
                    ),
                    description=playground.record_dashboard_description
                ),
                cheeringPhrase='',
            ),
            certificate=dict(
                title=playground.certificate_title,
                description=playground.certificate_description,
                images=playground.certificate_event_images,
                content=dict(
                    left=dict(
                        title=playground.certificate_content_left_title,
                        value=playground.certificate_content_left_value
                    ),
                    center=dict(
                        title=playground.certificate_content_center_title,
                        value=playground.certificate_content_center_value
                    ),
                    right=dict(
                        title=playground.certificate_content_right_title,
                        value=playground.certificate_content_right_value
                    )
                ),
                criterionForIssue=playground.certificate_criterion_for_issue,
                minimumValueForIssue=playground.certificate_minimum_value_for_issue,
                disabled=playground.certificate_guidance_for_issue,
            ),
            rank=dict(
                rankTitle=playground.rank_title,
                rankValue=playground.rank_value,
                rankScale=playground.rank_scale,
            ),
            condition=dict(
                certificateionCriterion=playground.certification_criterion,
                amountDeterminingDailySuccess=None if playground.amount_determining_daily_success is None else round(float(playground.amount_determining_daily_success), 2),
                inputScale=playground.input_scale,
                inputPlaceholder=playground.input_placeholder,
                minimumInput=None if playground.minimum_input is None else round(float(playground.minimum_input), 2),
                maximumInput=playground.maximum_input,
            )
        )
        return {'result': True, 'data': entry}


def get_notices(mission_id: int, page_cursor: int, limit: int, mission_notice_repo: AbstractMissionNoticeRepository) -> list:
    notices = mission_notice_repo.get_list(mission_id, page_cursor, limit)
    entries = [dict(
        id=notice.id,
        createdAt=notice.created_at,
        title=notice.title,
        body=notice.body,
        images=json.loads(notice.images) if notice.images is not None else [],
        cursor=notice.cursor,
    ) for notice in notices] if notices is not None else []
    return entries


def get_notice_count_of_the_mission(mission_id: int, mission_notice_repo: AbstractMissionNoticeRepository) -> int:
    total_count = mission_notice_repo.count_number_of_notice(mission_id)
    return total_count


def get_rank_list(mission_id: int, user_id: int, page_cursor: int, limit: int, mission_rank_repo: AbstractMissionRankRepository):
    result: dict = {"my_rank": None, "rank": []}
    latest_mission_rank_id: int = mission_rank_repo.get_latest_rank_id(mission_id)
    if latest_mission_rank_id is None:
        return result
    rank_scale = mission_rank_repo.get_rank_scale(mission_id).rank_scale

    ranks = mission_rank_repo.get_list(latest_mission_rank_id, page_cursor, limit)
    entries: list = [dict(
        user=dict(
            id=rank.user_id,
            nickname=rank.nickname,
            gender=rank.gender,
            profile=rank.profile_image,
            followers=rank.followers
        ),
        rank=rank.rank,
        feedsCount=f"{str(rank.feeds_count)}회",
        record=f"{str(rank.summation)} {rank_scale}" if rank.summation > 0 else f"{str(rank.feeds_count)} 회",
        cursor=rank.cursor,
    ) for rank in ranks]

    my_rank = mission_rank_repo.get_my_rank(latest_mission_rank_id, user_id)
    my_rank: dict = dict(
        user=dict(
            id=my_rank.user_id,
            nickname=my_rank.nickname,
            gender=my_rank.gender,
            profile=my_rank.profile_image
        ),
        rank=my_rank.rank,
        feedsCount=f"{str(my_rank.feeds_count)}회",
        record=f"{str(my_rank.summation)} {rank_scale}" if my_rank.summation > 0 else f"{str(my_rank.feeds_count)} 회",
    ) if my_rank is not None else None
    result["rank"] = entries
    result["my_rank"] = my_rank
    return result


def get_rank_count_of_the_mission(mission_id: int, mission_rank_repo: AbstractMissionRankRepository):
    latest_mission_rank_id: int = mission_rank_repo.get_latest_rank_id(mission_id)
    total_count = mission_rank_repo.count_number_of_rank(latest_mission_rank_id)
    return total_count


# region mission participants
def get_mission_participant_list(mission_id: int, user_id: int, page_cursor: int, limit: int, mission_repo: AbstractMissionRepository):
    participants: list = mission_repo.get_participants(mission_id, user_id, page_cursor, limit)
    entries: list = [dict(
        id=participant.id,
        nickname=participant.nickname,
        gender=participant.gender,
        profile=participant.profile_image,
        followed=participant.followed,
        followers=participant.followers,
        cursor=participant.cursor
    ) for participant in participants] if participants is not None else []
    return entries


def count_number_of_mission_participant(mission_id: int, mission_repo: AbstractMissionRepository):
    total_count: int = mission_repo.count_number_of_participants(mission_id)
    return total_count
# endregion


# region category
def get_mission_categories(mission_category_repo: AbstractMissionCategoryRepository, favorite_mission_categories: list):
    category_list = mission_category_repo.get_list()

    entries = [dict(id=category.id,
                    key=str(category.id),
                    missionCategoryId=category.mission_category_id,
                    title=category.title,
                    emoji=category.emoji if category.emoji is not None else '',
                    description=category.description if category.description is not None else '',
                    isFavorite=True if category.id in favorite_mission_categories else False
                    ) for category in category_list]
    return entries
# endregion


# region comments
def get_comment_count_of_the_mission(mission_id, mission_comment_repo: AbstractMissionCommentRepository) -> int:
    return mission_comment_repo.count_number_of_comment(mission_id)


def get_comments(mission_id: int, page_cursor: int, limit: int, user_id: int, mission_comment_repo: AbstractMissionCommentRepository) -> list:
    comments: list = mission_comment_repo.get_list(mission_id, page_cursor, limit, user_id)
    entries: list = [
        dict(
            id=comment.id,
            createdAt=comment.created_at,
            group=comment.group,
            depth=comment.depth,
            comment=comment.comment,
            userId=comment.user_id,
            isBlocked=True if comment.is_blocked == 1 else False,
            nickname=comment.nickname,
            profile=comment.profile_image,
            gender=comment.gender,
            cursor=comment.cursor
        ) for comment in comments
    ]
    return entries
# endregion


# region feeds
def get_feeds_by_mission(mission_id: int, page_cursor: int, limit: int, user_id: int, feed_repo: AbstractFeedRepository, mission_stat_repo: AbstractMissionStatRepository) -> list:
    feeds = feed_repo.get_feeds_by_mission(mission_id, user_id, page_cursor, limit)
    entries: list = [dict(
        id=feed.id,
        createdAt=feed.created_at,
        body=feed.body,
        distance=None if feed.distance is None
        else f'{str(round(feed.distance, 2))} L' if feed.laptime is None and feed.distance_origin is None and feed.laptime_origin is None
        else f'{round(feed.distance, 2)} km',
        images=[] if feed.images is None else json.loads(feed.images),
        isShow=True if feed.is_hidden == 0 else False,
        user=dict(
            id=feed.user_id,
            nickname=feed.nickname,
            profile=feed.profile_image,
            followed=True if feed.followed == 1 else False,
            area=feed.area,
            followers=feed.followers,
            gender=feed.gender,
            isBlocked=True if feed.is_blocked == 1 else False,
            isChatBlocked=True if feed.is_chat_blocked == 1 else False
        ) if feed.user_id is not None else None,
        commentsCount=feed.comments_count,
        missions=[dict(
            id=mission['id'],
            title=mission['title'] if mission['emoji'] is None else f"{mission['emoji']}{mission['title']}",
            isEvent=True if mission['is_event'] == 1 else False,
            isOldEvent=True if mission['is_old_event'] == 1 else False,
            isGround=True if mission['is_ground'] == 1 else False,
            eventType=mission['event_type'],
            thumbnail=mission['thumbnail'],
            bookmarked=True if mission_stat_repo.get_one_excluding_ended(user_id, mission['id']) else False
        ) for mission in json.loads(feed.mission)] if json.loads(feed.mission)[0]['id'] is not None else [],
        checkedUsers=[dict(
            id=user['id'],
            nickname=user['nickname'],
            profile=user['profile_image']
        ) for user in json.loads(feed.checked_users)] if feed.checked_users is not None else [],
        checked=True if feed.checked == 1 else False,
        product=json.loads(feed.product) if json.loads(feed.product)['id'] is not None else None,
        food=json.loads(feed.food) if json.loads(feed.food)['id'] is not None else None,
        cursor=feed.cursor,
    ) for feed in feeds]
    return entries


def get_feed_count_of_the_mission(mission_id: int, feed_repo: AbstractFeedRepository) -> int:
    count = feed_repo.count_number_of_feed_of_mission(mission_id)
    return count
# endregion
