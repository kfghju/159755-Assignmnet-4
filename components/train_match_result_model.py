import joblib
import pandas as pd
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler


# pd.set_option('display.max_rows', 100)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)
db_path = "../data/allData.sl3"
conn = sqlite3.connect(db_path)

df = pd.read_sql_query("""SELECT
    m.*,

    -- Home Team Rating
    th.overall AS home_overall,
    th.attack AS home_attack,
    th.midfield AS home_midfield,
    th.defence AS home_defence,
    th.players AS home_players,

    -- Away Team Rating
    ta.overall AS away_overall,
    ta.attack AS away_attack,
    ta.midfield AS away_midfield,
    ta.defence AS away_defence,
    ta.players AS away_players

FROM match_stats AS m

LEFT JOIN team_stats AS th
    ON m.home_team = th.team AND substr(m.season, 1, 4) = CAST(th.year AS TEXT)

LEFT JOIN team_stats AS ta
    ON m.away_team = ta.team AND substr(m.season, 1, 4) = CAST(ta.year AS TEXT);""", conn)
conn.close()


df = df.dropna(subset=[
    'b365_prob_h', 'b365_prob_d', 'b365_prob_a',
    'home_overall', 'home_attack', 'home_midfield', 'home_defence', 'home_players',
    'away_overall', 'away_attack', 'away_midfield', 'away_defence', 'away_players',
    'ftr'
])

# print(df['ftr'].value_counts())

df = df[df['ftr'] != 'D']
# df['ftr_encoded'] = df['ftr'].map({'H': 0, 'D': 1, 'A': 2})
df['ftr_encoded'] = df['ftr'].map({'H': 0, 'A': 1})
df['overall_diff'] = df['home_overall'] - df['away_overall']
df['attack_diff'] = df['home_attack'] - df['away_attack']
df['midfield_diff'] = df['home_midfield'] - df['away_midfield']
df['defence_diff'] = df['home_defence'] - df['away_defence']
df['age_diff'] = df['home_players'] - df['away_players']

features = [
    'b365_prob_h', 'b365_prob_d', 'b365_prob_a',
    'overall_diff', 'attack_diff', 'midfield_diff',
    'defence_diff', 'age_diff'
]
X = df[features]
y = df['ftr_encoded']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression(max_iter=1000, class_weight='balanced', solver='liblinear')
param_grid = {
    'C': [0.01, 0.1, 1, 10],
    'penalty': ['l1', 'l2']
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(model, param_grid, cv=cv, scoring='accuracy', n_jobs=1, verbose=1)

grid.fit(X_scaled, y)
best_model = grid.best_estimator_
best_params = grid.best_params_
cv_score = grid.best_score_

print("Optimal parameters：", best_params)
print("Cross-validation accuracy：{:.2f}%".format(cv_score * 100))

y_pred = best_model.predict(X_scaled[:1000])
print("Accuracy：{:.2f}%".format(accuracy_score(y[:1000], y_pred) * 100))
print("classification_report:")
print(classification_report(y[:1000], y_pred, target_names=['Home Win', 'Away Win']))
joblib.dump(best_model, "../models/pre_match_result_model.pkl")
joblib.dump(scaler, "../models/pre_match_result_scaler.pkl")
# print(classification_report(y[:1000], y_pred, target_names=['Home Win', 'Draw', 'Away Win']))
