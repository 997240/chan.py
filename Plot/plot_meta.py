from typing import List

from bi.bi import Bi
from buy_sell_point.bs_point import BSPoint
from common.enums import FX_TYPE
from kline.kline import KLine
from kline.kline_list import KLineList
from seg.eigen import Eigen
from seg.eigen_fx import EigenFX
from seg.seg import Seg
from zs.zs import ZS


class KlcMeta:
    def __init__(self, klc: KLine):
        self.high = klc.high
        self.low = klc.low
        self.begin_idx = klc.lst[0].idx
        self.end_idx = klc.lst[-1].idx
        self.type = klc.fx if klc.fx != FX_TYPE.UNKNOWN else klc.dir

        self.klu_list = list(klc.lst)


class Bi_meta:
    def __init__(self, bi: Bi):
        self.idx = bi.idx
        self.dir = bi.dir
        self.type = bi.type
        self.begin_x = bi.get_begin_klu().idx
        self.end_x = bi.get_end_klu().idx
        self.begin_y = bi.get_begin_val()
        self.end_y = bi.get_end_val()
        self.is_sure = bi.is_sure


class Seg_meta:
    def __init__(self, seg: Seg):
        if isinstance(seg.start_bi, Bi):
            self.begin_x = seg.start_bi.get_begin_klu().idx
            self.begin_y = seg.start_bi.get_begin_val()
            self.end_x = seg.end_bi.get_end_klu().idx
            self.end_y = seg.end_bi.get_end_val()
        else:
            assert isinstance(seg.start_bi, Seg)
            self.begin_x = seg.start_bi.start_bi.get_begin_klu().idx
            self.begin_y = seg.start_bi.start_bi.get_begin_val()
            self.end_x = seg.end_bi.end_bi.get_end_klu().idx
            self.end_y = seg.end_bi.end_bi.get_end_val()
        self.dir = seg.dir
        self.is_sure = seg.is_sure
        self.idx = seg.idx

        self.tl = {}
        if seg.support_trend_line and seg.support_trend_line.line:
            self.tl["support"] = seg.support_trend_line
        if seg.resistance_trend_line and seg.resistance_trend_line.line:
            self.tl["resistance"] = seg.resistance_trend_line

    def format_tl(self, tl):
        assert tl.line
        tl_slope = tl.line.slope + 1e-7
        tl_x = tl.line.p.x
        tl_y = tl.line.p.y
        tl_y0 = self.begin_y
        tl_y1 = self.end_y
        tl_x0 = (tl_y0-tl_y)/tl_slope + tl_x
        tl_x1 = (tl_y1-tl_y)/tl_slope + tl_x
        return tl_x0, tl_y0, tl_x1, tl_y1


class EigenMeta:
    def __init__(self, eigen: Eigen):
        self.begin_x = eigen.lst[0].get_begin_klu().idx
        self.end_x = eigen.lst[-1].get_end_klu().idx
        self.begin_y = eigen.low
        self.end_y = eigen.high
        self.w = self.end_x - self.begin_x
        self.h = self.end_y - self.begin_y


class EigenFXMeta:
    def __init__(self, eigenFX: EigenFX):
        self.ele = [EigenMeta(ele) for ele in eigenFX.ele if ele is not None]
        assert len(self.ele) == 3
        assert eigenFX.ele[1] is not None
        self.gap = eigenFX.ele[1].gap
        self.fx = eigenFX.ele[1].fx


class ZS_meta:
    def __init__(self, zs: ZS):
        self.low = zs.low
        self.high = zs.high
        self.begin = zs.begin.idx
        self.end = zs.end.idx
        self.w = self.end - self.begin
        self.h = self.high - self.low
        self.is_sure = zs.is_sure
        self.sub_zs_lst = [ZS_meta(t) for t in zs.sub_zs_lst]
        self.is_onebi_zs = zs.is_one_bi_zs()


class BSPoint_meta:
    def __init__(self, bsp: BSPoint, is_seg):
        self.is_buy = bsp.is_buy
        self.type = bsp.type2str()
        self.is_seg = is_seg

        self.x = bsp.klu.idx
        self.y = bsp.klu.low if self.is_buy else bsp.klu.high

    def desc(self):
        is_seg_flag = "※" if self.is_seg else ""
        return f'{is_seg_flag}b{self.type}' if self.is_buy else f'{is_seg_flag}s{self.type}'


class ChanPlotMeta:
    def __init__(self, kl_list: KLineList):
        self.data = kl_list

        self.klc_list: List[KlcMeta] = [KlcMeta(klc) for klc in kl_list.lst]
        self.datetick = [klu.time.to_str() for klu in self.klu_iter()]
        self.klu_len = sum(len(klc.klu_list) for klc in self.klc_list)

        self.bi_list = [Bi_meta(bi) for bi in kl_list.bi_list]

        self.seg_list: List[Seg_meta] = []
        self.eigenfx_lst: List[EigenFXMeta] = []
        for seg in kl_list.seg_list:
            self.seg_list.append(Seg_meta(seg))
            if seg.eigen_fx:
                self.eigenfx_lst.append(EigenFXMeta(seg.eigen_fx))

        self.seg_eigenfx_lst: List[EigenFXMeta] = []
        self.segseg_list: List[Seg_meta] = []
        for segseg in kl_list.segseg_list:
            self.segseg_list.append(Seg_meta(segseg))
            if segseg.eigen_fx:
                self.seg_eigenfx_lst.append(EigenFXMeta(segseg.eigen_fx))

        self.zs_lst: List[ZS_meta] = [ZS_meta(zs) for zs in kl_list.zs_list]
        self.segzs_lst: List[ZS_meta] = [ZS_meta(segzs) for segzs in kl_list.segzs_list]

        self.bs_point_lst: List[BSPoint_meta] = [BSPoint_meta(bs_point, is_seg=False) for bs_point in kl_list.bs_point_lst.bsp_iter()]
        self.seg_bsp_lst: List[BSPoint_meta] = [BSPoint_meta(seg_bsp, is_seg=True) for seg_bsp in kl_list.seg_bs_point_lst.bsp_iter()]

    def klu_iter(self):
        for klc in self.klc_list:
            yield from klc.klu_list

    def sub_last_kseg_start_idx(self, seg_cnt):
        if seg_cnt is None or len(self.data.seg_list) <= seg_cnt:
            return 0
        else:
            return self.data.seg_list[-seg_cnt].get_begin_klu().sub_kl_list[0].idx

    def sub_last_kbi_start_idx(self, bi_cnt):
        if bi_cnt is None or len(self.data.bi_list) <= bi_cnt:
            return 0
        else:
            return self.data.bi_list[-bi_cnt].begin_klc.lst[0].sub_kl_list[0].idx

    def sub_range_start_idx(self, x_range):
        for klc in self.data[::-1]:
            for klu in klc[::-1]:
                x_range -= 1
                if x_range == 0:
                    return klu.sub_kl_list[0].idx
        return 0
