# pages/dashboard.py
"""Dashboard page for the Ticket‑to‑FAQ app.
Displays KPI cards and analytics charts.
"""
import os
import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from dotenv import load_dotenv
from backend.db import get_all_closed_tickets
from backend.processing import vectorize, auto_cluster
from collections import Counter

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "tickets.db")

def get_metrics():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Total tickets
    cur.execute("SELECT COUNT(*) FROM tickets")
    total = cur.fetchone()[0]
    # Closed tickets
    cur.execute("SELECT COUNT(*) FROM tickets WHERE status='closed'")
    closed = cur.fetchone()[0]
    
    # Calculate clusters dynamically from closed tickets
    df_closed = get_all_closed_tickets()
    if not df_closed.empty:
        try:
            tfidf = vectorize(df_closed)
            _, clusters = auto_cluster(tfidf)
        except Exception:
            clusters = 0
    else:
        clusters = 0
        
    # FAQs generated (drafts)
    cur.execute("SELECT COUNT(*) FROM faq_drafts")
    drafts = cur.fetchone()[0]
    # Pending reviews
    cur.execute("SELECT COUNT(*) FROM faq_drafts WHERE status='pending'")
    pending = cur.fetchone()[0]
    # Published FAQs
    cur.execute("SELECT COUNT(*) FROM published_faqs")
    published = cur.fetchone()[0]
    conn.close()
    
    return {
        "total": total,
        "closed": closed,
        "clusters": clusters,
        "drafts": drafts,
        "pending": pending,
        "published": published,
    }

def ticket_status_chart():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT status, COUNT(*) as count FROM tickets GROUP BY status", conn)
    conn.close()
    chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="status", type="nominal", legend=None),
        tooltip=["status", "count"]
    ).properties(width=300, height=300)
    return chart

def get_cluster_data():
    df = get_all_closed_tickets()
    if df.empty:
        return pd.DataFrame(), []
    try:
        tfidf = vectorize(df)
        labels, k = auto_cluster(tfidf)
        df['cluster_id'] = labels
        
        # Group by cluster and count
        counts = df.groupby('cluster_id').size().reset_index(name='count')
        counts = counts.sort_values(by='count', ascending=False)
        
        # Generate names based on top terms
        issues_list = []
        cluster_names = {}
        for _, row in counts.iterrows():
            cid = row['cluster_id']
            cnt = row['count']
            
            # Simple keyword extraction
            cluster_text = " ".join(df[df['cluster_id'] == cid]['issue'].str.lower().tolist())
            words = [w for w in cluster_text.split() if len(w) > 3 and w not in ['issue', 'ticket', 'problem', 'error', 'with', 'this', 'that', 'please', 'help']]
            top_words = [item[0] for item in Counter(words).most_common(2)]
            name = " & ".join(top_words).title() if top_words else f"Cluster {cid + 1}"
            
            issues_list.append({"name": f"{name} Issues", "count": cnt})
            cluster_names[cid] = f"{name} Issues"
            
        df['cluster_name'] = df['cluster_id'].map(cluster_names)
        dist_df = df.groupby('cluster_name').size().reset_index(name='count')
        
        return dist_df, issues_list
    except Exception:
        return pd.DataFrame(), []

def cluster_distribution_chart(dist_df):
    if dist_df.empty:
        return None
    chart = alt.Chart(dist_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("cluster_name:N", title="Cluster Type", sort="-y"),
        y=alt.Y("count:Q", title="Ticket Count"),
        color=alt.Color("cluster_name:N", scale=alt.Scale(scheme="darkmulti"), legend=None),
        tooltip=["cluster_name", "count"]
    ).properties(height=300)
    return chart

def top_issues_chart(top_issues):
    if not top_issues:
        return None
    df_issues = pd.DataFrame(top_issues)
    chart = alt.Chart(df_issues).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
        x=alt.X("count:Q", title="Ticket Count"),
        y=alt.Y("name:N", title="Issue Type", sort="-x"),
        color=alt.Color("name:N", scale=alt.Scale(scheme="purpleorange"), legend=None),
        tooltip=["name", "count"]
    ).properties(height=300)
    return chart

