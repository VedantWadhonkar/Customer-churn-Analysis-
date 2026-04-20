import pandas as pd
import matplotlib.pyplot as plt
import time
import os

def analyze_churn(filepath):

    df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)

    if 'Churn' not in df.columns:
        return "Dataset must contain 'Churn' column"

    df = df.dropna()
    df['Churn'] = df['Churn'].replace({'Yes': 1, 'No': 0})

    total = len(df)
    churn_count = int(df['Churn'].sum())
    non_churn = total - churn_count
    churn_rate = round((churn_count / total) * 100, 2)

    # ✅ AUTO CLEAN OLD IMAGES
    if os.path.exists("static"):
        for file in os.listdir("static"):
            if file.endswith(".png"):
                os.remove(os.path.join("static", file))

    timestamp = str(int(time.time()))

    bar_file = f"bar_{timestamp}.png"
    pie_file = f"pie_{timestamp}.png"

    bar_path = os.path.join("static", bar_file)
    pie_path = os.path.join("static", pie_file)

    # BAR
    plt.figure()
    plt.bar(['Churn', 'Not Churn'], [churn_count, non_churn])
    plt.savefig(bar_path)
    plt.close()

    # PIE
    plt.figure()
    plt.pie([churn_count, non_churn], labels=['Churn', 'Not Churn'], autopct='%1.1f%%')
    plt.savefig(pie_path)
    plt.close()

    return f"""
    <b>Total Customers:</b> {total}<br>
    <b>Churn Customers:</b> {churn_count}<br>
    <b>Churn Rate:</b> {churn_rate}%<br><br>

    <img src="/static/{bar_file}?v={timestamp}" width="350"><br><br>
    <img src="/static/{pie_file}?v={timestamp}" width="350">
    """