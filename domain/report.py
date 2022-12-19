class Report:
    def __init__(self):
        pass

    # Column("id", BIGINT(unsigned=True), primary_key=True),
    # Column("created_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    # Column("updated_at", TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
    # Column("user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True, comment='신고자 user id'),
    # Column("target_feed_id", BIGINT(unsigned=True), ForeignKey('feeds.id'), index=True, comment='피드 신고 시 feed id값'),
    # Column("target_user_id", BIGINT(unsigned=True), ForeignKey('users.id'), index=True, comment='유저 신고 시 user id값'),
    # Column("target_mission_id", BIGINT(unsigned=True), ForeignKey('missions.id'), index=True, comment='미션 신고 시 mission id값'),
    # Column("target_feed_comment_id", BIGINT(unsigned=True), ForeignKey('feed_comments.id'), index=True, comment='피드 댓글 신고 시 feed_comment id값'),
    # Column("target_notice_comment_id", BIGINT(unsigned=True), ForeignKey('notice_comments.id'), index=True, comment='공지사항 댓글 신고 시 notice_comment id값'),
    # Column("target_mission_comment_id", BIGINT(unsigned=True), ForeignKey('mission_comments.id'), index=True, comment='미션 댓글 신고 시 mission_comment id값'),
    # Column("reason", TEXT(collation='utf8mb4_unicode_ci')),