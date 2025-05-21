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
    "https://sofifa.com/players?"
    "showCol[0]=pi&showCol[1]=ae&showCol[2]=hi&showCol[3]=wi&showCol[4]=pf&showCol[5]=oa&showCol[6]=pt"
    "&showCol[7]=bo&showCol[8]=bp&showCol[9]=gu&showCol[10]=vl&showCol[11]=wg&showCol[12]=rc&showCol[13]=ta"
    "&showCol[14]=cr&showCol[15]=fi&showCol[16]=he&showCol[17]=sh&showCol[18]=vo&showCol[19]=ts&showCol[20]=dr"
    "&showCol[21]=cu&showCol[22]=fr&showCol[23]=lo&showCol[24]=bl&showCol[25]=to&showCol[26]=ac&showCol[27]=sp"
    "&showCol[28]=ag&showCol[29]=re&showCol[30]=ba&showCol[31]=tp&showCol[32]=so&showCol[33]=ju&showCol[34]=st"
    "&showCol[35]=sr&showCol[36]=ln&showCol[37]=te&showCol[38]=ar&showCol[39]=in&showCol[40]=po&showCol[41]=vi"
    "&showCol[42]=pe&showCol[43]=cm&showCol[44]=td&showCol[45]=ma&showCol[46]=sa&showCol[47]=sl&showCol[48]=tg"
    "&showCol[49]=gd&showCol[50]=gh&showCol[51]=gc&showCol[52]=gp&showCol[53]=gr&showCol[54]=tt&showCol[55]=bs"
    "&showCol[56]=ir&showCol[57]=pac&showCol[58]=sho&showCol[59]=pas&showCol[60]=dri&showCol[61]=def"
    "&showCol[62]=phy"
)

# 分页抓取（前3页）
for offset in range(0, 3060, 60):
    url = f"{base_url}&offset={offset}"
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
        print(f"✅ 第{offset/60 + 1}页共找到 {len(rows)} 行")

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

driver.quit()

# 保存结果
df = pd.DataFrame(all_players)
df["Value"] = df["Value"].apply(parse_euro)
df["Wage"] = df["Wage"].apply(parse_euro)
df["Release clause"] = df["Release clause"].apply(parse_euro)
df.to_csv("players_stats2.csv", index=False, encoding="utf-8-sig")
print("✅ 成功保存 players_stats.csv，共", len(df), "名球员")
