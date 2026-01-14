import streamlit as st

st.set_page_config(
    page_title="Grass Squad Analytics",
    page_icon="🌊",
    layout="wide"
)

st.title("Grass Squad Analytics Platform")

st.markdown("""
### Welcome to the Data Management & Analytics UI

This platform creates a seamless interface for managing and analyzing maritime operation data.

**Navigate to:**
- **📊 Dashboard**: View key performance indicators and operational maps.
- **📝 Gestion Données**: Edit operation records (CRUD) and manage data quality.
- **🛡️ Audit**: Track all changes made to the database.

---
*Built with Streamlit, Pandas, and PostgreSQL.*
""")

st.sidebar.success("Select a page above.")
