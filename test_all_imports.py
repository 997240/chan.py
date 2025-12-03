"""
全面测试所有模块的导入是否正常
"""
import sys

def test_import(module_name, import_statement):
    """测试单个模块导入"""
    try:
        exec(import_statement)
        print(f"✅ {module_name}")
        return True
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("开始全面测试所有模块导入...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    tests = [
        # 核心模块
        ("chan", "from chan import Chan"),
        ("chan_config", "from chan_config import ChanConfig"),
        
        # common 模块
        ("common.enums", "from common.enums import AUTYPE, DATA_SRC, KL_TYPE, BI_DIR, FX_TYPE, BSP_TYPE"),
        ("common.ctime", "from common.ctime import CTime"),
        ("common.chan_exception", "from common.chan_exception import ChanException"),
        
        # bi 模块
        ("bi.bi", "from bi.bi import Bi"),
        ("bi.bi_config", "from bi.bi_config import BiConfig"),
        ("bi.bi_list", "from bi.bi_list import BiList"),
        
        # seg 模块
        ("seg.seg", "from seg.seg import Seg"),
        ("seg.seg_config", "from seg.seg_config import SegConfig"),
        ("seg.seg_list_comm", "from seg.seg_list_comm import SegListComm"),
        ("seg.seg_list_chan", "from seg.seg_list_chan import SegListChan"),
        ("seg.seg_list_def", "from seg.seg_list_def import SegListDef"),
        ("seg.seg_list_dyh", "from seg.seg_list_dyh import SegListDYH"),
        ("seg.eigen", "from seg.eigen import Eigen"),
        ("seg.eigen_fx", "from seg.eigen_fx import EigenFX"),
        
        # zs 模块
        ("zs.zs", "from zs.zs import ZS"),
        ("zs.zs_config", "from zs.zs_config import ZSConfig"),
        ("zs.zs_list", "from zs.zs_list import ZSList"),
        
        # kline 模块
        ("kline.kline", "from kline.kline import KLine"),
        ("kline.kline_unit", "from kline.kline_unit import KLineUnit"),
        ("kline.kline_list", "from kline.kline_list import KLineList"),
        ("kline.trade_info", "from kline.trade_info import TradeInfo"),
        
        # buy_sell_point 模块
        ("buy_sell_point.bs_point", "from buy_sell_point.bs_point import BSPoint"),
        ("buy_sell_point.bs_point_config", "from buy_sell_point.bs_point_config import BSPointConfig, PointConfig"),
        ("buy_sell_point.bs_point_list", "from buy_sell_point.bs_point_list import BSPointList"),
        
        # combiner 模块
        ("combiner.combine_item", "from combiner.combine_item import CombineItem"),
        ("combiner.kline_combiner", "from combiner.kline_combiner import KLineCombiner"),
        
        # math_util 模块
        ("math_util.macd", "from math_util.macd import MACD, MACDItem"),
        ("math_util.demark", "from math_util.demark import DemarkEngine, DemarkIndex"),
        ("math_util.trend_line", "from math_util.trend_line import TrendLine"),
        ("math_util.trend_model", "from math_util.trend_model import TrendModel"),
        
        # chan_model 模块
        ("chan_model.features", "from chan_model.features import Features"),
        
        # data_api 模块
        ("data_api.common_stock_api", "from data_api.common_stock_api import CommonStockApi"),
        ("data_api.bao_stock_api", "from data_api.bao_stock_api import BaoStock"),
        ("data_api.csv_api", "from data_api.csv_api import CSV_API"),
        # 以下是可选依赖，需要安装第三方库
        # ("data_api.ccxt", "from data_api.ccxt import CCXT"),  # 需要 pip install ccxt
        # ("data_api.futu_api", "from data_api.futu_api import FutuApi"),  # 需要 pip install futu-api
        
        # plot 模块
        ("plot.plot_meta", "from plot.plot_meta import ChanPlotMeta, KlcMeta, Bi_meta, Seg_meta, ZS_meta"),
        ("plot.plot_driver", "from plot.plot_driver import PlotDriver"),
        ("plot.animate_plot_driver_matplotlib", "from plot.animate_plot_driver_matplotlib import AnimateDriver"),
    ]
    
    print("\n📦 测试模块导入:\n")
    
    for module_name, import_stmt in tests:
        if test_import(module_name, import_stmt):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: ✅ 成功 {success_count} | ❌ 失败 {fail_count}")
    print("=" * 60)
    
    # 如果所有导入成功，进行功能测试
    if fail_count == 0:
        print("\n🔬 开始功能测试...\n")
        
        try:
            from chan import Chan
            from chan_config import ChanConfig
            from common.enums import AUTYPE, DATA_SRC, KL_TYPE
            
            print("创建 Chan 实例并分析股票数据...")
            chan = Chan(
                code="sz.000001",
                begin_time="2024-01-01",
                end_time="2024-03-01",
                data_src=DATA_SRC.BAO_STOCK,
                lv_list=[KL_TYPE.K_DAY],
                config=ChanConfig({"trigger_step": False}),
                autype=AUTYPE.QFQ,
            )
            
            print(f"  ✅ K线数量: {len(chan[0])}")
            print(f"  ✅ 笔数量: {len(chan[0].bi_list)}")
            print(f"  ✅ 线段数量: {len(chan[0].seg_list)}")
            print(f"  ✅ 中枢数量: {len(chan[0].zs_list)}")
            print(f"  ✅ 买卖点数量: {len(chan[0].bs_point_lst)}")
            
            print("\n" + "=" * 60)
            print("🎉 所有测试通过！重构成功！")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 功能测试失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠️ 存在导入失败，请检查错误信息")
        print("   注意：ccxt/futu 等可选依赖失败可以忽略")
        sys.exit(1)
