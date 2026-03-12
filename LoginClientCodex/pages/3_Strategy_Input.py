import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, time
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.mongodb_handler import MongoDBHandler
from modules.constants import STRATEGY_MAPPING, STRATEGY_FIELDS

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Strategy Input",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>
/* HIDE STREAMLIT SIDEBAR MENU AND TOGGLES */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* Hide Streamlit default page navigation in sidebar */
section[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# -------- CHECK LOGIN --------
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first!")
    st.switch_page("app.py")

if not st.session_state.get("selected_strategy"):
    st.error("❌ Please select a strategy first!")
    st.switch_page("pages/2_Strategy_Selection.py")

# -------- PAGE TITLE --------
strategy_id = st.session_state.selected_strategy
strategy_name = STRATEGY_MAPPING.get(strategy_id, "Unknown Strategy")

st.title(f"⚙️ {strategy_name} Configuration")
st.markdown("---")

# -------- GET SECRETS --------
try:
    mongo_uri = st.secrets["mongodb"]["uri"]
except KeyError:
    st.error("❌ Missing MongoDB URI in secrets")
    st.stop()

# -------- MONGODB HANDLER --------
@st.cache_resource
def get_mongo_handler():
    try:
        return MongoDBHandler(mongo_uri)
    except Exception as e:
        st.error(f"❌ MongoDB connection failed: {str(e)}")
        return None

mongo_handler = get_mongo_handler()

# -------- HEADER WITH REFRESH --------
col1, col2, col3, col4 = st.columns([2.4, 1.2, 1.2, 1.2])

with col1:
    st.markdown(f"""
    **User:** {st.session_state.user_id}  
    **Strategy:** {strategy_name} ({strategy_id})  
    **Last Updated:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}
    """)

with col2:
    if st.button("🔄 Refresh", use_container_width=True, key="refresh_input"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()

with col3:
    if st.button("⬅️ Back", use_container_width=True, key="back_to_strategies"):
        st.session_state.selected_strategy = None
        st.switch_page("pages/2_Strategy_Selection.py")

with col4:
    if st.button("🚪 Logout", use_container_width=True, key="logout_input"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.selected_strategy = None
        st.switch_page("app.py")

st.markdown("---")

# -------- LOAD EXISTING DATA --------
if not mongo_handler:
    st.error("❌ MongoDB connection failed")
    st.stop()

try:
    existing_data = mongo_handler.get_strategy_data(st.session_state.user_id, strategy_id)
    
    # Get strategy fields configuration
    if strategy_id not in STRATEGY_FIELDS:
        st.error(f"❌ Strategy configuration not found: {strategy_id}")
        st.stop()
    
    strategy_config = STRATEGY_FIELDS[strategy_id]
    fields = strategy_config["fields"]
    
    # -------- BUILD FORM --------
    st.subheader("📝 Enter Strategy Parameters")
    st.markdown(f"Configure {strategy_name} parameters. All changes are saved automatically.")
    st.markdown("")
    
    form_data = {}
    
    # Create form inputs based on strategy configuration
    form_cols = st.columns(2)
    col_idx = 0
    
    for field_name, field_config in fields.items():
        col = form_cols[col_idx % 2]
        col_idx += 1
        
        with col:
            field_type = field_config.get("type", "text")
            label = field_config.get("label", field_name)
            default_value = existing_data.get(field_name, field_config.get("default"))
            
            if field_type == "time":
                # For time fields, accept both string and time object
                if isinstance(default_value, str):
                    try:
                        default_value = datetime.strptime(default_value, "%H:%M:%S").time()
                    except:
                        default_value = datetime.strptime(field_config.get("default"), "%H:%M:%S").time()
                elif default_value is None:
                    default_value = datetime.strptime(field_config.get("default"), "%H:%M:%S").time()
                
                value = st.time_input(label, value=default_value, key=f"input_{field_name}")
                form_data[field_name] = value.strftime("%H:%M:%S")
            
            elif field_type == "number":
                value = st.number_input(
                    label,
                    value=float(default_value) if default_value else float(field_config.get("default", 0)),
                    key=f"input_{field_name}"
                )
                form_data[field_name] = value
            
            elif field_type == "checkbox":
                value = st.checkbox(
                    label,
                    value=bool(default_value) if default_value is not None else bool(field_config.get("default", True)),
                    key=f"input_{field_name}"
                )
                form_data[field_name] = value
            
            elif field_type == "text":
                value = st.text_input(
                    label,
                    value=str(default_value) if default_value else "",
                    key=f"input_{field_name}"
                )
                form_data[field_name] = value
    
    # -------- SAVE BUTTON --------
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        save_button = st.button(
            "💾 Save Configuration",
            use_container_width=True,
            type="primary",
            key="save_strategy"
        )
    
    with col2:
        reset_button = st.button(
            "↺ Reset to Default",
            use_container_width=True,
            key="reset_strategy"
        )
    
    with col3:
        view_json = st.button(
            "📄 View JSON",
            use_container_width=True,
            key="view_json"
        )
    
    # -------- SAVE HANDLER --------
    if save_button:
        try:
            success = mongo_handler.save_strategy_data(
                st.session_state.user_id,
                strategy_id,
                form_data
            )
            
            if success:
                st.session_state.last_refresh = datetime.now()
                st.success("✅ Configuration saved successfully!")
                st.balloons()
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to save configuration")
        except Exception as e:
            st.error(f"❌ Error saving: {str(e)}")
    
    # -------- RESET HANDLER --------
    if reset_button:
        st.warning("⚠️ This will reset all values to defaults. Refresh the page to reset.")
    
    # -------- VIEW JSON --------
    if view_json:
        st.markdown("### 📄 Configuration JSON")
        st.json({
            "StrategyID": strategy_id,
            "Strategy": strategy_name,
            "User": st.session_state.user_id,
            "Configuration": form_data,
            "LastUpdated": st.session_state.last_refresh.isoformat()
        })
    
    # -------- CURRENT DATA DISPLAY --------
    st.markdown("---")
    st.subheader("📊 Current Saved Configuration")
    
    if existing_data:
        display_data = {k: v for k, v in existing_data.items() if k not in ["_id", "updated_at", "StrategyID"]}
        
        if display_data:
            st.json(display_data)
        else:
            st.info("ℹ️ No saved data yet. Fill the form above and click Save.")
    else:
        st.info("ℹ️ No saved data yet. Fill the form above and click Save.")
    
    # -------- AUTO-REFRESH SETTINGS (REMOVED) --------

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())

# -------- FOOTER --------
st.markdown("---")
st.caption("📈 Odin Trading Platform | Strategy Configuration Module")
