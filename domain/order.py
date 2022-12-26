class Order:
    def __init__(
            self,
            user_id: int,
            total_price: int,
            use_point: int,
            order_no: int,
            imp_id: str or None,
            merchant_id: str or None,
            deleted_at: str or None
    ):
        self.user_id = user_id
        self.total_price = total_price
        self.use_point = use_point
        self.order_no = order_no
        self.imp_id = imp_id
        self.merchant_id = merchant_id
        self.deleted_at = deleted_at


class OrderProduct:
    pass

