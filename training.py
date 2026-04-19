import pandas as pd
import matplotlib.pyplot as plt
import time
import os

def analyze_churn(filepath):

    # ---------- LOAD DATA ----------
    df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)

    if 'Churn' not in df.columns:
        return "Dataset must contain 'Churn' column"

    # ---------- CLEAN ----------
    df = df.dropna()
    df['Churn'] = df['Churn'].replace({'Yes': 1, 'No': 0})

    total = len(df)
    churn_count = int(df['Churn'].sum())
    non_churn = total - churn_count
    churn_rate = round((churn_count / total) * 100, 2)

    # ---------- UNIQUE IMAGE NAMES (FIX CACHE ISSUE) ----------
    timestamp = str(int(time.time()))
    bar_path = f"static/bar_{timestamp}.png"
    pie_path = f"static/pie_{timestamp}.png"

    # ---------- BAR CHART ----------
    plt.figure()
    plt.bar(['Churn', 'Not Churn'], [churn_count, non_churn])
    plt.title("Churn vs Non-Churn")
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    # ---------- PIE CHART ----------
    plt.figure()
    plt.pie([churn_count, non_churn],
            labels=['Churn', 'Not Churn'],
            autopct='%1.1f%%')
    plt.title("Churn Distribution")
    plt.tight_layout()
    plt.savefig(pie_path)
    plt.close()

    # ---------- FINAL OUTPUT ----------
    result = f"""
    <b>📊 Final Summary</b><br><br>

    Total Customers: {total}<br>
    Churn Customers: {churn_count}<br>
    Non-Churn Customers: {non_churn}<br>
    Churn Rate: {churn_rate}%<br><br>

    <b>📊 Charts</b><br><br>

    <img src="/{bar_path}" width="350"><br><br>
    <img src="/{pie_path}" width="350">
    """

    return result