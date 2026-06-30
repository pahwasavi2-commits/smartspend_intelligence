import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SmartSpend Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #e2e8f0;
        margin: 20px 0 10px;
        border-left: 4px solid #534AB7;
        padding-left: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df_txn    = pd.read_csv('data/raw_transactions.csv', parse_dates=['txn_date'])
    df_users  = pd.read_csv('data/users.csv')
    df_rfm    = pd.read_csv('data/rfm_segments.csv')
    df_scored = pd.read_csv('data/transactions_scored.csv')

    df_txn['txn_month']   = df_txn['txn_date'].dt.to_period('M').astype(str)
    df_txn['txn_hour']    = df_txn['txn_date'].dt.hour
    df_txn['day_of_week'] = df_txn['txn_date'].dt.day_name()
    df_txn['is_weekend']  = df_txn['txn_date'].dt.dayofweek.isin([5, 6])
    return df_txn, df_users, df_rfm, df_scored

df_txn, df_users, df_rfm, df_scored = load_data()
df_success = df_txn[df_txn['status'] == 'success']

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💳 SmartSpend")
    st.markdown("### Intelligence Platform")
    st.markdown("---")

    page = st.selectbox(
        "Navigate",
        ["🏠 Overview", "🚨 Fraud Detection", "👥 User Segments", "🤖 NLP Agent", "📈 Trends"]
    )

    st.markdown("---")
    st.markdown("**Filters**")

    cities = ['All'] + sorted(df_txn['city'].unique().tolist())
    selected_city = st.selectbox("City", cities)

    categories = ['All'] + sorted(df_txn['category'].unique().tolist())
    selected_cat = st.selectbox("Category", categories)

    st.markdown("---")
    st.markdown("**Built by Savi Pahwa**")
    st.markdown("MCA — Thapar Institute")
    st.markdown("IEEE Published Researcher")

# apply filters
df_f = df_success.copy()
if selected_city != 'All':
    df_f = df_f[df_f['city'] == selected_city]
if selected_cat != 'All':
    df_f = df_f[df_f['category'] == selected_cat]

COLORS = {
    'Champions':       '#7C3AED',
    'Loyal Customers': '#059669',
    'At Risk':         '#DC2626',
    'Occasional':      '#D97706',
    'Dormant':         '#6B7280'
}

# ─────────────────────────────────────────────
# PAGE 1 — OVERVIEW
# ─────────────────────────────────────────────
if page == "🏠 Overview":
    st.markdown("# 💳 SmartSpend Intelligence Dashboard")
    st.markdown("**AI-powered financial analytics — 500K+ transactions**")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Transactions", f"{len(df_txn):,}")
    with col2:
        st.metric("Total Users", f"{df_txn['user_id'].nunique():,}")
    with col3:
        st.metric("Total Spend", f"₹{df_success['amount'].sum()/1e7:.1f}Cr")
    with col4:
        st.metric("Fraud Rate", f"{df_txn['is_fraud'].mean()*100:.2f}%")
    with col5:
        st.metric("Avg Transaction", f"₹{df_success['amount'].mean():,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Spend by Category</p>', unsafe_allow_html=True)
        cat_spend = df_f.groupby('category')['amount'].sum().reset_index()
        cat_spend.columns = ['Category', 'Total Spend']
        cat_spend = cat_spend.sort_values('Total Spend', ascending=True)
        fig = px.bar(cat_spend, x='Total Spend', y='Category',
                     orientation='h', color='Total Spend',
                     color_continuous_scale='Purples')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Payment Mode Split</p>', unsafe_allow_html=True)
        pm = df_f['payment_mode'].value_counts().reset_index()
        pm.columns = ['Payment Mode', 'Count']
        fig = px.pie(pm, values='Count', names='Payment Mode',
                     color_discrete_sequence=['#7C3AED','#059669','#DC2626','#D97706'],
                     hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=350)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Monthly Spend Trend</p>', unsafe_allow_html=True)
        monthly = df_f.groupby('txn_month')['amount'].sum().reset_index()
        monthly.columns = ['Month', 'Total Spend']
        fig = px.line(monthly, x='Month', y='Total Spend',
                      color_discrete_sequence=['#7C3AED'], markers=True)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=300)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Top 10 Merchants</p>', unsafe_allow_html=True)
        top_m = df_f.groupby('merchant')['amount'].sum().nlargest(10).reset_index()
        top_m.columns = ['Merchant', 'Revenue']
        fig = px.bar(top_m, x='Merchant', y='Revenue',
                     color='Revenue', color_continuous_scale='Purples')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=300)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE 2 — FRAUD DETECTION