def render():
    st.title("📊 Pipeline Overview")
    st.write("End‑to‑end view of Ticket‑to‑FAQ pipeline")
    
    # Try/except block to handle case where DB tables aren't created/populated yet
    try:
        metrics = get_metrics()
    except sqlite3.OperationalError:
        st.warning("⚠️ Database tables are not initialized yet. Please initialize the database and load some tickets.")
        return

    # KPI cards - Premium rounded cards with soft shadows
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <span style="font-size: 2.2rem; font-weight: bold; color: #ff5e5e;">{metrics["total"]}</span>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 5px;">Total Tickets</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <span style="font-size: 2.2rem; font-weight: bold; color: #00cc66;">{metrics["closed"]}</span>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 5px;">Closed Tickets</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <span style="font-size: 2.2rem; font-weight: bold; color: #4e44ff;">{metrics["clusters"]}</span>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 5px;">Clusters</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <span style="font-size: 2.2rem; font-weight: bold; color: #ffa500;">{metrics["drafts"]}</span>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 5px;">FAQ Drafts</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <span style="font-size: 2.2rem; font-weight: bold; color: #00bcd4;">{metrics["published"]}</span>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 5px;">Published FAQs</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    # Load cluster details dynamically
    dist_df, top_issues = get_cluster_data()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🔥 Top Recurring Issues")
        chart_issues = top_issues_chart(top_issues)
        if chart_issues is not None:
            st.altair_chart(chart_issues, use_container_width=True)
        else:
            st.info("No issue data available.")
            
    with col_right:
        st.subheader("🕸️ Cluster Distribution")
        chart_dist = cluster_distribution_chart(dist_df)
        if chart_dist is not None:
            st.altair_chart(chart_dist, use_container_width=True)
        else:
            st.info("No clusters available yet.")
            
    st.markdown("---")
    
    # Workflow Visualization and Funnel Progress
    col_flow, col_tracker = st.columns([2, 1])
    
    with col_flow:
        st.subheader("🔄 Pipeline Workflow")
        st.markdown(
            """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; padding: 1.5rem; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #ff4b4b;">👤 Customer Portal</div>
                <div style="color: #6e68ff; font-weight: bold; font-size: 1.2rem;">↓</div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #ffa500;">🎧 Support Agent Resolution</div>
                <div style="color: #6e68ff; font-weight: bold; font-size: 1.2rem;">↓</div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #00cc66;">🗄️ Closed Ticket Database</div>
                <div style="color: #6e68ff; font-weight: bold; font-size: 1.2rem;">↓</div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #4e44ff;">🕸️ ML Clustering (Scikit-learn)</div>
                <div style="color: #6e68ff; font-weight: bold; font-size: 1.2rem;">↓</div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #ffa500;">🤖 Gemini AI FAQ Generation</div>
                <div style="color: #6e68ff; font-weight: bold; font-size: 1.2rem;">↓</div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #6e68ff;">🛡️ Admin Review</div>
                <div style="color: #6e68ff; font-weight: bold; font-size: 1.2rem;">↓</div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold; border-left: 4px solid #00bcd4;">📚 Published Knowledge Base</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_tracker:
        st.subheader("📈 Pipeline Funnel")
        # Compute active open tickets count
        conn = sqlite3.connect(DB_PATH)
        open_count = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='open'").fetchone()[0]
        conn.close()
        
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); padding: 1.5rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
                    <span style="color:#aaa;">Tickets Raised (Open)</span>
                    <strong style="color:#ff4b4b; font-size:1.1rem;">{open_count}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
                    <span style="color:#aaa;">Tickets Closed</span>
                    <strong style="color:#00cc66; font-size:1.1rem;">{metrics["closed"]}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
                    <span style="color:#aaa;">Clusters Generated</span>
                    <strong style="color:#4e44ff; font-size:1.1rem;">{metrics["clusters"]}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
                    <span style="color:#aaa;">FAQ Drafts Created</span>
                    <strong style="color:#ffa500; font-size:1.1rem;">{metrics["drafts"]}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <span style="color:#aaa;">FAQs Published</span>
                    <strong style="color:#00bcd4; font-size:1.1rem;">{metrics["published"]}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    render()

