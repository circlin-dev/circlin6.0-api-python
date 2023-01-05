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
import re

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

    if introduce is None or introduce.introduce_id is None:
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

    if playground is None or playground.id is None:
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
                    value=round(mission_repo.translate_variables(playground.ground_progress_value, mission_id, user_id)) if playground.ground_progress_value is not None else 0,
                    scale=playground.ground_progress_scale,
                ),
                dashboard=dict(
                    center=dict(
                        title=playground.ground_dashboard_center_title,
                        value=0 if mission_repo.translate_variables(playground.ground_dashboard_center_value, mission_id, user_id) is None else round(mission_repo.translate_variables(playground.ground_dashboard_center_value, mission_id, user_id))
                    ),
                    right=dict(
                        title=playground.ground_dashboard_right_title,
                        value=0 if mission_repo.translate_variables(playground.ground_dashboard_right_value, mission_id, user_id) is None else round(mission_repo.translate_variables(playground.ground_dashboard_right_value, mission_id, user_id))
                    )
                ),
                banner=dict(
                    bannerImage=playground.banner_image,
                    type=playground.banner_type,
                    link=playground.banner_link,
                ) if playground.banner_image is not None else None,
                dday=dict(
                    title="종료" if playground.status == "end"
                    else "함께하는 중" if playground.status == "ongoing"
                    else "함께하기 전",
                    value=None if playground.status == "end"
                    else f"D + {playground.d_day}" if playground.status == "ongoing" and playground.d_day > 0
                    else f"D-DAY" if playground.status == "ongoing" and playground.d_day == 0
                    else f"D - {playground.d_day}",
                ),
                cheerPhrases=None if json.loads(playground.cheer_phrases)[0]['tab'] is None
                else current_cheer_phrase([phrase for phrase in sorted(json.loads(playground.cheer_phrases), key=lambda x: x['order']) if phrase['tab'] == 'ground'], playground.status, mission_id, user_id, mission_repo)
            ),
            myRecord=dict(
                progress=dict(
                    symbolImage=playground.record_symbol_image,
                    image=dict(
                        before=playground.daily_image_before_completed,
                        completed=playground.daily_image_after_completed,
                    ),
                    numberToMapImage=playground.total_success_count,
                    title=playground.record_progress_title,
                    value=mission_repo.translate_variables(playground.record_progress_type, mission_id, user_id),
                ),
                dashboard=dict(
                    left=dict(
                        title=playground.record_dashboard_left_title,
                        value=mission_repo.translate_variables(playground.record_dashboard_left_value, mission_id, user_id),
                    ),
                    center=dict(
                        title=playground.record_dashboard_center_title,
                        value=mission_repo.translate_variables(playground.record_dashboard_center_value, mission_id, user_id)
                    ),
                    right=dict(
                        title=playground.record_dashboard_right_title,
                        value=mission_repo.translate_variables(playground.record_dashboard_right_value, mission_id, user_id)

                    ),
                    description=playground.record_dashboard_description
                ),
                cheerPhrases=None if json.loads(playground.cheer_phrases)[0]['tab'] is None
                else current_cheer_phrase([phrase for phrase in sorted(json.loads(playground.cheer_phrases), key=lambda x: x['order']) if phrase['tab'] == 'record'], playground.status, mission_id, user_id, mission_repo)
            ),
            certificate=dict(
                title=playground.certificate_title,
                description=playground.certificate_description if playground.certificate_description is not None else playground.certificate_guidance_for_issue,
                images=playground.certificate_event_images,
                content=dict(
                    left=dict(
                        title=playground.certificate_content_left_title,
                        value=mission_repo.translate_variables(playground.certificate_content_left_value, mission_id, user_id),
                    ),
                    center=dict(
                        title=playground.certificate_content_center_title,
                        value=mission_repo.translate_variables(playground.certificate_content_center_value, mission_id, user_id)
                    ),
                    right=dict(
                        title=playground.certificate_content_right_title,
                        value=mission_repo.translate_variables(playground.certificate_content_right_value, mission_id, user_id)
                    )
                ),
                availble=True if mission_repo.translate_variables(playground.certificate_criterion_for_issue, mission_id, user_id) >= playground.certificate_minimum_value_for_issue else False,
                myCurrentSuccessCount=mission_repo.translate_variables(playground.certificate_criterion_for_issue, mission_id, user_id),
                requiredSuccessCountForIssue=playground.certificate_minimum_value_for_issue,
                sentenceWhenUnavailable=playground.certificate_guidance_for_issue,
            ),
            rankTitle=playground.rank_title,
            # condition=dict(   => 피드 업로드 시 체크할 값
            #     certificateionCriterion=playground.certification_criterion,
            #     amountDeterminingDailySuccess=None if playground.amount_determining_daily_success is None else round(float(playground.amount_determining_daily_success), 2),
            #     inputScale=playground.input_scale,
            #     inputPlaceholder=playground.input_placeholder,
            #     minimumInput=None if playground.minimum_input is None else round(float(playground.minimum_input), 2),
            #     maximumInput=playground.maximum_input,
            # )
        )
        return {'result': True, 'data': entry}


