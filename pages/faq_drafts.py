# pages/faq_drafts.py
"""Page displaying FAQ drafts with status filtering and edit options."""
import streamlit as st
import pandas as pd
from backend.db import get_faq_drafts_by_status, update_faq_draft

from backend.db import get_faq_drafts_by_status, update_faq_draft, publish_faq

def render():
    st.title("🗒️ FAQ Drafts")
    status = st.selectbox("Filter by Status", ["pending", "approved", "rejected"])
    df = get_faq_drafts_by_status(status)
    
    if df.empty:
        st.info(f"No FAQ drafts with status '{status}' found.")
        return

    st.write(f"Found {len(df)} draft(s) with status **{status}**.")
    
    for _, row in df.iterrows():
        faq_id = row['faq_id']
        
        # Premium glass-morphism style card container
        st.markdown(
            f"""
            <div class="card" style="margin-bottom: 1rem;">
                <h4 style="color: #6e68ff; margin: 0 0 0.5rem 0;">FAQ Draft #{faq_id} (Cluster {row['cluster_id']})</h4>
                <p><strong>Q:</strong> {row['question']}</p>
                <p><strong>A:</strong> {row['answer']}</p>
                <span style="font-size: 0.85rem; color: #aaa;">Source Tickets: {row['source_ticket_ids']}</span> | 
                <span style="font-size: 0.85rem; font-weight: bold; color: #a19dff;">Confidence: {row['confidence_score']}%</span> | 
                <span style="font-size: 0.85rem; font-weight: bold; color: {'#ffa500' if status=='pending' else '#00cc66' if status=='approved' else '#ff3333'};">Status: {row['status'].upper()}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action buttons row
        col1, col2, col3, col4 = st.columns([1, 1, 1, 4])
        
        # Toggle edit block in session state
        edit_key = f"editing_{faq_id}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False
            
        with col1:
            if status == "pending":
                if st.button("✅ Approve", key=f"app_{faq_id}"):
                    # Update status and move to published table
                    publish_faq(faq_id)
                    st.success(f"FAQ #{faq_id} approved & published!")
                    st.rerun()
            else:
                st.write("")
                
        with col2:
            if status == "pending":
                if st.button("❌ Reject", key=f"rej_{faq_id}"):
                    update_faq_draft(faq_id, status="rejected")
                    st.warning(f"FAQ #{faq_id} rejected.")
                    st.rerun()
            else:
                st.write("")
                
        with col3:
            if st.button("✏️ Edit", key=f"edt_{faq_id}"):
                st.session_state[edit_key] = not st.session_state[edit_key]
                st.rerun()
                
        # Inline edit block
        if st.session_state[edit_key]:
            with st.container():
                st.markdown("**Edit Draft Details**")
                new_q = st.text_input("Edit Question", value=row['question'], key=f"edit_q_{faq_id}")
                new_a = st.text_area("Edit Answer", value=row['answer'], key=f"edit_a_{faq_id}", height=120)
                if st.button("💾 Save Changes", key=f"save_{faq_id}"):
                    update_faq_draft(faq_id, question=new_q, answer=new_a)
                    st.session_state[edit_key] = False
                    st.success("Draft saved successfully.")
                    st.rerun()
        
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 1.5rem 0;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    render()