# ─────────────────────────────────────────────
elif page == "🚨 Fraud Detection":
    st.markdown("# 🚨 Fraud Detection Engine")
    st.markdown("**Isolation Forest — ROC-AUC: 0.9974**")
    st.markdown("---")

    fraud_df = df_txn[df_txn['is_fraud'] == 1]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Fraud Txns", f"{len(fraud_df):,}")
    with col2:
        st.metric("Fraud Amount", f"₹{fraud_df['amount'].sum()/1e7:.1f}Cr")
    with col3:
        st.metric("Fraud Rate", f"{df_txn['is_fraud'].mean()*100:.2f}%")
    with col4:
        st.metric("Avg Fraud Amount", f"₹{fraud_df['amount'].mean():,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Fraud by City</p>', unsafe_allow_html=True)
        city_fraud = fraud_df.groupby('city').agg(
            fraud_count=('txn_id', 'count'),
            fraud_amount=('amount', 'sum')
        ).reset_index().sort_values('fraud_amount', ascending=False)
        fig = px.bar(city_fraud, x='city', y='fraud_amount',
                     color='fraud_amount', color_continuous_scale='Reds')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Fraud by Hour</p>', unsafe_allow_html=True)
        hour_fraud = fraud_df.groupby('txn_hour').size().reset_index()
        hour_fraud.columns = ['Hour', 'Fraud Count']
        fig = px.bar(hour_fraud, x='Hour', y='Fraud Count',
                     color='Fraud Count', color_continuous_scale='Reds')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Fraud Rate by Category</p>', unsafe_allow_html=True)
        cat_fraud = df_txn.groupby('category').agg(
            fraud_rate=('is_fraud', 'mean')
        ).reset_index().sort_values('fraud_rate', ascending=False)
        cat_fraud['fraud_rate'] = (cat_fraud['fraud_rate'] * 100).round(2)
        fig = px.bar(cat_fraud, x='category', y='fraud_rate',
                     color='fraud_rate', color_continuous_scale='Reds')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=320)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Top Fraud Merchants</p>', unsafe_allow_html=True)
        merch_fraud = fraud_df.groupby('merchant')['amount'].sum().nlargest(10).reset_index()
        merch_fraud.columns = ['Merchant', 'Fraud Amount']
        fig = px.bar(merch_fraud, x='Merchant', y='Fraud Amount',
                     color='Fraud Amount', color_continuous_scale='Reds')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=320)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">High Risk Transactions</p>', unsafe_allow_html=True)
    high_risk = fraud_df.nlargest(50, 'amount')[
        ['txn_id', 'user_id', 'txn_date', 'amount',
         'merchant', 'city', 'payment_mode']
    ]
    st.dataframe(high_risk, use_container_width=True, height=300)

