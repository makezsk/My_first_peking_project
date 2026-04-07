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
# 2. 从数据库读取疾病对应食疗方数量
# =========================
sql = """
SELECT d.disease_name AS 疾病名称, COUNT(r.id) AS 食疗方数量
FROM disease d
JOIN recipe r ON d.id = r.disease_id
GROUP BY d.id, d.disease_name
ORDER BY 食疗方数量 DESC;
"""

disease_count_df = pd.read_sql(sql, conn)

# 关闭连接
conn.close()

# =========================
# 3. 取前五名和后五名
# =========================
top5 = disease_count_df.head(5)
bottom5 = disease_count_df.sort_values(by=["食疗方数量", "疾病名称"], ascending=[True, True]).head(5)

# =========================
# 4. 设置中文字体
# =========================
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# =========================
# 5. 创建画布
# =========================
fig, axes = plt.subplots(1, 2, figsize=(20, 8), constrained_layout=True)
fig.suptitle("疾病对应食疗方数量统计分析（数据来源：MySQL）", fontsize=20, fontweight="bold")

# =========================
# 6. 左边饼图
# =========================
axes[0].pie(
    top5["食疗方数量"],
    labels=top5["疾病名称"],
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.78,
    labeldistance=1.08,
    radius=1.15,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    textprops={"fontsize": 12}
)
axes[0].set_title("食疗方数量前五名疾病", fontsize=15, fontweight="bold", pad=15)
axes[0].axis("equal")

# =========================
# 7. 右边柱状图
# =========================
x = range(len(bottom5))

bars = axes[1].bar(
    x,
    bottom5["食疗方数量"],
    width=0.6,
    edgecolor="black",
    linewidth=1
)

axes[1].set_title("食疗方数量最少的后五名疾病", fontsize=15, fontweight="bold", pad=15)
axes[1].set_xlabel("疾病名称", fontsize=12)
axes[1].set_ylabel("食疗方数量", fontsize=12)

axes[1].set_xticks(list(x))
axes[1].set_xticklabels(
    bottom5["疾病名称"],
    rotation=25,
    ha="right",
    fontsize=11
)

axes[1].grid(axis="y", linestyle="--", alpha=0.4)
axes[1].set_ylim(0, bottom5["食疗方数量"].max() + 2)

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

plt.savefig("disease_recipe_count_mysql.png", dpi=300, bbox_inches="tight")
plt.show()