import abc
from typing import Iterable

from kline.kline_unit import KLineUnit


class CommonStockApi:
    def __init__(self, code, k_type, begin_date, end_date, autype):
        self.code = code
        self.name = None
        self.is_stock = None
        self.k_type = k_type
        self.begin_date = begin_date
        self.end_date = end_date
        self.autype = autype
        self.set_basic_info()

    @abc.abstractmethod
    def get_kl_data(self) -> Iterable[KLineUnit]:
        pass

    @abc.abstractmethod
    def set_basic_info(self):
        pass

    @classmethod
    @abc.abstractmethod
    def do_init(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def do_close(cls):
        pass