# ─────────────────────────────────────────────
# PAGE 3 — USER SEGMENTS
# ─────────────────────────────────────────────
elif page == "👥 User Segments":
    st.markdown("# 👥 User Segmentation — RFM + K-Means")
    st.markdown("**5 personas built on Recency, Frequency, Monetary analysis**")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    personas = ['Champions', 'Loyal Customers', 'At Risk', 'Occasional', 'Dormant']
    for col, persona in zip([col1,col2,col3,col4,col5], personas):
        count   = len(df_rfm[df_rfm['persona'] == persona])
        avg_spd = df_rfm[df_rfm['persona'] == persona]['monetary'].mean()
        with col:
            st.metric(persona, f"{count:,}", f"₹{avg_spd/1000:.0f}K avg")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">User Distribution</p>', unsafe_allow_html=True)
        persona_counts = df_rfm['persona'].value_counts().reset_index()
        persona_counts.columns = ['Persona', 'Users']
        fig = px.pie(persona_counts, values='Users', names='Persona',
                     color='Persona', color_discrete_map=COLORS, hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Revenue by Persona</p>', unsafe_allow_html=True)
        rev = df_rfm.groupby('persona')['monetary'].sum().reset_index()
        rev.columns = ['Persona', 'Total Revenue']
        rev = rev.sort_values('Total Revenue', ascending=False)
        fig = px.bar(rev, x='Persona', y='Total Revenue',
                     color='Persona', color_discrete_map=COLORS)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Recency vs Monetary</p>', unsafe_allow_html=True)
        fig = px.scatter(df_rfm, x='recency', y='monetary',
                         color='persona', color_discrete_map=COLORS,
                         opacity=0.6,
                         labels={'recency': 'Days Since Last Txn',
                                 'monetary': 'Total Spend (₹)'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">RFM Summary Table</p>', unsafe_allow_html=True)
        rfm_summary = df_rfm.groupby('persona').agg(
            Users=('user_id', 'count'),
            Avg_Recency=('recency', 'mean'),
            Avg_Frequency=('frequency', 'mean'),
            Avg_Spend=('monetary', 'mean'),
            Total_Revenue=('monetary', 'sum')
        ).round(0).reset_index()
        rfm_summary.columns = ['Persona','Users','Avg Recency',
                                'Avg Freq','Avg Spend ₹','Total Rev ₹']
        st.dataframe(rfm_summary, use_container_width=True, height=350)

# ─────────────────────────────────────────────
# PAGE 4 — NLP AGENT
# ─────────────────────────────────────────────
elif page == "🤖 NLP Agent":
    st.markdown("# 🤖 SmartSpend NLP Analytics Agent")
    st.markdown("**Ask questions in plain English — get SQL + insights instantly**")
    st.markdown("---")

    @st.cache_resource
    def get_db():
        conn = sqlite3.connect('data/smartspend.db', check_same_thread=False)
        df_t = pd.read_csv('data/transactions_scored.csv', parse_dates=['txn_date'])
        df_u = pd.read_csv('data/users.csv')
        df_r = pd.read_csv('data/rfm_segments.csv')
        df_t.to_sql('transactions',  conn, if_exists='replace', index=False)
        df_u.to_sql('users',         conn, if_exists='replace', index=False)
        df_r.to_sql('rfm_segments',  conn, if_exists='replace', index=False)
        return conn

    conn = get_db()

    def generate_sql(question):
        q = question.lower().strip()
        if 'fraud' in q and 'merchant' in q:
            return "SELECT merchant, COUNT(*) as fraud_count, ROUND(SUM(amount),2) as total_fraud_amount FROM transactions WHERE is_fraud=1 GROUP BY merchant ORDER BY total_fraud_amount DESC LIMIT 10"
        elif 'fraud' in q and 'city' in q:
            return "SELECT city, COUNT(*) as fraud_count, ROUND(SUM(amount),2) as total_fraud_amount FROM transactions WHERE is_fraud=1 GROUP BY city ORDER BY total_fraud_amount DESC"
        elif 'fraud' in q and 'hour' in q:
            return "SELECT txn_hour, COUNT(*) as fraud_count FROM transactions WHERE is_fraud=1 GROUP BY txn_hour ORDER BY fraud_count DESC LIMIT 5"
        elif 'fraud' in q and 'category' in q:
            return "SELECT category, SUM(is_fraud) as fraud_txns, ROUND(100.0*SUM(is_fraud)/COUNT(*),2) as fraud_rate_pct FROM transactions GROUP BY category ORDER BY fraud_rate_pct DESC"
        elif 'spend' in q and 'category' in q:
            return "SELECT category, ROUND(SUM(amount),2) as total_spend FROM transactions WHERE status='success' GROUP BY category ORDER BY total_spend DESC"
        elif 'spend' in q and 'city' in q:
            return "SELECT city, ROUND(SUM(amount),2) as total_spend FROM transactions WHERE status='success' GROUP BY city ORDER BY total_spend DESC"
        elif 'weekend' in q:
            return "SELECT CASE WHEN CAST(STRFTIME('%w',txn_date) AS INT) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END as day_type, COUNT(*) as txns, ROUND(SUM(amount),2) as total_spend FROM transactions WHERE status='success' GROUP BY day_type"
        elif 'payment' in q or 'upi' in q:
            return "SELECT payment_mode, COUNT(*) as total_txns, ROUND(SUM(amount),2) as total_spend FROM transactions WHERE status='success' GROUP BY payment_mode ORDER BY total_txns DESC"
        elif 'merchant' in q and 'top' in q:
            return "SELECT merchant, COUNT(*) as total_txns, ROUND(SUM(amount),2) as total_revenue FROM transactions WHERE status='success' GROUP BY merchant ORDER BY total_revenue DESC LIMIT 10"
        elif 'persona' in q or 'segment' in q or 'champion' in q:
            return "SELECT persona, COUNT(*) as users, ROUND(AVG(monetary),2) as avg_spend, ROUND(SUM(monetary),2) as total_revenue FROM rfm_segments GROUP BY persona ORDER BY avg_spend DESC"
        elif 'at risk' in q or 'churn' in q:
            return "SELECT user_id, recency, frequency, ROUND(monetary,2) as total_spend FROM rfm_segments WHERE persona='At Risk' ORDER BY recency DESC LIMIT 20"
        elif 'high value' in q or 'top user' in q:
            return "SELECT r.user_id, u.city, ROUND(r.monetary,2) as total_spend, r.persona FROM rfm_segments r JOIN users u ON r.user_id=u.user_id ORDER BY r.monetary DESC LIMIT 10"
        else:
            return None

    # sample buttons
    st.markdown("**Try these questions:**")
    sample_qs = [
        "Which merchant has highest fraud amount?",
        "What is the spend by category?",
        "Show me fraud by city",
        "Show persona summary",
        "Who are at risk users?",
        "Show payment mode analysis",
        "Weekend vs weekday spend",
        "Show top 10 high value users",
    ]
    cols = st.columns(4)
    for i, q in enumerate(sample_qs):
        if cols[i % 4].button(q, key=f"btn_{i}"):
            st.session_state['nlp_question'] = q

    st.markdown("---")
    question = st.text_input(
        "Or type your own question:",
        value=st.session_state.get('nlp_question', ''),
        placeholder="e.g. Which city has highest fraud amount?"
    )

    if question:
        sql = generate_sql(question)
        if sql:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("**SQL Generated:**")
                st.code(sql, language='sql')
            with col2:
                try:
                    result = pd.read_sql_query(sql, conn)
                    st.markdown("**Result:**")
                    st.dataframe(result, use_container_width=True)
                    num_cols = result.select_dtypes(include=np.number).columns.tolist()
                    cat_cols = result.select_dtypes(include='object').columns.tolist()
                    if cat_cols and num_cols:
                        fig = px.bar(result, x=cat_cols[0], y=num_cols[0],
                                     color_discrete_sequence=['#7C3AED'])
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                          plot_bgcolor='rgba(0,0,0,0)',
                                          font_color='#e2e8f0', height=300)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Try asking about: fraud, spend, category, merchant, persona, or users.")

# ─────────────────────────────────────────────
# PAGE 5 — TRENDS
# ─────────────────────────────────────────────
elif page == "📈 Trends":
    st.markdown("# 📈 Spending Trends & Patterns")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Hourly Transaction Volume</p>', unsafe_allow_html=True)
        hourly = df_txn.groupby('txn_hour').size().reset_index()
        hourly.columns = ['Hour', 'Transactions']
        fig = px.area(hourly, x='Hour', y='Transactions',
                      color_discrete_sequence=['#7C3AED'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Weekend vs Weekday Spend</p>', unsafe_allow_html=True)
        wk = df_success.copy()
        wk['day_type'] = wk['txn_date'].dt.dayofweek.apply(
            lambda x: 'Weekend' if x >= 5 else 'Weekday'
        )
        wd = wk.groupby('day_type')['amount'].sum().reset_index()
        fig = px.pie(wd, values='amount', names='day_type',
                     color_discrete_sequence=['#7C3AED', '#059669'], hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0', height=300)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Day of Week Pattern</p>', unsafe_allow_html=True)
        dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        dow = df_success.groupby('day_of_week')['amount'].sum().reindex(dow_order).reset_index()
        dow.columns = ['Day', 'Total Spend']
        fig = px.bar(dow, x='Day', y='Total Spend',
                     color='Total Spend', color_continuous_scale='Purples')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          coloraxis_showscale=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Income Band Analysis</p>', unsafe_allow_html=True)
        inc = df_txn.merge(df_users[['user_id','income_band']], on='user_id', how='left')
        inc_spend = inc.groupby('income_band')['amount'].agg(['sum','mean']).reset_index()
        inc_spend.columns = ['Income Band', 'Total Spend', 'Avg Spend']
        fig = px.bar(inc_spend, x='Income Band', y='Total Spend',
                     color='Income Band',
                     color_discrete_sequence=['#7C3AED','#059669','#D97706'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#e2e8f0',
                          showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-title">City vs Category Heatmap</p>', unsafe_allow_html=True)
    city_cat = df_f.groupby(['city','category'])['amount'].sum().reset_index()
    pivot = city_cat.pivot(index='city', columns='category', values='amount').fillna(0)
    fig = px.imshow(pivot, color_continuous_scale='Purples',
                    labels=dict(x='Category', y='City', color='Spend'),
                    aspect='auto')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font_color='#e2e8f0', height=400)
    st.plotly_chart(fig, use_container_width=True)