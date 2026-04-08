# 作者 马明洋 时间 2026-04-02
import pandas as pd
import pymysql

# =========================
# 1. 读取清洗后的 CSV
# =========================
df = pd.read_csv("../data_analysis_clean/all_recipes_cleaned.csv", encoding="utf-8-sig")

# =========================
# 2. 连接 MySQL 数据库
# =========================
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="admin",
    database="diet_system",
    charset="utf8mb4"
)

cursor = conn.cursor()

# =========================
# 3. 先处理疾病表
# 去重后插入 disease
# =========================
disease_df = df[["疾病名称", "疾病链接"]].drop_duplicates()

# 这里先简单给类别统一写“未分类”
# 如果你后面有内科/妇科信息，也可以再改
disease_df["category"] = "未分类"

for _, row in disease_df.iterrows():
    disease_name = str(row["疾病名称"]).strip()
    disease_url = str(row["疾病链接"]).strip()
    category = str(row["category"]).strip()

    sql = """
    INSERT IGNORE INTO disease (disease_name, disease_url, category)
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (disease_name, disease_url, category))

conn.commit()
print("疾病表写入完成")

# =========================
# 4. 查询 disease 表，建立 疾病名称 -> id 的映射
# =========================
cursor.execute("SELECT id, disease_name FROM disease")
disease_rows = cursor.fetchall()

disease_map = {}
for row in disease_rows:
    disease_id = row[0]
    disease_name = row[1]
    disease_map[disease_name] = disease_id

# =========================
# 5. 写入 recipe 表
# =========================
for _, row in df.iterrows():
    disease_name = str(row["疾病名称"]).strip()
    dish_name = str(row["菜品名称"]).strip()
    formula = str(row["配方"]).strip()
    effect = str(row["功效"]).strip()
    method = str(row["制法"]).strip()

    # 根据疾病名称找 disease_id
    disease_id = disease_map.get(disease_name)

    # 如果没找到，就跳过
    if not disease_id:
        continue

    sql = """
    INSERT INTO recipe (disease_id, dish_name, formula, effect, method)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (disease_id, dish_name, formula, effect, method))

conn.commit()
print("食疗方表写入完成")

# =========================
# 6. 关闭连接
# =========================
cursor.close()
conn.close()

print("数据已成功写入数据库")