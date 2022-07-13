from pypika import Table

# region B
Boards = Table('boards')
BoardCategories = Table('board_categories')
BoardFiles = Table('board_files')
BoardLikes = Table('board_likes')
BoardComments = Table('board_comments')
# endregion

# region F
Files = Table('files')
# endregion

# region P
PushHistories = Table('push_histories')
# endregion


# region N
Notifications = Table('notifications')
# endregion


# region U
Users = Table('users')
# endregion


# region V
Versions = Table('versions')
# endregion
