# Superstore Sales Executive Dashboard
# 3-Page Interactive HTML Report
# Data: Sample Superstore (2015–2018)
# Author: [Eduardo Villalobos]
# Purpose: Portfolio Project - Data Visualization & Analysis

import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
from datetime import datetime

print("Superstore Executive Dashboard")
print("Loading data...")

path = input("Please drag and drop your train.csv file here: ").strip().strip('"')
df = pd.read_csv(path)

# Handle mixed date formats
df["Order Date"] = pd.to_datetime(df["Order Date"], format='%d/%m/%Y', errors='coerce')
df["Order Date"] = df["Order Date"].fillna(pd.to_datetime(df["Order Date"], format='%m/%d/%Y', errors='coerce'))
df = df.dropna(subset=["Order Date", "Sales"]).copy()

df["Year"] = df["Order Date"].dt.year
df["Quarter"] = df["Order Date"].dt.quarter

# Key metrics
total_sales = df["Sales"].sum()
total_orders = df["Order ID"].nunique()
avg_order_value = total_sales / total_orders  # ← fixed variable name
top_region = df.groupby("Region")["Sales"].sum().idxmax()

print(f"Analysis complete: ${total_sales:,.0f} in sales across {total_orders:,} orders")

def fig_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# Page 1: Overview
fig = plt.figure(figsize=(18, 10))

ax1 = fig.add_subplot(1, 2, 1)
regions = df.groupby("Region")["Sales"].sum().reindex(["West", "East", "Central", "South"])
colors = ["#6366f1", "#10b981", "#f59e0b", "#ef4444"]
bars = ax1.bar(regions.index, regions.values, color=colors, edgecolor="black", linewidth=1.5, width=0.6)
ax1.set_title("Sales by Region", fontsize=22, fontweight="bold", color="#1e293b", pad=20)
ax1.tick_params(left=False, labelleft=False, bottom=True, labelbottom=True)
ax1.set_xticklabels(regions.index, fontsize=14, fontweight="bold", color="black")
ax1.grid(False)
for spine in ['left', 'top', 'right']:
    ax1.spines[spine].set_visible(False)
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height + height*0.02,
             f"${height:,.0f}", ha="center", va="bottom", fontweight="bold", fontsize=14, color="black")

ax2 = fig.add_subplot(1, 2, 2)
quarterly = df.groupby(["Year", "Quarter"])["Sales"].sum().unstack(fill_value=0)
quarterly = quarterly.reindex(columns=[1,2,3,4], fill_value=0)
yearly_totals = quarterly.sum(axis=1)
x_labels = quarterly.index.astype(str)

scale = 0.78
bottom = [0] * len(quarterly)
for i, q in enumerate([1,2,3,4]):
    values = quarterly[q].values * scale
    ax2.bar(x_labels, values, bottom=bottom, color=["#6366f1","#10b981","#f59e0b","#ef4444"][i], label=f"Q{q}")
    for j, val in enumerate(quarterly[q]):
        if val > 10000:
            ax2.text(x_labels[j], bottom[j] + (val*scale)/2, f"${val:,.0f}",
                     ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    bottom = [a + b for a, b in zip(bottom, values)]

for year, total in yearly_totals.items():
    idx = list(quarterly.index).index(year)
    ax2.text(idx, total * scale * 1.02, f"${total:,.0f}",
             ha="center", va="bottom", fontsize=18, fontweight="bold", color="black")

ax2.set_title("Quarterly Revenue by Year", fontsize=22, fontweight="bold", color="#1e293b", pad=20)
ax2.legend(title="Quarter", loc="upper left")
ax2.grid(False)
ax2.tick_params(left=False, labelleft=False, bottom=True, labelbottom=True)
ax2.set_xticklabels(x_labels, fontweight="bold", fontsize=14, color="black")

plt.subplots_adjust(top=0.88, wspace=0.3)
img_overview = fig_to_base64()
plt.close()

# Page 2: Category Analysis
fig = plt.figure(figsize=(18, 10))
ax1 = fig.add_subplot(1, 2, 1)
cat_sales = df.groupby("Category")["Sales"].sum()
bars = ax1.bar(cat_sales.index, cat_sales.values, color=["#6366f1", "#10b981", "#f59e0b"], edgecolor="black")
ax1.set_title("Sales by Category", fontsize=22, fontweight="bold", color="#1e293b")
ax1.tick_params(left=False, labelleft=False)
for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, h/2, f"${h:,.0f}",
             ha="center", va="center", color="white", fontsize=16, fontweight="bold")

ax2 = fig.add_subplot(1, 2, 2)
top_sub = df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False).head(10)
bars = ax2.barh(range(len(top_sub)), top_sub.values[::-1], color="#6366f1", edgecolor="black")
ax2.set_title("Top 10 Sub-Categories by Sales", fontsize=22, fontweight="bold", color="#1e293b")
ax2.set_yticks(range(len(top_sub)))
ax2.set_yticklabels(top_sub.index[::-1], fontsize=12)
ax2.tick_params(bottom=False, labelbottom=False)
for i, bar in enumerate(bars):
    w = bar.get_width()
    ax2.text(w/2, bar.get_y() + bar.get_height()/2, f"${top_sub.values[::-1][i]:,.0f}",
             ha="center", va="center", color="white", fontsize=12, fontweight="bold")

