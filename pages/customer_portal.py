# pages/customer_portal.py
"""Page for customers to raise support tickets."""
import streamlit as st
from backend.db import insert_ticket

def render():
    st.title("👤 Customer Portal")
    st.write("Raise a new support ticket")

    with st.form("submit_ticket_form", clear_on_submit=True):
        st.markdown("<h3 style='margin-top:0; color: #fff;'>Submit a New Ticket</h3>", unsafe_allow_html=True)
        
        subject = st.text_input("Issue Subject *", placeholder="VPN not connecting")
        description = st.text_area("Detailed Description *", placeholder="I am unable to connect to the VPN since morning. Getting 'Connection Timeout' error.", height=150)
        
        submitted = st.form_submit_button("Submit Ticket")
        
        if submitted:
            if not subject.strip():
                st.error("Please enter an issue subject.")
                return
            
            # Combine subject and description for the SQLite issue text
            full_issue = f"{subject.strip()}: {description.strip()}" if description.strip() else subject.strip()
            
            # Insert into database
            ticket_id = insert_ticket(issue=full_issue, status="open")
            
            st.markdown(
                f"""
                <div style="background-color: rgba(0, 204, 102, 0.1); border: 1px solid rgba(0, 204, 102, 0.3); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                    <div style="display: flex; align-items: center; color: #00cc66; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        <span>✅ Ticket submitted successfully!</span>
                    </div>
                    <div style="color: #eee; font-size: 0.95rem;">
                        Ticket ID: <strong style="color:#00cc66;">TKT-{ticket_id}</strong> | Status: <strong style="color:#00cc66;">Open</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    render()
