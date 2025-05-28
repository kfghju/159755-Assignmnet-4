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

# url for fetching latest team stats
base_url2 = (
    "https://sofifa.com/teams?type=all&lg%5B0%5D=13&lg%5B1%5D=31&lg%5B2%5D=53&lg%5B3%5D=19&lg%5B4%5D=16&lg%5B5%5D=14"
    "&lg%5B6%5D=60&lg%5B7%5D=61&lg%5B8%5D=32&lg%5B9%5D=54&lg%5B10%5D=20&lg%5B11%5D=2076&lg%5B12%5D=17&lg%5B13%5D=10"
    "&lg%5B14%5D=308&lg%5B15%5D=4&lg%5B16%5D=319&lg%5B17%5D=68&lg%5B18%5D=41&lg%5B19%5D=1&lg%5B20%5D=63&lg%5B21%5D"
    "=189&lg%5B22%5D=80&lg%5B23%5D=190&lg%5B24%5D=50&lg%5B25%5D=66&lg%5B26%5D=317&lg%5B27%5D=332&lg%5B28%5D=56&lg"
    "%5B29%5D=64&lg%5B30%5D=318&lg%5B31%5D=330&lg%5B32%5D=67&lg%5B33%5D=313&lg%5B34%5D=65&lg%5B35%5D=322&lg%5B36%5D=7"
    "&lg%5B37%5D=2025&lg%5B38%5D=353&lg%5B39%5D=337&lg%5B40%5D=2018&lg%5B41%5D=338&lg%5B42%5D=2017&lg%5B43%5D=336&lg"
    "%5B44%5D=335&lg%5B45%5D=2020&lg%5B46%5D=2019&lg%5B47%5D=341&lg%5B48%5D=39&lg%5B49%5D=350&lg%5B50%5D=349&lg%5B51"
    "%5D=2013&lg%5B52%5D=83&lg%5B53%5D=2012&lg%5B54%5D=351&lg%5B55%5D=2149&lg%5B56%5D=347&r=250036&set=true&offset=600"
)

years = ['240050', '230054', '220069', '210064', '200061', '190075', '180084', '170099', '160058', '150059',
         '140052', '130034', '120002', '110002', '100002', '090002', '080002', '070002']

for year in years:
    # for offset in range(0, 660, 60):
    for offset in range(0, 120, 60):
        # url = f"{base_url2}&offset={offset}"
        url = f"{base_url}&r={year}&offset={offset}"
        print(f"Fetching: {url}")
        driver.get(url)
        time.sleep(1)

        try:
            if offset == 0:
                header = driver.find_elements(By.CSS_SELECTOR, "table thead th")
                column_names = [th.text.strip() for th in header[1:] if th.text.strip()]
                print("Get Column Name:", column_names)

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
