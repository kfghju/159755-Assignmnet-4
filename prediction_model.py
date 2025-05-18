import joblib
import numpy as np

# 加载模型
model = joblib.load("models/trained_model.pkl")

def predict_match_result(team_home, team_away, match_date):
    # 构造输入特征（这里是示例）
    features = build_features(team_home, team_away, match_date)
    probabilities = model.predict_proba([features])[0]

    outcome_index = np.argmax(probabilities)
    outcome_map = {0: "Home Win", 1: "Draw", 2: "Away Win"}
    return outcome_map[outcome_index], {
        "Home Win": probabilities[0],
        "Draw": probabilities[1],
        "Away Win": probabilities[2]
    }

def build_features(team_home, team_away, match_date):
    # 应根据你的特征工程构建，示意：
    return [
        get_recent_win_rate(team_home),
        get_recent_win_rate(team_away),
        get_avg_goals(team_home),
        get_avg_goals(team_away),
        get_home_advantage(team_home)
    ]
