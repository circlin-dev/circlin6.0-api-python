class File:
    def __init__(
            self,
            id: int,
            pathname: str,
            original_name: str,
            mime_type: str,
            size: int,
            width: int,
            height: int,
            original_file_id: int
    ):
        self.id = id
        self.pathname = pathname
        self.original_name = original_name
        self.mime_type = mime_type
        self.size = size
        self.width = width
        self.height = height
        self.original_file_id = original_file_id
