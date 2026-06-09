# pages/support_agent_panel.py
"""Page for support agents to resolve and close open tickets."""
import streamlit as st
from backend.db import get_open_tickets, close_ticket

def render():
    st.title("🎧 Support Panel")
    st.write("Resolve open tickets raised by customers.")

    open_df = get_open_tickets()
    
    if open_df.empty:
        st.success("✅ All caught up! No open support tickets to resolve.")
        return

    st.subheader(f"Open Tickets ({len(open_df)})")
    
    # Initialize selected ticket in session state
    if 'selected_ticket_id' not in st.session_state:
        st.session_state['selected_ticket_id'] = open_df.iloc[0]['ticket_id']
        
    # If the selected ticket is no longer open, reset to first open ticket
    if st.session_state['selected_ticket_id'] not in open_df['ticket_id'].values:
        st.session_state['selected_ticket_id'] = open_df.iloc[0]['ticket_id']
        
    selected_id = st.session_state['selected_ticket_id']

    # Table Header
    col_radio, col_id, col_subj, col_raised, col_status, col_act = st.columns([0.4, 1.0, 2.5, 2.0, 1.0, 1.0])
    with col_radio:
        st.markdown("")
    with col_id:
        st.markdown("**Ticket ID**")
    with col_subj:
        st.markdown("**Issue Subject**")
    with col_raised:
        st.markdown("**Raised On**")
    with col_status:
        st.markdown("**Status**")
    with col_act:
        st.markdown("**Action**")
        
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 0.5rem 0;'>", unsafe_allow_html=True)

    # Render each row
    for _, row in open_df.iterrows():
        t_id = row['ticket_id']
        subj = row['issue'].split(':')[0] if ':' in row['issue'] else row['issue']
        raised = row['raised_at'] if row['raised_at'] else "N/A"
        is_selected = (t_id == selected_id)
        
        color_class = "color: #ffaa44; font-weight: bold;" if is_selected else "color: #eee;"
        radio_icon = "🔘" if is_selected else "⚪"
        
        c_radio, c_id, c_subj, c_raised, c_status, c_act = st.columns([0.4, 1.0, 2.5, 2.0, 1.0, 1.0])
        
        with c_radio:
            st.markdown(f"<div style='text-align: center; margin-top: 8px; font-size: 1.1rem;'>{radio_icon}</div>", unsafe_allow_html=True)
        with c_id:
            st.markdown(f"<div style='margin-top: 8px; {color_class}'>TKT-{t_id}</div>", unsafe_allow_html=True)
        with c_subj:
            st.markdown(f"<div style='margin-top: 8px; color: #eee; font-weight: {'600' if is_selected else '400'};'>{subj}</div>", unsafe_allow_html=True)
        with c_raised:
            st.markdown(f"<div style='margin-top: 8px; color: #aaa; font-size: 0.9rem;'>{raised}</div>", unsafe_allow_html=True)
        with c_status:
            st.markdown(
                """
                <div style='margin-top: 6px;'>
                    <span style="background-color: rgba(255, 165, 0, 0.15); color: #ffa500; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; border: 1px solid rgba(255,165,0,0.3);">Open</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_act:
            if st.button("Resolve", key=f"sel_{t_id}"):
                st.session_state['selected_ticket_id'] = t_id
                st.rerun()
                
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 0.4rem 0;'>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Resolution Portal")
    
    # Load selected row details
    selected_row = open_df[open_df['ticket_id'] == selected_id].iloc[0]
    sel_id = selected_row['ticket_id']
    sel_issue = selected_row['issue']
    
    with st.form("resolution_form"):
        st.markdown(
            f"""
            <div style="background-color: rgba(110, 104, 255, 0.05); border: 1px solid rgba(110, 104, 255, 0.2); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <h5 style="margin: 0; color: #a19dff; font-size: 1rem; font-weight: 600;">Resolving TKT-{sel_id}</h5>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem; color: #e2e8f0;">{sel_issue}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        resolution_input = st.text_area(
            "Resolution / Steps Taken *",
            placeholder="Checked service status. Verified user configuration. Cleared cache and reconnected.",
            height=150,
            key=f"res_input_{sel_id}"
        )
        
        submitted = st.form_submit_button("Mark as Closed")
        
        if submitted:
            if not resolution_input.strip():
                st.error("Please enter a resolution description before marking the ticket as closed.")
                return
                
            try:
                close_ticket(sel_id, resolution_input.strip())
                st.success(f"🎉 Ticket TKT-{sel_id} has been marked as Closed!")
                st.rerun()
            except Exception as e:
                st.error(f"Error closing ticket: {e}")

if __name__ == "__main__":
    render()
