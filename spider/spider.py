# 作者 宗圣凯 时间 2026-04-01
import re
import csv
import requests
from lxml import etree
from urllib.parse import urljoin

# =========================
# 1. 基础配置
# =========================
BASE_URL = "http://www.cnzyao.com/shiliao/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# 2. 获取网页源码
# =========================
def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"请求失败: {url} -> {e}")
        return ""


# =========================
# 3. 解析首页，提取内科食疗和妇科病食疗的疾病链接
# =========================
def parse_homepage():
    html_text = get_html(BASE_URL)
    if not html_text:
        return [], []

    html = etree.HTML(html_text)

    # 提取“内科食疗”板块下面的所有链接
    nk_links = html.xpath('//h2[contains(., "内科") or contains(., "内科食疗")]/following-sibling::*[1]//a')

    # 提取“妇科病食疗”板块下面的所有链接
    fk_links = html.xpath('//h2[contains(., "妇科") or contains(., "妇科病食疗")]/following-sibling::*[1]//a')

    # 如果没抓到，就放宽规则
    if not nk_links:
        nk_links = html.xpath('//*[contains(text(), "内科食疗")]/ancestor::*[1]//a')
    if not fk_links:
        fk_links = html.xpath('//*[contains(text(), "妇科病食疗")]/ancestor::*[1]//a')

    nk_result = parse_links(nk_links, BASE_URL)
    fk_result = parse_links(fk_links, BASE_URL)

    return nk_result, fk_result


# =========================
# 4. 整理链接结果
# =========================
def parse_links(link_list, base_url):
    result = []
    seen = set()

    for a in link_list:
        name = ''.join(a.xpath('.//text()')).strip()
        href = a.xpath('./@href')

        if name and href:
            full_url = urljoin(base_url, href[0].strip())
            key = (name, full_url)

            if key not in seen:
                seen.add(key)
                result.append((name, full_url))

    return result


# =========================
# 5. 获取页面正文文本
# =========================
def get_page_text(url):
    html_text = get_html(url)
    if not html_text:
        return ""

    try:
        html = etree.HTML(html_text)
        texts = html.xpath('//body//text()')
        texts = [t.strip() for t in texts if t.strip()]
        page_text = '\n'.join(texts)
        return page_text
    except Exception as e:
        print(f"正文解析失败: {url} -> {e}")
        return ""