# region mission notice
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
# endregion


# region mission ranking
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
# endregion


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


# region variables for mission
def translate_variables(variable: str, mission_id: int, user_id: int, mission_repo: AbstractMissionRepository):
    return mission_repo.translate_variables(variable, mission_id, user_id)


def extract_variables_from_sentence(sentence: str) -> list:
    pattern = re.compile('{%[a-z|A-Z|0-9|(-_~`!@#$%^&*()+=\\|/)]+}')
    variables_from_sentence = pattern.findall(sentence)
    return variables_from_sentence


def current_cheer_phrase(sentences: list, mission_status: str, mission_id: int, user_id: int, mission_repo: AbstractMissionRepository) -> str:
    """
    [
        {
            "tab": "ground",
            "order": 0,
            "value": 0,
            "sentence": "챌린지 참여자들이 열심히 움직이고 있어요!\n함께 도전해볼까요?",
            "condition": "cert"
        },
        {
            "tab": "ground",
            "order": 1,
            "value": 1,
            "sentence": "오늘 {%today_cert_count}명의 참여자가 도전했어요! \n오늘도 함께 움직여볼까요?",
            "condition": "cert"
        },
    ]
    :param sentences:
        - variable 별로 수행되어야 하는 연산은 다음과 같다.
            - default: 신청기간(챌린지 시작시점 이전)까지 보여줄 화면 멘트
            - cert: 인증 횟수
                - cert == 0: 지금까지 한 번도 인증을 완료한 날이 없음(미션 신청은 했으나, 미시작자)
                - cert == 1: 지금까지 인증 완료한 횟수 1회(최초 1회 인증 완료자)
            - today_cert: 금일 인증 완료 여부
            - complete:
            - today_complete: 당일의 미션 완료 여부
            - end: 챌린지 종료
    :param mission_status:
    :param mission_id:
    :param user_id:
    :param mission_repo:
    :return:
    """
    cheer_phrase = ""
    if mission_status == 'ongoing':
        sentences_filtered_by_status: list = [sentence for sentence in sentences if sentence['condition'] in ["cert", "today_cert", "complete", "today_complete"]]
    elif mission_status == 'end':
        sentences_filtered_by_status: list = [sentence for sentence in sentences if sentence['condition'] in ["default", "end"]]
    else:  # mission_status in ["before_reserve", "reserve", "before_ongoing"]
        sentences_filtered_by_status: list = [sentence for sentence in sentences if sentence['condition'] == "default"]

    for sentence in sentences_filtered_by_status:
        condition: str = sentence['condition']
        if sentence['value'] == get_value_of_cheer_phrase_variable(condition, mission_id, user_id, mission_repo):
            cheer_phrase = sentence['sentence']
        # sentence['current_value'] = get_value_of_cheer_phrase_variable(condition, mission_id, user_id, mission_repo)

        # if sentence['variable'] == 'cert':
        # elif sentence['variable'] == 'today_cert':
        #     result[variable] = get_value_of_cheer_phrase_variable(variable, mission_id, user_id, mission_repo)
        # elif sentence['variable'] == 'complete':  # 미션 전체 성공 여부
        #     result[variable] = get_value_of_cheer_phrase_variable(variable, mission_id, user_id, mission_repo)
        # elif sentence['variable'] == 'today_complete':  # 금일 미션 성공 여부
        #     result[variable] = get_value_of_cheer_phrase_variable(variable, mission_id, user_id, mission_repo)
        # if sentence['variable'] == 'default':  # 미션 시작 전 기본 문구
            # result[variable] = get_value_of_cheer_phrase_variable(variable, mission_id, user_id, mission_repo)
        # elif sentence['variable'] == 'end':
        #     pass
        # else:
        #     pass
            variables_in_a_sentence: list = extract_variables_from_sentence(cheer_phrase)
            # translated_variables: dict = {
            #     variable: translate_variables(variable, mission_id, user_id, mission_repo)
            #     for variable in variables_in_a_sentence
            # }
            for variable in variables_in_a_sentence:
                value = translate_variables(variable, mission_id, user_id, mission_repo)
                cheer_phrase = cheer_phrase.replace(variable, value)
                # cheer_phrase = cheer_phrase.replace(variable, translated_variables[variable])
        else:
            pass
    return cheer_phrase


def get_value_of_cheer_phrase_variable(variable: str, mission_id: int, user_id: int, mission_repo: AbstractMissionRepository):
    return mission_repo.get_value_of_cheer_phrase_variable(variable, mission_id, user_id)
# endregion
