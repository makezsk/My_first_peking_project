import pandas as pd
import numpy as np
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取CSV文件
file_path = '../spider_datas/all_recipes.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

print("=" * 80)
print("数据统计分析")
print("=" * 80)

# ==================== 1. 数据基本信息 ====================
print("\n【一、数据基本信息】")
print(f"总记录数: {len(df)}")
print(f"列名: {list(df.columns)}")
print(f"\n数据类型:\n{df.dtypes}")

# 检查缺失值
print(f"\n缺失值统计:")
for col in df.columns:
    missing = df[col].isnull().sum()
    if missing > 0:
        print(f"  {col}: {missing} 条缺失 ({missing/len(df)*100:.1f}%)")

# ==================== 2. 异常数据检测 ====================
print("\n【二、异常数据检测】")

# 定义异常计数
abnormal_count = {}

# 2.1 检查菜品名称异常（包含特殊字符或为空）
empty_dish = df[df['菜品名称'].isnull() | (df['菜品名称'].str.strip() == '')]
abnormal_count['菜品名称为空'] = len(empty_dish)

# 检查菜品名称中的异常字符
special_char_pattern = r'[【】、，。！？：；""''（）]'
dish_with_special = df[df['菜品名称'].str.contains(special_char_pattern, na=False)]
abnormal_count['菜品名称含特殊字符'] = len(dish_with_special)

# 2.2 检查配方异常
empty_recipe = df[df['配方'].isnull() | (df['配方'].str.strip() == '')]
abnormal_count['配方为空'] = len(empty_recipe)

# 配方以特殊符号开头（如：、）
recipe_start_abnormal = df[df['配方'].str.startswith(('：', '、', '，', '。'), na=False)]
abnormal_count['配方以特殊符号开头'] = len(recipe_start_abnormal)

# 2.3 检查功效异常
empty_effect = df[df['功效'].isnull() | (df['功效'].str.strip() == '')]
abnormal_count['功效为空'] = len(empty_effect)

# 功效以特殊符号开头
effect_start_abnormal = df[df['功效'].str.startswith(('：', '、', '，', '。'), na=False)]
abnormal_count['功效以特殊符号开头'] = len(effect_start_abnormal)

# 2.4 检查制法异常
empty_method = df[df['制法'].isnull() | (df['制法'].str.strip() == '')]
abnormal_count['制法为空'] = len(empty_method)

# 2.5 检查疾病名称异常
empty_disease = df[df['疾病名称'].isnull() | (df['疾病名称'].str.strip() == '')]
abnormal_count['疾病名称为空'] = len(empty_disease)

# 2.6 检查链接异常
empty_link = df[df['疾病链接'].isnull() | (df['疾病链接'].str.strip() == '')]
abnormal_count['链接为空'] = len(empty_link)
invalid_link = df[~df['疾病链接'].str.startswith('http', na=False)]
abnormal_count['链接格式异常'] = len(invalid_link)

# 2.7 检查数据完整性（关键字段都为空的行）
critical_cols = ['菜品名称', '配方', '功效']
empty_critical = df[df[critical_cols].isnull().all(axis=1)]
abnormal_count['关键字段全为空'] = len(empty_critical)

# 2.8 检查重复菜品
duplicate_dishes = df[df.duplicated(subset=['菜品名称', '疾病名称'], keep=False)]
abnormal_count['重复菜品(同疾病)'] = len(duplicate_dishes) // 2 if len(duplicate_dishes) > 0 else 0

# 输出异常统计
print("\n异常数据统计:")
total_abnormal = 0
for name, count in abnormal_count.items():
    if count > 0:
        print(f"  - {name}: {count} 条")
        total_abnormal += count

print(f"\n总计异常条目数（可能存在重叠）: {total_abnormal}")

# ==================== 3. 疾病统计分析 ====================
print("\n【三、疾病统计分析】")

# 统计各疾病类型的菜品数量
disease_counts = df['疾病名称'].value_counts()
print(f"\n共有 {len(disease_counts)} 种疾病类型")
print(f"\n菜品数量最多的前10种疾病:")
for i, (disease, count) in enumerate(disease_counts.head(10).items(), 1):
    print(f"  {i}. {disease}: {count} 个菜品")

