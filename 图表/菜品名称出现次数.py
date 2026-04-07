import pymysql
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. 连接 MySQL
# =========================
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="admin",   # 改成你的 MySQL 密码
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
# 5. 创建画布
# =========================
fig, axes = plt.subplots(1, 2, figsize=(20, 8), constrained_layout=True)
fig.suptitle("菜品名称出现次数统计分析（数据来源：MySQL）", fontsize=20, fontweight="bold")

# =========================
# 6. 左边饼图
# =========================
axes[0].pie(
    top5["出现次数"],
    labels=top5["菜品名称"],
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.78,
    labeldistance=1.08,
    radius=1.15,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    textprops={"fontsize": 12}
)
axes[0].set_title("出现次数最多的前五个菜品", fontsize=15, fontweight="bold", pad=15)
axes[0].axis("equal")

# =========================
# 7. 右边柱状图
# =========================
x = range(len(bottom5))

bars = axes[1].bar(
    x,
    bottom5["出现次数"],
    width=0.6,
    edgecolor="black",
    linewidth=1
)

axes[1].set_title("出现次数最少的后五个菜品", fontsize=15, fontweight="bold", pad=15)
axes[1].set_xlabel("菜品名称", fontsize=12)
axes[1].set_ylabel("出现次数", fontsize=12)

axes[1].set_xticks(list(x))
axes[1].set_xticklabels(
    bottom5["菜品名称"],
    rotation=25,
    ha="right",
    fontsize=11
)

axes[1].grid(axis="y", linestyle="--", alpha=0.4)
axes[1].set_ylim(0, bottom5["出现次数"].max() + 2)

# 柱子顶部显示数值
for bar in bars:
    height = bar.get_height()
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.05,
        f"{int(height)}",
        ha="center",
        va="bottom",
        fontsize=11
    )

# 在柱状图中加入说明文字
axes[1].text(
    0.98, 0.95,
    "菜品名称出现频次呈现明显长尾分布，\n少数菜品重复出现较多，\n而多数菜品仅出现一次。",
    transform=axes[1].transAxes,
    fontsize=11,
    ha="right",
    va="top",
    bbox=dict(boxstyle="round,pad=0.4", alpha=0.15)
)

# =========================
# 8. 保存并显示
# =========================
plt.savefig("dish_count_mysql.png", dpi=300, bbox_inches="tight")
plt.show()