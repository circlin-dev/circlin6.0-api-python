class Product:
    def __init__(
            self,
            id: int,
            code: str,
            name_ko: str,
            thumbnail_image: str,
            brand_id: int,
            product_category_id: int,
            is_show: bool,
            status: str,
            order: int,
            price: int,
            sale_price: int,
            shipping_fee: int,
            deleted_at: str
    ):
        self.id = id
        self.code = code
        self.name_ko = name_ko
        self.thumbnail_image = thumbnail_image
        self.brand_id = brand_id
        self.product_category_id = product_category_id
        self.is_show = is_show
        self.status = status
        self.order = order
        self.price = price
        self.sale_price = sale_price
        self.shipping_fee = shipping_fee
        self.deleted_at = deleted_at


class ProductCategory:
    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title


class OutsideProduct:
    def __init__(
            self,
            id: int or None,
            product_id: int,
            brand: str or None,
            title: str,
            image: str or None,
            url: str or None,
            price: int
    ):
        self.id = id
        self.product_id = product_id
        self.brand = brand
        self.title = title
        self.image = image
        self.url = url
        self.price = price
