import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.mongodb_handler import MongoDBHandler
from modules.constants import STRATEGY_MAPPING

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Strategy Selection",
    page_icon="📊",
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

st.title("📊 Strategy Selection")
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

# -------- REFRESH LOGIC --------
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.markdown(f"**User:** {st.session_state.user_id} | **Last Updated:** {st.session_state.last_refresh.strftime('%H:%M:%S')}")

with col2:
    if st.button("🔄 Refresh", use_container_width=True, key="refresh_strategies"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()

with col3:
    if st.button("🚪 Logout", use_container_width=True, key="logout_strategies"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.selected_strategy = None
        st.switch_page("app.py")

st.markdown("---")

# -------- GET USER STRATEGIES --------
if not mongo_handler:
    st.error("❌ MongoDB connection failed")
    st.stop()

try:
    strategy_ids = mongo_handler.get_user_strategies(st.session_state.user_id)
    
    if not strategy_ids:
        st.warning("⚠️ No strategies found in your MongoDB database!")
        st.info(f"Please add strategies to the **{st.session_state.user_id}** database under **Selected_Strategies_Inputs** collection.")
        st.stop()
    
    # Map StrategyIDs to Strategy Names
    strategy_names = []
    strategy_mapping_dict = {}
    
    for strategy_id in strategy_ids:
        if strategy_id in STRATEGY_MAPPING:
            strategy_name = STRATEGY_MAPPING[strategy_id]
            strategy_names.append(strategy_name)
            strategy_mapping_dict[strategy_name] = strategy_id
    
    if not strategy_names:
        st.error("❌ No valid strategies found!")
        st.stop()
    
    st.subheader("🎯 Available Strategies")
    st.markdown("Select a strategy to configure:")
    st.markdown("")
    
    # Display strategies as cards
    cols = st.columns(len(strategy_names))
    
    for idx, strategy_name in enumerate(strategy_names):
        with cols[idx]:
            strategy_id = strategy_mapping_dict[strategy_name]
            
            card = st.container(border=True)
            with card:
                st.markdown(f"### {strategy_name}")
                st.caption(f"ID: {strategy_id}")
                
                if st.button(
                    "⚙️ Configure",
                    key=f"select_{strategy_id}",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.selected_strategy = strategy_id
                    st.session_state.last_refresh = datetime.now()
                    
                    if strategy_id == "CST0007":
                        st.switch_page("pages/5_Cash_Profit_Loop.py")
                    elif strategy_id in ["CST0005", "CST0003"]:
                        st.switch_page("pages/4_Straddle_And_ATP.py")
                    else:
                        st.switch_page("pages/3_Strategy_Input.py")
    

    
except Exception as e:
    st.error(f"❌ Error loading strategies: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
