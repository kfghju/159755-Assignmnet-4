# prediction_player_value_model.py

import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


# 模型训练部分（仅首次运行用）
def train_model():
    df = pd.read_csv("data/players_stats.csv")
    df = df[[
        'Full Name', 'Age', 'Height', 'Weight', 'Potential', 'Best position',
        'Value', 'Wage', 'Stamina', 'Dribbling', 'Short passing']]

    # 高度重量处理
    df['Height'] = df['Height'].astype(str).str[:3].astype(int)
    df['Weight'] = df['Weight'].astype(str).str.extract(r'(\d+)').astype(int)

    # 金额清洗
    df['Value'] = df['Value'].replace(0, np.nan)
    df['Wage'] = df['Wage'].replace(0, np.nan)
    df = df.dropna(subset=['Value', 'Wage'])
    df['Value'] = np.log(df['Value'])
    df['Wage'] = np.log(df['Wage'])

    # 技术评分字段清洗
    for col in ['Stamina', 'Dribbling', 'Short passing']:
        df[col] = df[col].astype(str).str.extract(r'(\d+)').astype(float)

    # 特征/标签
    X = df.drop(['Full Name', 'Value', 'Wage'], axis=1)
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].astype(str).str.extract(r'(\d+)').astype(float)
    y = df['Value']

    # 类别处理（如有）
    if 'Best position' in X.columns:
        X = pd.get_dummies(X, columns=['Best position'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    joblib.dump(model, "models/player_value_model.pkl")


# 单个预测入口
def predict_player_value(player_dict):
    model = joblib.load("models/player_value_model.pkl")
    df = pd.DataFrame([player_dict])

    # 技术字段预处理
    for col in ['Stamina', 'Dribbling', 'Short passing']:
        df[col] = df[col].astype(float)

    if 'Best position' in df.columns:
        df = pd.get_dummies(df)

    # 确保与模型一致列
    model_columns = model.feature_names_in_
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[model_columns]

    log_pred = model.predict(df)[0]
    return np.exp(log_pred)  # 将 log 预测结果转换回欧元数值


if __name__ == '__main__':
    train_model()
