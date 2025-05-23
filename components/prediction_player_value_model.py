import os
import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


def train_model():
    player_df = pd.read_csv(f"data/player_data/players_stats_07.csv")
    player_df['Year'] = '2007'
    for year in range(8, 10):
        player_df = pd.read_csv(f"data/player_data/players_stats_0{year}.csv")
        player_df['Year'] = year + 2000
        player_df['Year'] = player_df['Year'].astype(str)
        player_df = pd.concat([player_df, player_df], axis=0, ignore_index=True)

    for year in range(10, 26):
        player_df = pd.read_csv(f"data/player_data/players_stats_{year}.csv")
        player_df['Year'] = year + 2000
        player_df['Year'] = player_df['Year'].astype(str)
        player_df = pd.concat([player_df, player_df], axis=0, ignore_index=True)


    player_df['Height'] = player_df['Height'].astype(str).str[:3].astype(int)
    player_df['Weight'] = player_df['Weight'].astype(str).str.extract(r'(\d+)').astype(int)


    player_df['Value'] = player_df['Value'].replace(0, np.nan)
    player_df['Wage'] = player_df['Wage'].replace(0, np.nan)
    player_df = player_df.dropna(subset=['Value', 'Wage'])
    player_df['Value'] = np.log(player_df['Value'])
    player_df['Wage'] = np.log(player_df['Wage'])


    for col in ['Stamina', 'Dribbling', 'Short passing']:
        player_df[col] = player_df[col].astype(str).str.extract(r'(\d+)').astype(float)


    X = player_df.drop(['Full Name', 'Value', 'Wage', 'Year'], axis=1)
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].astype(str).str.extract(r'(\d+)').astype(float)
    y = player_df['Value']


    if 'Best position' in X.columns:
        X = pd.get_dummies(X, columns=['Best position'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    # y_perd = model.predict(X_test)
    # mse = mean_squared_error(y_test, y_perd)
    # print(mse)
    joblib.dump(model, "models/player_value_model.pkl")


def predict_player_value(player_dict):
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, '..', 'models', 'player_value_model.pkl')
    model = joblib.load(data_path)
    df = pd.DataFrame([player_dict])

    for col in ['Stamina', 'Dribbling', 'Short passing']:
        df[col] = df[col].astype(float)

    if 'Best position' in df.columns:
        df = pd.get_dummies(df)

    model_columns = model.feature_names_in_
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[model_columns]

    log_pred = model.predict(df)[0]
    return np.exp(log_pred)


if __name__ == '__main__':
    train_model()

