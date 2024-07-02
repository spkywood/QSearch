def test(capacities, levels):
    '''绘制图像'''
    from pylab import mpl
    import matplotlib.pyplot as plt
    from matplotlib.ticker import AutoLocator, MaxNLocator 

    # 设置中文字体
    mpl.rcParams['font.family']= "SimHei"      
    mpl.rcParams['axes.unicode_minus']=False

    # 绘制曲线
    x0 = len(capacities) if len(capacities) <= 20 else 20
    plt.figure(figsize=(x0 if x0 > 8 else 12, 8))
    plt.plot(capacities, levels, marker='o')
    # 在曲线上标注数值
    for i, level in enumerate(levels):
        plt.annotate(f"{level} m", (capacities[i], levels[i]), textcoords="offset points", xytext=(0,10), ha='center')

    start = int(min(levels))
    end = int(max(levels))
    a = int(int(end - start)/6)
    for i in range(start, end, a):
        plt.axhline(y=i, color='#D3D3D3', linestyle='--', linewidth=1, label=f'y={i}')

    plt.fill_between(capacities, levels, y2=start, color='#1E90FF', alpha=0.1)
    # 设置标题和坐标轴标签
    plt.title(f'{ennm}水库库容与水位关系曲线')
    plt.xlabel(r'库容 (m$^{{\scr 3}}$)')
    plt.ylabel('水位 (m)')
    plt.tight_layout()  # 自动调整参数，使图像各元素位置不重叠
    # 设置横坐标步长
    plt.xticks(capacities)
    # 显示网格
    plt.grid(False)
    # 显示图表
    # plt.show()
    
    plt.savefig(f'demo/data/result/test.png')