plt.subplots_adjust(wspace=0.4)
img_categories = fig_to_base64()
plt.close()

# Page 3: Customer Insights
fig = plt.figure(figsize=(18, 10))
ax1 = fig.add_subplot(1, 2, 1)
segment_sales = df.groupby("Segment")["Sales"].sum()
ax1.pie(segment_sales.values, labels=segment_sales.index, autopct='%1.1f%%',
        colors=["#6366f1", "#f59e0b", "#10b981"], textprops={'fontsize': 14, 'fontweight': 'bold'})
ax1.set_title("Sales by Customer Segment", fontsize=22, fontweight="bold", color="#1e293b")

ax2 = fig.add_subplot(1, 2, 2)
top_customers = df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(10)
bars = ax2.barh(range(len(top_customers)), top_customers.values[::-1], color="#6366f1", edgecolor="black")
ax2.set_title("Top 10 Customers by Sales", fontsize=22, fontweight="bold", color="#1e293b")
ax2.set_yticks(range(len(top_customers)))
ax2.set_yticklabels(top_customers.index[::-1], fontsize=11)
ax2.tick_params(bottom=False, labelbottom=False)
for i, bar in enumerate(bars):
    w = bar.get_width()
    ax2.text(w/2, bar.get_y() + bar.get_height()/2, f"${top_customers.values[::-1][i]:,.0f}",
             ha="center", va="center", color="white", fontsize=12, fontweight="bold")

plt.subplots_adjust(wspace=0.4)
img_customers = fig_to_base64()
plt.close()

# Final HTML
html_report = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Superstore Sales Executive Dashboard</title>
    <style>
        body {{margin:0;background:#f1f5f9;font-family:'Segoe UI',sans-serif}}
        .header {{background:#4f46e5;color:white;padding:80px;text-align:center}}
        h1 {{font-size:52px;margin:0}}
        .subtitle {{font-size:28px;margin:10px 0;opacity:0.9}}
        .tab {{background:#4338ca;padding:15px;text-align:center}}
        .tab button {{background:none;border:none;color:white;padding:14px 32px;font-size:18px;cursor:pointer;transition:0.3s;border-radius:8px}}
        .tab button:hover {{background:#312e81}}
        .tab button.active {{background:#1e1b4b;font-weight:bold}}
        .content {{display:none;padding:40px;background:white;min-height:100vh}}
        .content.active {{display:block}}
        .metrics {{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px;margin:50px 0}}
        .metric {{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:40px;border-radius:20px;text-align:center}}
        big {{font-size:44px;font-weight:bold;display:block;margin-bottom:8px}}
        small {{font-size:18px}}
        img {{max-width:100%;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.3);margin:30px 0}}
        .footer {{text-align:center;padding:40px;color:#666;font-size:14px}}
    </style>
</head>
<body>

<div class="header">
    <h1>Superstore Executive Dashboard</h1>
    <div class="subtitle">2015 – 2018 • Sales Performance Analysis</div>
</div>

<div class="tab">
    <button class="active" onclick="openTab('overview')">Overview</button>
    <button onclick="openTab('categories')">Categories</button>
    <button onclick="openTab('customers')">Customers</button>
</div>

<div id="overview" class="content active">
    <div class="metrics">
        <div class="metric"><big>${total_sales:,.0f}</big><small>Total Revenue</small></div>
        <div class="metric"><big>{total_orders:,}</big><small>Unique Orders</small></div>
        <div class="metric"><big>${avg_order_value:,.0f}</big><small>Avg Order Value</small></div>
        <div class="metric"><big>{top_region}</big><small>Top Region</small></div>
    </div>
    <img src="data:image/png;base64,{img_overview}">
</div>

<div id="categories" class="content">
    <h2 style="text-align:center;color:#4f46e5;padding:20px;font-size:28px">Category & Sub-Category Performance</h2>
    <img src="data:image/png;base64,{img_categories}">
</div>

<div id="customers" class="content">
    <h2 style="text-align:center;color:#4f46e5;padding:20px;font-size:28px">Customer Insights</h2>
    <img src="data:image/png;base64,{img_customers}">
</div>

<div class="footer">
    Superstore Sales Analysis • Generated on {datetime.now():%B %d, %Y}
</div>

<script>
function openTab(tabName) {{
    document.querySelectorAll('.content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}}
</script>

</body>
</html>'''

output_path = os.path.expanduser("~/Downloads/Superstore_Executive_Dashboard.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_report)

os.startfile(output_path)
print(f"\nExecutive dashboard generated successfully!")
print(f"Saved to: {output_path}")
print("Ready for portfolio and professional use.")