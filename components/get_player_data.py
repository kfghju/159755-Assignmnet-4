import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time


def parse_euro(value):
    if pd.isna(value): return None
    value = str(value).replace("€", "").upper()
    if value.endswith("M"):
        return float(value[:-1]) * 1_000_000
    elif value.endswith("K"):
        return float(value[:-1]) * 1_000
    else:
        return float(value)


# 初始化浏览器
driver = uc.Chrome(headless=False)
all_players = []
column_names = []

# 完整字段 URL
base_url = (
    "https://sofifa.com/players?type=all&lg%5B0%5D=13&lg%5B1%5D=31&lg%5B2%5D=53&lg%5B3%5D=19&lg%5B4%5D=16&showCol%5B0"
    "%5D=ae&showCol%5B1%5D=hi&showCol%5B2%5D=wi&showCol%5B3%5D=oa&showCol%5B4%5D=pt&showCol%5B5%5D=bp&showCol%5B6%5D"
    "=vl&showCol%5B7%5D=wg&showCol%5B8%5D=sh&showCol%5B9%5D=dr&showCol%5B10%5D=st&set=true"
)

# years = ['250036', '240036', '230036', '220036', '210036', '200036', '190036', '180036', '170036', '160036', '150036',
#          '140036', '130036', '120036', '110036', '100036', '090036', '080036', '070036']

years = ['080036', '070036']

for year in years:
    for offset in range(0, 1320, 60):
        url = f"{base_url}&r={year}&offset={offset}"
        print(f"📥 抓取中: {url}")
        driver.get(url)
        time.sleep(1)

        try:
            # 获取字段名：跳过第一个 th（头像图标列）
            if offset == 0:
                header = driver.find_elements(By.CSS_SELECTOR, "table thead th")
                column_names = [th.text.strip() for th in header[1:] if th.text.strip()]
                print("✅ 获取列名:", column_names)

            # 抓取每一行
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"✅ 第{offset / 60 + 1}页共找到 {len(rows)} 行")

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) <= 1:
                    continue

                # 提取完整姓名
                try:
                    name_cell = cols[1].find_element(By.CSS_SELECTOR, "a")
                    full_name = name_cell.get_attribute("data-tippy-content") or name_cell.text.strip()
                except:
                    full_name = ""

                # 提取数据（跳过头像列）
                values = [col.text.strip() for col in cols[1:]]

                # 对齐列数
                if len(values) < len(column_names):
                    values += [""] * (len(column_names) - len(values))
                elif len(values) > len(column_names):
                    values = values[:len(column_names)]

                row_dict = dict(zip(column_names, values))
                row_dict["Full Name"] = full_name  # ✅ 插入完整姓名

                all_players.append(row_dict)
        except Exception as e:
            print("❌ 页面出错:", e)
            continue
    # 保存结果
    df = pd.DataFrame(all_players)
    df["Value"] = df["Value"].apply(parse_euro)
    df["Wage"] = df["Wage"].apply(parse_euro)
    df.to_csv(f"../data/player_data/players_stats_{year[:2]}.csv", index=False, encoding="utf-8-sig")
    print(f"Save data as players_stats_{year[:2]}.csv，include", len(df), " players")

driver.quit()

