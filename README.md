# 💳 SmartSpend Intelligence

**An AI-powered financial analytics platform — from raw transactions to real-time fraud detection, customer intelligence, and natural language insights.**

🔗 **Live Demo:** [smartspend-intelligence](https://fqwcwwzrrtyzbdsosjh6q9.streamlit.app/)
📦 **Tech Stack:** Python · SQL · Scikit-learn · Streamlit · Plotly · Pandas · Git

---

## 📌 Overview

SmartSpend Intelligence simulates a real-world fintech analytics stack — the kind of system used internally by companies like Amex, CRED, and Razorpay to monitor spending behavior, catch fraud, and understand customer value.

The platform was built end-to-end: from a synthetic 500K-row transaction dataset, through feature engineering and machine learning, to a fully interactive, deployed dashboard with a natural-language query agent.

---

## 🧩 What It Does

### 1. Data Pipeline
Generated and engineered a realistic transaction dataset — 500,000+ records across 10,000 users, 10 spending categories, and 50 Indian merchants (UPI, Credit Card, Debit Card, Net Banking) — with controlled fraud injection (1.5% rate) to mimic real-world class imbalance.

### 2. Fraud Detection Engine
Built an unsupervised anomaly detection system using **Isolation Forest**, since real-world fraud data is rarely labeled at scale.

- **ROC-AUC: 0.997**
- **83% recall** — catches 8 out of every 10 fraud cases
- **₹49.6 Crore** in fraudulent transactions flagged
- Customer friction cost (false positives) kept under **₹1 Lakh**
- Every prediction is framed with a business cost lens: false negatives = revenue loss, false positives = customer friction

### 3. Customer Segmentation (RFM + K-Means)
Segmented all users into 5 actionable personas using Recency, Frequency, and Monetary analysis combined with K-Means clustering:

| Persona | Users | Avg Spend | Strategy |
|---|---|---|---|
| Champions | 1,250 | ₹2.37L | Retain & upsell |
| Loyal Customers | 1,501 | ₹1.75L | Increase frequency |
| At Risk | 1,261 | ₹66K | Win-back campaign |
| Occasional | 3,003 | ₹84K | Category-targeted offers |
| Dormant | 2,985 | ₹53K | Reactivation push |

### 4. NLP Analytics Agent
A natural-language query interface — ask a question in plain English, get back a generated SQL query, a results table, and an auto-chart. No SQL knowledge required.

> *"Which merchant has the highest fraud amount?"* → SQL generated → results + chart returned instantly.

### 5. Live Interactive Dashboard
A 5-page Streamlit dashboard covering Overview, Fraud Detection, User Segments, the NLP Agent, and Spending Trends — with dynamic filters by city and category.

---

## 📊 Key Business Insights

- **Dominos** had the highest total fraud exposure (₹1.4Cr across 172 transactions)
- **Surat** recorded the highest fraud volume by city — a non-obvious geographic risk signal
- Fraud peaks consistently around **12 PM, 3 PM, and 8 PM**
- The top 12.5% of users (*Champions*) generate disproportionately high revenue relative to the rest of the base
- Weekday spending (₹75.3Cr) significantly outpaces weekend spending (₹30.1Cr)

---

## 🛠️ Project Structure

```
smartspend/
├── app.py                          # Streamlit dashboard (5 pages)
├── requirements.txt                # Python dependencies
└── data/
    ├── raw_transactions.csv        # Transaction-level data
    ├── users.csv                   # User profiles
    ├── rfm_segments.csv            # RFM scores + persona labels
    ├── transactions_scored.csv     # Transactions with fraud risk scores
    └── high_risk_transactions.csv  # Top flagged transactions
```

---

## ⚙️ Run It Locally

```bash
git clone https://github.com/pahwasavi2-commits/smartspend_intelligence.git
cd smartspend_intelligence
pip install -r requirements.txt
streamlit run app.py
```

---

## 👩‍💻 Built By

**Savi Pahwa**
MCA, Thapar Institute of Engineering and Technology
IEEE Published Researcher — *Smart Education Using Artificial Intelligence*

[LinkedIn](https://linkedin.com/in/savi-pahwa-b575b7378) · [GitHub](https://github.com/pahwasavi2-commits)
