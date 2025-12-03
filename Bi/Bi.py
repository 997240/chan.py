from typing import List, Optional

from common.cache import make_cache
from common.enums import BI_DIR, BI_TYPE, DATA_FIELD, FX_TYPE, MACD_ALGO
from common.chan_exception import ChanException, ErrCode
from kline.kline import KLine
from kline.kline_unit import KLineUnit


class Bi:
    def __init__(self, begin_klc: KLine, end_klc: KLine, idx: int, is_sure: bool):
        # self.__begin_klc = begin_klc
        # self.__end_klc = end_klc
        self.__dir = None
        self.__idx = idx
        self.__type = BI_TYPE.STRICT

        self.set(begin_klc, end_klc)

        self.__is_sure = is_sure
        self.__sure_end: List[KLine] = []

        self.__seg_idx: Optional[int] = None

        from seg.seg import Seg
        self.parent_seg: Optional[Seg['Bi']] = None  # 在哪个线段里面

        from buy_sell_point.bs_point import BSPoint
        self.bsp: Optional[BSPoint] = None  # 尾部是不是买卖点

        self.next: Optional[Bi] = None
        self.pre: Optional[Bi] = None

    def clean_cache(self):
        self._memoize_cache = {}

    @property
    def begin_klc(self): return self.__begin_klc

    @property
    def end_klc(self): return self.__end_klc

    @property
    def dir(self): return self.__dir

    @property
    def idx(self): return self.__idx

    @property
    def type(self): return self.__type

    @property
    def is_sure(self): return self.__is_sure

    @property
    def sure_end(self): return self.__sure_end

    @property
    def klc_lst(self):
        klc = self.begin_klc
        while True:
            yield klc
            klc = klc.next
            if not klc or klc.idx > self.end_klc.idx:
                break

    @property
    def klc_lst_re(self):
        klc = self.end_klc
        while True:
            yield klc
            klc = klc.pre
            if not klc or klc.idx < self.begin_klc.idx:
                break

    @property
    def seg_idx(self): return self.__seg_idx

    def set_seg_idx(self, idx):
        self.__seg_idx = idx

    def __str__(self):
        return f"{self.dir}|{self.begin_klc} ~ {self.end_klc}"

    def check(self):
        try:
            if self.is_down():
                assert self.begin_klc.high > self.end_klc.low
            else:
                assert self.begin_klc.low < self.end_klc.high
        except Exception as e:
            raise ChanException(f"{self.idx}:{self.begin_klc[0].time}~{self.end_klc[-1].time}笔的方向和收尾位置不一致!", ErrCode.BI_ERR) from e

    def set(self, begin_klc: KLine, end_klc: KLine):
        self.__begin_klc: KLine = begin_klc
        self.__end_klc: KLine = end_klc
        if begin_klc.fx == FX_TYPE.BOTTOM:
            self.__dir = BI_DIR.UP
        elif begin_klc.fx == FX_TYPE.TOP:
            self.__dir = BI_DIR.DOWN
        else:
            raise ChanException("ERROR DIRECTION when creating bi", ErrCode.BI_ERR)
        self.check()
        self.clean_cache()

    @make_cache
    def get_begin_val(self):
        return self.begin_klc.low if self.is_up() else self.begin_klc.high

    @make_cache
    def get_end_val(self):
        return self.end_klc.high if self.is_up() else self.end_klc.low

    @make_cache
    def get_begin_klu(self) -> KLineUnit:
        if self.is_up():
            return self.begin_klc.get_peak_klu(is_high=False)
        else:
            return self.begin_klc.get_peak_klu(is_high=True)

    @make_cache
    def get_end_klu(self) -> KLineUnit:
        if self.is_up():
            return self.end_klc.get_peak_klu(is_high=True)
        else:
            return self.end_klc.get_peak_klu(is_high=False)

    @make_cache
    def amp(self):
        return abs(self.get_end_val() - self.get_begin_val())

    @make_cache
    def get_klu_cnt(self):
        return self.get_end_klu().idx - self.get_begin_klu().idx + 1

    @make_cache
    def get_klc_cnt(self):
        assert self.end_klc.idx == self.get_end_klu().klc.idx
        assert self.begin_klc.idx == self.get_begin_klu().klc.idx
        return self.end_klc.idx - self.begin_klc.idx + 1

    @make_cache
    def _high(self):
        return self.end_klc.high if self.is_up() else self.begin_klc.high

    @make_cache
    def _low(self):
        return self.begin_klc.low if self.is_up() else self.end_klc.low

    @make_cache
    def _mid(self):
        return (self._high() + self._low()) / 2  # 笔的中位价

    @make_cache
    def is_down(self):
        return self.dir == BI_DIR.DOWN

    @make_cache
    def is_up(self):
        return self.dir == BI_DIR.UP

    def update_virtual_end(self, new_klc: KLine):
        self.append_sure_end(self.end_klc)
        self.update_new_end(new_klc)
        self.__is_sure = False

    def restore_from_virtual_end(self, sure_end: KLine):
        self.__is_sure = True
        self.update_new_end(new_klc=sure_end)
        self.__sure_end = []

    def append_sure_end(self, klc: KLine):
        self.__sure_end.append(klc)

    def update_new_end(self, new_klc: KLine):
        self.__end_klc = new_klc
        self.check()
        self.clean_cache()

    def cal_macd_metric(self, macd_algo, is_reverse):
        if macd_algo == MACD_ALGO.AREA:
            return self.cal_macd_half(is_reverse)
        elif macd_algo == MACD_ALGO.PEAK:
            return self.cal_macd_peak()
        elif macd_algo == MACD_ALGO.FULL_AREA:
            return self.cal_macd_area()
        elif macd_algo == MACD_ALGO.DIFF:
            return self.cal_macd_diff()
        elif macd_algo == MACD_ALGO.SLOPE:
            return self.cal_macd_slope()
        elif macd_algo == MACD_ALGO.AMP:
            return self.cal_macd_amp()
        elif macd_algo == MACD_ALGO.AMOUNT:
            return self.cal_macd_trade_metric(DATA_FIELD.FIELD_TURNOVER, cal_avg=False)
        elif macd_algo == MACD_ALGO.VOLUME:
            return self.cal_macd_trade_metric(DATA_FIELD.FIELD_VOLUME, cal_avg=False)
        elif macd_algo == MACD_ALGO.VOLUME_AVG:
            return self.cal_macd_trade_metric(DATA_FIELD.FIELD_VOLUME, cal_avg=True)
        elif macd_algo == MACD_ALGO.AMOUNT_AVG:
            return self.cal_macd_trade_metric(DATA_FIELD.FIELD_TURNOVER, cal_avg=True)
        elif macd_algo == MACD_ALGO.TURNRATE_AVG:
            return self.cal_macd_trade_metric(DATA_FIELD.FIELD_TURNRATE, cal_avg=True)
        elif macd_algo == MACD_ALGO.RSI:
            return self.cal_rsi()
        else:
            raise ChanException(f"unsupport macd_algo={macd_algo}, should be one of area/full_area/peak/diff/slope/amp", ErrCode.PARA_ERROR)

    @make_cache
    def cal_rsi(self):
        rsi_lst: List[float] = []
        for klc in self.klc_lst:
            rsi_lst.extend(klu.rsi for klu in klc.lst)
        return 10000.0/(min(rsi_lst)+1e-7) if self.is_down() else max(rsi_lst)

    @make_cache
    def cal_macd_area(self):
        _s = 1e-7
        begin_klu = self.get_begin_klu()
        end_klu = self.get_end_klu()
        for klc in self.klc_lst:
            for klu in klc.lst:
                if klu.idx < begin_klu.idx or klu.idx > end_klu.idx:
                    continue
                if (self.is_down() and klu.macd.macd < 0) or (self.is_up() and klu.macd.macd > 0):
                    _s += abs(klu.macd.macd)
        return _s

    @make_cache
    def cal_macd_peak(self):
        peak = 1e-7
        for klc in self.klc_lst:
            for klu in klc.lst:
                if abs(klu.macd.macd) > peak:
                    if self.is_down() and klu.macd.macd < 0:
                        peak = abs(klu.macd.macd)
                    elif self.is_up() and klu.macd.macd > 0:
                        peak = abs(klu.macd.macd)
        return peak

    def cal_macd_half(self, is_reverse):
        if is_reverse:
            return self.cal_macd_half_reverse()
        else:
            return self.cal_macd_half_obverse()

    @make_cache
    def cal_macd_half_obverse(self):
        _s = 1e-7
        begin_klu = self.get_begin_klu()
        peak_macd = begin_klu.macd.macd
        for klc in self.klc_lst:
            for klu in klc.lst:
                if klu.idx < begin_klu.idx:
                    continue
                if klu.macd.macd*peak_macd > 0:
                    _s += abs(klu.macd.macd)
                else:
                    break
            else:  # 没有被break，继续找写一个KLC
                continue
            break
        return _s

    @make_cache
    def cal_macd_half_reverse(self):
        _s = 1e-7
        begin_klu = self.get_end_klu()
        peak_macd = begin_klu.macd.macd
        for klc in self.klc_lst_re:
            for klu in klc[::-1]:
                if klu.idx > begin_klu.idx:
                    continue
                if klu.macd.macd*peak_macd > 0:
                    _s += abs(klu.macd.macd)
                else:
                    break
            else:  # 没有被break，继续找写一个KLC
                continue
            break
        return _s

    @make_cache
    def cal_macd_diff(self):
        """
        macd红绿柱最大值最小值之差
        """
        _max, _min = float("-inf"), float("inf")
        for klc in self.klc_lst:
            for klu in klc.lst:
                macd = klu.macd.macd
                if macd > _max:
                    _max = macd
                if macd < _min:
                    _min = macd
        return _max-_min

    @make_cache
    def cal_macd_slope(self):
        begin_klu = self.get_begin_klu()
        end_klu = self.get_end_klu()
        if self.is_up():
            return (end_klu.high - begin_klu.low)/end_klu.high/(end_klu.idx - begin_klu.idx + 1)
        else:
            return (begin_klu.high - end_klu.low)/begin_klu.high/(end_klu.idx - begin_klu.idx + 1)

    @make_cache
    def cal_macd_amp(self):
        begin_klu = self.get_begin_klu()
        end_klu = self.get_end_klu()
        if self.is_down():
            return (begin_klu.high-end_klu.low)/begin_klu.high
        else:
            return (end_klu.high-begin_klu.low)/begin_klu.low

    def cal_macd_trade_metric(self, metric: str, cal_avg=False) -> float:
        _s = 0
        for klc in self.klc_lst:
            for klu in klc.lst:
                metric_res = klu.trade_info.metric[metric]
                if metric_res is None:
                    return 0.0
                _s += metric_res
        return _s / self.get_klu_cnt() if cal_avg else _s

    # def set_klc_lst(self, lst):
    #     self.__klc_lst = lst
