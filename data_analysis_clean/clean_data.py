# 作者 钟一鸣 时间 2026-04-02
import re
import pandas as pd

# =========================
# 1. 读取原始数据
# =========================
df = pd.read_csv("../spider_datas/all_recipes.csv", encoding="utf-8-sig")

# =========================
# 2. 删除菜品名称为空的行
# =========================
df = df.dropna(subset=["菜品名称"])
df["菜品名称"] = df["菜品名称"].astype(str).str.strip()

# =========================
# 3. 清洗菜品名称
# =========================
def clean_dish_name(name):
    name = str(name).strip()
    name = re.sub(r"\s+", " ", name).strip()

    name = re.sub(r'^[一二三四五六七八九十]+、', '', name)
    name = re.sub(r'^（[一二三四五六七八九十]+）', '', name)
    name = re.sub(r'^\([一二三四五六七八九十]+\)', '', name)
    name = re.sub(r'^\d+[、\.．]\s*', '', name)

    name = re.sub(r'^[、，,\.。\s:：]+', '', name)
    name = re.sub(r'^【', '', name)
    name = re.sub(r'】$', '', name)

    name = name.strip(" 、，,.。【】[]()（）:：")
    return name

# =========================
# 4. 清洗通用文本字段
# =========================
def clean_text_field(text):
    text = str(text).strip()

    # 压缩空格
    text = re.sub(r"\s+", " ", text).strip()

    # 去掉开头残留标点
    text = re.sub(r'^[：:、，,\.\s]+', '', text)

    # -------------------------
    # 先截断网页尾部噪声
    # -------------------------
    noise_patterns = [
        r'（本文由中医药网整理.*',
        r'本文由中医药网整理.*',
        r'内容仅供参考.*',
        r'上一篇[:：].*',
        r'下一篇[:：].*',
        r'更多关于.*',
        r'.*频道热.*',
        r'上一篇.*',
        r'下一篇.*',
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, '', text)

    # -------------------------
    # 去掉中文和数字之间明显不必要的空格
    # 例如：党参 100克 -> 党参100克
    # -------------------------
    text = re.sub(r'([\u4e00-\u9fa5])\s+(\d)', r'\1\2', text)

    # 去掉数字和中文单位之间空格
    # 例如：100 克 -> 100克
    text = re.sub(r'(\d)\s+([\u4e00-\u9fa5])', r'\1\2', text)

    # 去掉中文之间明显多余空格
    # 例如：茯苓 粉 -> 茯苓粉
    text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)

    # 再去一次首尾杂质
    text = text.strip(" ：:、，,.;；。!！?？")

    return text

# =========================
# 5. 执行清洗
# =========================
df["菜品名称"] = df["菜品名称"].apply(clean_dish_name)

for col in ["配方", "功效", "制法"]:
    if col in df.columns:
        df[col] = df[col].astype(str).apply(clean_text_field)

# 去掉空菜名
df = df[df["菜品名称"] != ""]

# =========================
# 6. 保存清洗后的数据
# =========================
df.to_csv("all_recipes_cleaned.csv", index=False, encoding="utf-8-sig")

print("数据清洗完成，已保存为 all_recipes_cleaned.csv")
print("清洗后数据条数：", len(df))
print(df.head(10).to_string())