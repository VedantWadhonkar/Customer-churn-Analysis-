import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

# STEP 1: Load dataset (your file)
data = pd.read_csv("data/churn.csv")   # change to read_excel if needed

# STEP 2: Select important columns
data = data[['tenure', 'MonthlyCharges', 'Contract', 'Churn']]

# STEP 3: Convert text to numbers
data['Churn'] = data['Churn'].map({'Yes':1, 'No':0})

data['Contract'] = data['Contract'].map({
    'Month-to-month':0,
    'One year':1,
    'Two year':2
})

# STEP 4: Remove missing values
data = data.dropna()

# STEP 5: Split data
X = data[['tenure', 'MonthlyCharges', 'Contract']]
y = data['Churn']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# STEP 6: Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# STEP 7: Save model
pickle.dump(model, open("model.pkl", "wb"))

print("✅ Model trained and saved!")