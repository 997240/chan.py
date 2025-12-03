from common.chan_exception import ChanException, ErrCode


class CombineItem:
    def __init__(self, item):
        from bi.bi import Bi
        from kline.kline_unit import KLineUnit
        from seg.seg import Seg
        if isinstance(item, Bi):
            self.time_begin = item.begin_klc.idx
            self.time_end = item.end_klc.idx
            self.high = item._high()
            self.low = item._low()
        elif isinstance(item, KLineUnit):
            self.time_begin = item.time
            self.time_end = item.time
            self.high = item.high
            self.low = item.low
        elif isinstance(item, Seg):
            self.time_begin = item.start_bi.begin_klc.idx
            self.time_end = item.end_bi.end_klc.idx
            self.high = item._high()
            self.low = item._low()
        else:
            raise ChanException(f"{type(item)} is unsupport sub class of CombineItem", ErrCode.COMMON_ERROR)