# ==================== 4. 菜品名称分析 ====================
print("\n【四、菜品名称分析】")

# 提取菜品种类关键词
dish_types = {
    '粥': df['菜品名称'].str.contains('粥', na=False).sum(),
    '汤': df['菜品名称'].str.contains('汤', na=False).sum(),
    '羹': df['菜品名称'].str.contains('羹', na=False).sum(),
    '酒': df['菜品名称'].str.contains('酒', na=False).sum(),
    '茶': df['菜品名称'].str.contains('茶', na=False).sum(),
    '糕': df['菜品名称'].str.contains('糕', na=False).sum(),
    '包子/饺': df['菜品名称'].str.contains('包子|饺子|包', na=False).sum(),
    '蛋': df['菜品名称'].str.contains('蛋', na=False).sum(),
    '炒': df['菜品名称'].str.contains('炒', na=False).sum(),
    '炖': df['菜品名称'].str.contains('炖', na=False).sum(),
}

print(f"\n菜品类型分布:")
for dish_type, count in sorted(dish_types.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"  {dish_type}: {count} 个")

# ==================== 5. 药材/食材使用频率分析 ====================
print("\n【五、药材/食材使用频率分析】")

# 常见药材列表
common_herbs = [
    '党参', '黄芪', '当归', '枸杞', '山药', '茯苓', '白术', '甘草',
    '人参', '红枣', '桂圆', '莲子', '百合', '麦冬', '天麻', '鹿茸',
    '肉苁蓉', '淫羊藿', '菟丝子', '枸杞子', '生地', '熟地', '白芍',
    '川芎', '丹参', '陈皮', '半夏', '生姜', '大枣', '薏米', '芡实'
]

herb_counts = {}
for herb in common_herbs:
    count = df['配方'].str.contains(herb, na=False).sum()
    if count > 0:
        herb_counts[herb] = count

print(f"\n常见药材/食材使用频率（前15名）:")
for i, (herb, count) in enumerate(sorted(herb_counts.items(), key=lambda x: x[1], reverse=True)[:15], 1):
    print(f"  {i}. {herb}: 出现 {count} 次")

# ==================== 6. 功效关键词分析 ====================
print("\n【六、功效关键词分析】")

# 常见功效关键词
effect_keywords = {
    '补气': ['补气', '益气', '补中益气'],
    '养血': ['养血', '补血', '益血'],
    '健脾': ['健脾', '补脾', '益脾'],
    '补肾': ['补肾', '益肾', '温肾', '滋肾'],
    '滋阴': ['滋阴', '养阴', '益阴'],
    '温阳': ['温阳', '壮阳', '助阳'],
    '清热': ['清热', '降火', '凉血'],
    '祛湿': ['祛湿', '化湿', '利湿'],
    '安神': ['安神', '宁心', '养心'],
    '通便': ['通便', '润肠'],
    '止血': ['止血', '摄血'],
    '调经': ['调经', '通经'],
}

effect_counts = {}
for category, keywords in effect_keywords.items():
    pattern = '|'.join(keywords)
    count = df['功效'].str.contains(pattern, na=False).sum()
    effect_counts[category] = count

print(f"\n功效关键词分布:")
for category, count in sorted(effect_counts.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"  {category}: {count} 个菜品")

# ==================== 7. 数据质量评分 ====================
print("\n【七、数据质量评估】")

# 计算完整率
complete_rate = {}
for col in df.columns:
    complete_rate[col] = (len(df) - df[col].isnull().sum()) / len(df) * 100

print("\n各字段完整率:")
for col, rate in complete_rate.items():
    quality = "✓ 优秀" if rate >= 95 else "○ 良好" if rate >= 85 else "△ 一般" if rate >= 70 else "✗ 较差"
    print(f"  {col}: {rate:.1f}% {quality}")

# 整体数据质量评分
overall_complete_rate = df[critical_cols].notnull().all(axis=1).sum() / len(df) * 100
print(f"\n整体数据质量评分（关键字段完整率）: {overall_complete_rate:.1f}%")