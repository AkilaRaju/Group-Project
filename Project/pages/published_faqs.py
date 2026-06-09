# pages/published_faqs.py
"""Page showing all approved and published FAQs."""
import streamlit as st
from backend.db import get_published_faqs

def render():
    st.title("📚 Published FAQs")
    df = get_published_faqs()
    
    if df.empty:
        st.info("No FAQs have been published yet.")
        return

    # Add search input
    search_query = st.text_input("🔍 Search FAQs (by question or answer)", "")
    
    # Filter dataframe based on search query
    if search_query:
        mask = df['question'].str.contains(search_query, case=False, na=False) | df['answer'].str.contains(search_query, case=False, na=False)
        filtered_df = df[mask]
    else:
        filtered_df = df

    st.write(f"Showing {len(filtered_df)} of {len(df)} published FAQ(s).")
    
    # Export options row
    if not filtered_df.empty:
        st.markdown("### 📥 Export FAQs")
        col_csv, col_md, _ = st.columns([1, 1, 3])
        
        # 1. Export as CSV
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        with col_csv:
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="published_faqs.csv",
                mime="text/csv",
                key="download_csv"
            )
            
        # 2. Export as Markdown
        md_content = "# Published FAQs\n\n"
        for _, row in filtered_df.iterrows():
            md_content += f"### Q: {row['question']}\n"
            md_content += f"**A:** {row['answer']}\n"
            md_content += f"*Source Tickets:* {row['source_ticket_ids']}\n\n---\n\n"
        
        with col_md:
            st.download_button(
                label="📝 Download Markdown",
                data=md_content.encode('utf-8'),
                file_name="published_faqs.md",
                mime="text/markdown",
                key="download_md"
            )
            
        st.markdown("---")

    # Render FAQs
    if filtered_df.empty:
        st.warning("No FAQs matches your search query.")
    else:
        for _, row in filtered_df.iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div class="card" style="margin-bottom: 1rem;">
                        <h3 style="color: #6e68ff; margin: 0 0 0.5rem 0;">Q: {row['question']}</h3>
                        <p style="white-space: pre-wrap;">{row['answer']}</p>
                        <small style='color: #888;'>Source Tickets: {row['source_ticket_ids']} | Confidence: {row['confidence_score']}%</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    render()
