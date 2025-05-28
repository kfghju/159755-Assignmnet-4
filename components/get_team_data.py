import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time

driver = uc.Chrome(headless=False)
all_teams = []
column_names = []

base_url = (
    "https://sofifa.com/teams?type=all&lg%5B0%5D=13&lg%5B1%5D=31&lg%5B2%5D=53&lg%5B3%5D=19&lg%5B4%5D=16&set=true"
)

years = ['250036', '240050', '230054', '220069', '210064', '200061', '190075', '180084', '170099', '160058', '150059',
         '140052', '130034', '120002', '110002', '100002', '090002', '080002', '070002']

for year in years:
    for offset in range(0, 120, 60):
        url = f"{base_url}&r={year}&offset={offset}"
        print(f"Fetching: {url}")
        driver.get(url)
        time.sleep(1)

        try:
            if offset == 0:
                header = driver.find_elements(By.CSS_SELECTOR, "table thead th")
                column_names = [th.text.strip() for th in header[1:] if th.text.strip()]
                print("Get Column Name:", column_names)

            # 抓取每一行
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"At page {offset / 60 + 1} found {len(rows)} rows")

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) <= 1:
                    continue

                values = [col.text.strip() for col in cols[1:]]

                if len(values) < len(column_names):
                    values += [""] * (len(column_names) - len(values))
                elif len(values) > len(column_names):
                    values = values[:len(column_names)]

                row_dict = dict(zip(column_names, values))

                all_teams.append(row_dict)
        except Exception as e:
            print("Page Wrong:", e)
            continue

    df = pd.DataFrame(all_teams)
    print(all_teams)
    if not os.path.exists("../data/team_data"):
        os.makedirs("../data/team_data")
    df.to_csv(f"../data/team_data/team_stats_20{year[:2]}.csv", index=False, encoding="utf-8-sig")
    all_teams.clear()
    print(f"Save data as team_stats_20{year[:2]}.csv，include", len(df), " players")

driver.quit()
