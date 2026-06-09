# app.py
"""Main entry point for the AI‑Powered Ticket‑to‑FAQ Streamlit app.
It sets up the multipage navigation and loads the shared CSS.
"""
import streamlit as st
from pathlib import Path

# Load custom CSS for premium dark‑mode design
def load_css():
    css_path = Path(__file__).parent / "static" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Page configuration
st.set_page_config(page_title="Ticket‑to‑FAQ Dashboard", layout="wide")

# Load CSS
load_css()

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Dashboard'

# Sidebar Navigation Header
st.sidebar.markdown(
    """
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;'>
        <span style='font-size: 1.5rem;'>⚙️</span>
        <h3 style='margin: 0; color: #fff; font-size: 1.25rem; font-weight: 700;'>Ticket‑to‑FAQ Pipeline</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Render Dashboard
if st.sidebar.button("🏠 Dashboard", key="nav_dashboard"):
    st.session_state['current_page'] = 'Dashboard'
    st.rerun()

st.sidebar.markdown("<div class='sidebar-section'>TICKET SIMULATOR</div>", unsafe_allow_html=True)
if st.sidebar.button("👤 Customer Portal", key="nav_customer_portal"):
    st.session_state['current_page'] = 'Customer Portal'
    st.rerun()
if st.sidebar.button("🎧 Support Panel", key="nav_support_agent_panel"):
    st.session_state['current_page'] = 'Support Agent Panel'
    st.rerun()

st.sidebar.markdown("<div class='sidebar-section'>PIPELINE</div>", unsafe_allow_html=True)
if st.sidebar.button("🗄️ Closed Tickets", key="nav_closed_tickets"):
    st.session_state['current_page'] = 'Closed Tickets'
    st.rerun()
if st.sidebar.button("🕸️ Clusters", key="nav_clusters"):
    st.session_state['current_page'] = 'Clusters'
    st.rerun()
if st.sidebar.button("📝 FAQ Drafts", key="nav_faq_drafts"):
    st.session_state['current_page'] = 'FAQ Drafts'
    st.rerun()
if st.sidebar.button("🛡️ Admin Review", key="nav_admin_review"):
    st.session_state['current_page'] = 'Admin Review'
    st.rerun()
if st.sidebar.button("📚 Published FAQs", key="nav_published_faqs"):
    st.session_state['current_page'] = 'Published FAQs'
    st.rerun()

st.sidebar.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 2rem 0 1rem 0;'>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Logout", key="nav_logout"):
    st.session_state['current_page'] = 'Dashboard'
    st.success("Log out successful!")
    st.rerun()

# Dynamic Active Button Highlight Injection
button_indices = {
    "Dashboard": 1,
    "Customer Portal": 2,
    "Support Agent Panel": 3,
    "Closed Tickets": 4,
    "Clusters": 5,
    "FAQ Drafts": 6,
    "Admin Review": 7,
    "Published FAQs": 8
}
active_idx = button_indices.get(st.session_state['current_page'], 1)

# Injected CSS to highlight active item
st.markdown(
    f"""
    <style>
    /* Highlight the active navigation button in the sidebar */
    div[data-testid="stSidebar"] .stButton:nth-of-type({active_idx}) button {{
        background: linear-gradient(135deg, #4e44ff, #6e68ff) !important;
        color: white !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

pages = {
    "Customer Portal": "pages/customer_portal.py",
    "Support Agent Panel": "pages/support_agent_panel.py",
    "Dashboard": "pages/dashboard.py",
    "Closed Tickets": "pages/closed_tickets.py",
    "Clusters": "pages/clusters.py",
    "FAQ Drafts": "pages/faq_drafts.py",
    "Admin Review": "pages/admin_review.py",
    "Published FAQs": "pages/published_faqs.py",
}

selection = st.session_state['current_page']

# Dynamically import and run the selected page module
page_path = Path(__file__).parent / pages[selection]
module_name = f"pages.{selection.lower().replace(' ', '_')}"

# Use importlib to load the module
import importlib.util, sys
spec = importlib.util.spec_from_file_location(module_name, page_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

# Each page module must define a `render()` function
if hasattr(module, "render"):
    module.render()
else:
    st.error(f"Page {selection} does not have a render() function.")
