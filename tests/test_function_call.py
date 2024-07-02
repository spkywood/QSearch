# from tools.register import (
#     get_capacity_curve, 
#     get_history_features,
#     get_real_time_water_condition
# )

# def draw():
#     import matplotlib.pyplot as plt
#     # from matplotlib.font_manager import FontManager
#     # fm = FontManager()
#     # mat_fonts = set(f.name for f in fm.ttflist)
#     from pylab import mpl
#     mpl.rcParams['font.family']= "SimHei"       # 指定字体，实际上相当于修改 matplotlibrc 文件　只不过这样做是暂时的　下次失效
#     mpl.rcParams['axes.unicode_minus']=False    # 正确显示负号，防止变成方框
#     # 数据
#     data = [
#         {"capactiy": 0.0, "level": 220.0},
#         {"capactiy": 5.0, "level": 247.021},
#         {"capactiy": 10.0, "level": 254.0},
#         {"capactiy": 15.0, "level": 257.947},
#         {"capactiy": 20.0, "level": 261.348},
#         {"capactiy": 25.0, "level": 264.157},
#         {"capactiy": 30.0, "level": 266.591},
#         {"capactiy": 35.0, "level": 268.864},
#         {"capactiy": 40.0, "level": 270.926},
#         {"capactiy": 45.0, "level": 272.778},
#         {"capactiy": 51.0, "level": 275.0}
#     ]
#     # 提取横坐标和纵坐标
#     capacities = [d['capactiy'] for d in data]
#     levels = [d['level'] for d in data]
#     # 绘制曲线
#     plt.figure(figsize=(10, 5))
#     plt.plot(capacities, levels, marker='o')
#     # 在曲线上标注数值
#     for i, txt in enumerate(levels):
#         plt.annotate(f"{txt} m", (capacities[i], levels[i]), textcoords="offset points", xytext=(0,10), ha='center')

#     for i in range(220, 290, 10):
#         plt.axhline(y=i, color='#D3D3D3', linestyle='--', linewidth=1, label=f'y={i}')

#     plt.fill_between(capacities, levels, y2=220, color='#1E90FF', alpha=0.1)
#     # 设置标题和坐标轴标签
#     plt.title('小浪底水库库容与水位关系曲线')
#     plt.xlabel(r'库容 (m$^{{\scr 3}}$)')
#     plt.ylabel('水位 (m)')
#     # 设置横坐标步长
#     plt.xticks(range(0, 52, 5))
#     # 显示网格
#     plt.grid(False)
#     # 显示图表
#     # plt.show()
    
#     plt.savefig('test.png')


# if __name__ == '__main__':
#     # import json
#     from demo.constants import ennm
#     # for e in ennm:
#     # test = get_capacity_curve("小浪底")
#         # test = get_history_features(e, 2024)
#         # print(test)
#         # break
    
#     # print(json.dumps(test, ensure_ascii=False, indent=4))
#     # draw()
#     get_real_time_water_condition("小浪底")