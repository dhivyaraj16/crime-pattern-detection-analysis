df=pd.read_csv("crime_dataset_2014-2023.csv")
x=df[["YEAR", "STATE/UT", "DISTRICT"]]
y=df["MURDER"]

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor()
model.fit(X_train, y_train)


import joblib
joblib.dump(model, "crime_model.pkl")