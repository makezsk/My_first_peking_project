# 作者 王岩茹 时间 2026-04-02
import pymysql
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. 连接 MySQL
# =========================
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="admin",
    database="diet_system",
    charset="utf8mb4"
)

# =========================
# 2. 从数据库读取菜品统计数据
# =========================
sql = """
SELECT dish_name AS 菜品名称, COUNT(*) AS 出现次数
FROM recipe
GROUP BY dish_name
ORDER BY 出现次数 DESC;
"""

dish_count_df = pd.read_sql(sql, conn)

# 关闭数据库连接
conn.close()

# =========================
# 3. 取前五名和后五名
# =========================
top5 = dish_count_df.head(5)
bottom5 = dish_count_df.sort_values(by=["出现次数", "菜品名称"], ascending=[True, True]).head(5)

# =========================
# 4. 设置中文字体
# =========================
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# =========================
# 5. 创建画布（为顶部标题预留空间）
# =========================
fig = plt.figure(figsize=(24, 11))
fig.suptitle("菜 品 名 称 出 现 次 数 统 计 分 析",
             fontsize=36, fontweight="bold",
             y=0.96,  # 控制标题垂直位置
             color='#2C3E50',
             fontfamily='Microsoft YaHei')

# 创建两个子图（增加子图间距）
axes = fig.subplots(1, 2)
fig.subplots_adjust(top=0.85, wspace=0.5)  # 调整顶部空间和子图间距

# =========================
# 6. 左边饼图（显示数量和占比）
# =========================
# 自定义颜色
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

# 准备饼图数据：显示数量和占比
total = top5["出现次数"].sum()
labels_with_count = [f"{name}\n({count}次)" for name, count in zip(top5["菜品名称"], top5["出现次数"])]

wedges, texts, autotexts = axes[0].pie(
    top5["出现次数"],
    labels=labels_with_count,  # 使用包含数量和菜品名称的标签
    autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total)}次)',  # 显示占比和数量
    startangle=90,
    pctdistance=0.78,
    labeldistance=1.15,  # 增加标签距离，避免拥挤
    radius=1.2,
    colors=colors,
    wedgeprops={"edgecolor": "white", "linewidth": 2.5},
    textprops={"fontsize": 16, "fontweight": "bold"}
)

# 美化百分比文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(15)
    autotext.set_fontweight('bold')

axes[0].set_title("出现次数最多的前五个菜品", fontsize=22, fontweight="bold", pad=25, color='#2C3E50')
axes[0].axis("equal")

# 添加中心注释
centre_circle = plt.Circle((0,0), 0.70, fc='white', linewidth=1.5, edgecolor='#2C3E50', alpha=0.9)
axes[0].add_artist(centre_circle)
axes[0].text(0, 0, f'总计\n{total}次',
             ha='center', va='center', fontsize=16, fontweight='bold', color='#2C3E50')

# =========================
# 7. 右边柱状图
# =========================
x = range(len(bottom5))

bars = axes[1].bar(
    x,
    bottom5["出现次数"],
    width=0.65,
    edgecolor="black",
    linewidth=1.5,
    color='#E74C3C',
    alpha=0.85
)

axes[1].set_title("出现次数最少的后五个菜品", fontsize=22, fontweight="bold", pad=25, color='#2C3E50')
axes[1].set_xlabel("菜 品 名 称", fontsize=17, fontweight="bold", labelpad=10)
# Y轴标签竖着排列
axes[1].set_ylabel("出\n现\n次\n数", fontsize=17, fontweight="bold", rotation=0,
                   ha="center", va="center", labelpad=15)

axes[1].set_xticks(list(x))
axes[1].set_xticklabels(
    bottom5["菜品名称"],
    rotation=25,
    ha="right",
    fontsize=15,
    fontweight='500'
)

axes[1].grid(axis="y", linestyle="--", alpha=0.4, linewidth=1, color='#BDC3C7')
axes[1].set_ylim(0, bottom5["出现次数"].max() + 2.5)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.25,
        f"{int(height)}",
        ha="center",
        va="bottom",
        fontsize=16,
        fontweight="bold",
        color='#E74C3C'
    )

# 在柱状图中加入说明文字
axes[1].text(
    0.98, 0.95,
    "菜品名称出现频次呈现明显长尾分布，\n少数菜品重复出现较多，\n而多数菜品仅出现一次。",
    transform=axes[1].transAxes,
    fontsize=13,
    ha="right",
    va="top",
    bbox=dict(boxstyle="round,pad=0.5", alpha=0.15, facecolor='#ECF0F1', edgecolor='#BDC3C7')
)

# =========================
# 8. 保存并显示
# =========================
plt.savefig("dish_count_mysql.png", dpi=300, bbox_inches="tight", facecolor='white')
plt.show()