# =========================
# 6. 提取疾病页中的所有食疗方
# 核心字段：菜品名称、配方、功效、制法
# 不提取“用法”
# =========================
def extract_recipes(page_text):
    result = []

    if not page_text:
        return result

    # =========================
    # 1. 文本预处理
    # =========================
    text = page_text

    # 统一配方字段
    text = text.replace("【食疗配方】", "【配方】")
    text = text.replace("【食疗方】", "【配方】")
    text = text.replace("食疗配方：", "【配方】")
    text = text.replace("食疗配方:", "【配方】")
    text = text.replace("配方：", "【配方】")
    text = text.replace("配方:", "【配方】")
    text = text.replace("组成：", "【配方】")
    text = text.replace("组成:", "【配方】")
    text = text.replace("原料：", "【配方】")
    text = text.replace("原料:", "【配方】")

    # 统一功效字段
    text = text.replace("【功效主治】", "【功效】")
    text = text.replace("功效主治：", "【功效】")
    text = text.replace("功效主治:", "【功效】")
    text = text.replace("功效：", "【功效】")
    text = text.replace("功效:", "【功效】")
    text = text.replace("主治：", "【功效】")
    text = text.replace("主治:", "【功效】")

    # 统一制法字段
    text = text.replace("【制作】", "【制法】")
    text = text.replace("制作：", "【制法】")
    text = text.replace("制作:", "【制法】")
    text = text.replace("制法：", "【制法】")
    text = text.replace("制法:", "【制法】")
    text = text.replace("做法：", "【制法】")
    text = text.replace("做法:", "【制法】")

    # 保留换行，压缩每行空格
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text = "\n".join(lines)

    # =========================
    # 2. 用【配方】定位每一道菜
    # =========================
    matches = list(re.finditer(r"【配方】", text))
    if not matches:
        return result

    blocks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        blocks.append((start, block))

    # =========================
    # 3. 逐块提取
    # =========================
    for start, block in blocks:
        prefix_text = text[max(0, start - 200):start]
        prefix_lines = [line.strip() for line in prefix_text.split("\n") if line.strip()]
        prefix_lines.reverse()

        dish_name = ""

        for line in prefix_lines:
            if any(x in line for x in [
                "临床表现", "以下为推荐", "参考使用", "中医食疗配方",
                "食疗方法", "常见食疗", "辨证论治", "食疗药膳"
            ]):
                continue

            if "【配方】" in line or "【功效】" in line or "【制法】" in line:
                continue

            if len(line) > 35:
                continue

            cleaned_name = line
            cleaned_name = re.sub(r'^[一二三四五六七八九十]+、', '', cleaned_name)
            cleaned_name = re.sub(r'^（[一二三四五六七八九十]+）', '', cleaned_name)
            cleaned_name = re.sub(r'^\([一二三四五六七八九十]+\)', '', cleaned_name)
            cleaned_name = re.sub(r'^\d+[、\.．]\s*', '', cleaned_name)
            cleaned_name = cleaned_name.strip("：: ")

            if cleaned_name and "配方" not in cleaned_name and "功效" not in cleaned_name and "制法" not in cleaned_name:
                dish_name = cleaned_name
                break

        # 配方
        formula_match = re.search(
            r'【配方】\s*(.*?)(?=【功效】|【制法】|$)',
            block,
            re.S
        )
        formula = formula_match.group(1).strip() if formula_match else ""

        # 功效
        effect_match = re.search(
            r'【功效】\s*(.*?)(?=【制法】|$)',
            block,
            re.S
        )
        effect = effect_match.group(1).strip() if effect_match else ""

        # 制法
        # 这里新增：遇到“下一道菜标题”就停止
        method_match = re.search(
            r'【制法】\s*(.*?)(?='
            r'用法[:：]|【用法】|'
            r'\n[一二三四五六七八九十]+、|'
            r'\n（[一二三四五六七八九十]+）|'
            r'\n\([一二三四五六七八九十]+\)|'
            r'\n\d+[、\.．]|'
            r'$)',
            block,
            re.S
        )
        method = method_match.group(1).strip() if method_match else ""

        # 清洗
        dish_name = re.sub(r"\s+", " ", dish_name).strip()
        formula = re.sub(r"\s+", " ", formula).strip()
        effect = re.sub(r"\s+", " ", effect).strip()
        method = re.sub(r"\s+", " ", method).strip()

        if formula:
            result.append({
                "菜品名称": dish_name,
                "配方": formula,
                "功效": effect,
                "制法": method
            })

    return result


# =========================
# 7. 主流程
# =========================
def main():
    # 第一步：首页拿疾病链接
    nk_result, fk_result = parse_homepage()

    print("===== 内科食疗疾病数量 =====", len(nk_result))
    print("===== 妇科病食疗疾病数量 =====", len(fk_result))

    # 合并，不再区分内科和妇科
    all_links = nk_result + fk_result

    # 去重
    unique_links = []
    seen = set()

    for disease_name, disease_url in all_links:
        if disease_url not in seen:
            seen.add(disease_url)
            unique_links.append((disease_name, disease_url))

    print(f"共得到 {len(unique_links)} 个疾病链接")

    # 第二步：逐个疾病页提取食疗方
    all_recipe_data = []

    for disease_name, disease_url in unique_links:
        print("正在爬取：", disease_name, disease_url)

        page_text = get_page_text(disease_url)
        if not page_text:
            continue

        recipe_list = extract_recipes(page_text)

        print(f"疾病：{disease_name}，提取到 {len(recipe_list)} 条食疗方")

        for item in recipe_list:
            all_recipe_data.append({
                "疾病名称": disease_name,
                "疾病链接": disease_url,
                "菜品名称": item["菜品名称"],
                "配方": item["配方"],
                "功效": item["功效"],
                "制法": item["制法"]
            })

    print(f"\n共提取到 {len(all_recipe_data)} 条食疗方")

    # 第三步：预览前10条
    for i, row in enumerate(all_recipe_data[:10], 1):
        print(f"\n第{i}条")
        print("疾病名称：", row["疾病名称"])
        print("菜品名称：", row["菜品名称"])
        print("配方：", row["配方"])
        print("功效：", row["功效"])
        print("制法：", row["制法"])

    # 第四步：保存为 CSV
    with open("../spider_datas/all_recipes.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["疾病名称", "疾病链接", "菜品名称", "配方", "功效", "制法"]
        )
        writer.writeheader()
        writer.writerows(all_recipe_data)

    print("\n已保存到 all_recipes.csv")


# =========================
# 8. 程序入口
# =========================
if __name__ == "__main__":
    main()