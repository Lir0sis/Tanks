import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

df = pd.read_csv("input.csv", delimiter=",")

df['result'].replace([1, 2], [0, 1], inplace=True)
df['result'].replace(['win', 'lose'], [1, 0], inplace=True)

x = df[["algorithm"]].to_numpy()
y = df["result"].to_numpy()
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1)
model = LogisticRegression()
model.fit(train_x, train_y)

result = model.predict(test_x)

input = np.array([0, 0, 1, 0, 1, 0, 0, 1]).reshape(-1, 1)


prediction = model.predict(input)
prediction_prob = model.predict_proba(input)

for p, pp in zip(prediction, prediction_prob):
    print('prediction:','win' if p == 1 else 'lose' , '\nprobability:',max(pp))