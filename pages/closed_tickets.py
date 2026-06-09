# pages/closed_tickets.py
"""Page displaying closed tickets with search functionality."""
import streamlit as st
import pandas as pd
from backend.db import get_all_closed_tickets

def render():
    st.title("🗄️ Closed Tickets")
    st.write("All resolved tickets ready for knowledge extraction")
    
    # Info Banner
    st.markdown(
        """
        <div style="background-color: rgba(78, 68, 255, 0.1); border: 1px solid rgba(78, 68, 255, 0.3); border-radius: 8px; padding: 0.8rem 1.2rem; color: #a19dff; margin-bottom: 1.5rem; display: flex; align-items: center;">
            <span style="margin-right: 0.5rem; font-weight: bold;">ℹ️</span>
            <span>These closed tickets will be used for clustering and FAQ generation.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    df = get_all_closed_tickets()
    if df.empty:
        st.info("No closed tickets found.")
        return
        
    # Search box
    search = st.text_input("🔍 Search closed tickets (by issue or resolution)", "")
    if search:
        mask = df['issue'].str.contains(search, case=False, na=False) | df['resolution'].str.contains(search, case=False, na=False)
        df = df[mask]
        
    # Custom Table Header
    col_id, col_subj, col_res, col_closed, col_status = st.columns([1.2, 2.5, 3.5, 2.2, 1.2])
    col_id.markdown("**Ticket ID**")
    col_subj.markdown("**Issue**")
    col_res.markdown("**Resolution**")
    col_closed.markdown("**Closed Date**")
    col_status.markdown("**Status**")
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 0.5rem 0;'>", unsafe_allow_html=True)
    
    for _, row in df.iterrows():
        t_id = row['ticket_id']
        issue_full = row['issue']
        res = row['resolution']
        closed_at = row['closed_at'] if row['closed_at'] else "N/A"
        
        c_id, c_subj, c_res, c_closed, c_status = st.columns([1.2, 2.5, 3.5, 2.2, 1.2])
        c_id.write(f"TKT-{t_id}")
        c_subj.write(issue_full)
        c_res.write(res)
        c_closed.write(closed_at)
        c_status.markdown(
            """
            <span style="background-color: rgba(0, 204, 102, 0.15); color: #00cc66; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; border: 1px solid rgba(0,204,102,0.3);">Closed</span>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 0.4rem 0;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    render()
