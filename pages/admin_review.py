# pages/admin_review.py
"""Page for admin review and publishing workflow. Password‑protected."""
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from backend.db import get_faq_drafts_by_status, update_faq_draft, publish_faq

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def render():
    st.title("🛡️ Admin Review Portal")
    
    # Simple password protection
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
        
    if not st.session_state["admin_authenticated"]:
        pwd_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Authenticate"):
            if pwd_input == ADMIN_PASSWORD:
                st.session_state["admin_authenticated"] = True
                st.success("Successfully authenticated!")
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
        return

    # Logout button
    if st.sidebar.button("Logout Admin"):
        st.session_state["admin_authenticated"] = False
        st.rerun()

    # Get pending drafts
    pending_df = get_faq_drafts_by_status("pending")
    
    if pending_df.empty:
        st.info("No pending FAQ drafts to review.")
        return

    st.subheader(f"Pending FAQ Drafts ({len(pending_df)})")
    
    # Dropdown to select a draft
    faq_id = st.selectbox("Select FAQ Draft to Review", pending_df["faq_id"].tolist())
    row = pending_df[pending_df["faq_id"] == faq_id].iloc[0]
    
    # Display details
    st.markdown(f"**Cluster ID:** {row['cluster_id']}")
    st.markdown(f"**Source Ticket IDs:** {row['source_ticket_ids']}")
    st.markdown(f"**AI Confidence Score:** `{row['confidence_score']}%`")
    
    edited_question = st.text_input("Question", value=row["question"])
    edited_answer = st.text_area("Answer (Step‑by‑step guidelines)", value=row["answer"], height=200)
    admin_comments = st.text_area("Admin Comments (Internal feedback)", placeholder="Wording looks good. Approved for knowledge base.", height=80)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve & Publish"):
            update_faq_draft(faq_id, question=edited_question, answer=edited_answer)
            publish_faq(faq_id)
            st.success(f"🎉 FAQ #{faq_id} has been published successfully!")
            st.rerun()
            
    with col2:
        if st.button("✏️ Save Changes"):
            update_faq_draft(faq_id, question=edited_question, answer=edited_answer)
            st.success("Changes saved successfully.")
            st.rerun()
            
    with col3:
        if st.button("❌ Reject Draft"):
            update_faq_draft(faq_id, status="rejected")
            st.warning(f"FAQ #{faq_id} has been rejected.")
            st.rerun()

if __name__ == "__main__":
    render()
