import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from chan import Chan

from .plot_driver import PlotDriver


class AnimateDriver:
    def __init__(self, chan: Chan, plot_config=None, plot_para=None):
        if plot_config is None:
            plot_config = {}
        if plot_para is None:
            plot_para = {}

        self.chan = chan
        self.plot_config = plot_config
        self.plot_para = plot_para
        self.chan_gen = self.chan.step_load()

        # 初始化，先画第一帧
        next(self.chan_gen)
        self.plot_driver = PlotDriver(self.chan, self.plot_config, self.plot_para)
        self.figure = self.plot_driver.figure

        # 创建动画
        # interval: 帧之间的延迟（毫秒）
        # blit=False: 因为标题等元素也在变化，所以需要重绘整个区域
        # save_count: 动画的最大帧数，可以设置一个较大的值
        self.anim = FuncAnimation(self.figure, self.update, interval=100, blit=False, save_count=1000)

        plt.show()

    def update(self, frame):
        # 更新chan的状态
        res = next(self.chan_gen, None)
        if res is None:
            self.anim.event_source.stop()  # 如果生成器耗尽，停止动画
            print("动画播放完毕。")
            return

        # 不再创建新实例，直接在现有实例上重绘
        self.plot_driver.draw()
