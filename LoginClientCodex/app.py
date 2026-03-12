import streamlit as st
import sys
from datetime import datetime
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
from modules.logging_config import setup_logging
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("🚀 Odin Trading Platform - Application Started")
logger.info(f"Session Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 80)

from modules.mongodb_handler import MongoDBHandler

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Odin Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------- GLOBAL STYLE --------
st.markdown("""
<style>
    /* HIDE STREAMLIT SIDEBAR MENU AND TOGGLES */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    .main {
        max-width: 1200px;
    }
    .stButton button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
    }
    .refresh-button {
        float: right;
    }
    .strategy-card {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 10px 0;
    }
    .success-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 10px 0;
    }
    .error-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 10px 0;
    }
    /* Hide Streamlit default page navigation in sidebar */
    section[data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# -------- INITIALIZE SESSION STATE --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    logger.info("🔐 Session State: Initializing as NOT logged in")

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "tenant_id" not in st.session_state:
    st.session_state.tenant_id = None

if "login_response" not in st.session_state:
    st.session_state.login_response = None

if "selected_strategy" not in st.session_state:
    st.session_state.selected_strategy = None

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()



if "login_checked" not in st.session_state:
    st.session_state.login_checked = False
    logger.info("🔍 Auto-login check status: Not yet performed")

# -------- AUTO-CHECK LOGIN ON APP START --------
if not st.session_state.login_checked:
    logger.info("⏳ Performing automatic login check at app startup...")
    
    try:
        mongo_uri = st.secrets.get("mongodb", {}).get("uri")
        
        if mongo_uri:
            mongo_handler = MongoDBHandler(mongo_uri)
            logger.info("✅ MongoDB connection established for auto-check")
            st.session_state.login_checked = True
            logger.info("✅ Auto-login check completed - system ready")
        else:
            logger.warning("⚠️ MongoDB URI not found in secrets")
            st.session_state.login_checked = True
    except Exception as e:
        logger.error(f"❌ Error during auto-login check: {str(e)}")
        st.session_state.login_checked = True

# -------- MAIN PAGE --------
st.markdown("<h1 style='text-align: center;'>📈 Odin Client Strategy Portal</h1>", unsafe_allow_html=True)
st.markdown("---")

logger.info(f"📄 Page rendering - Logged In: {st.session_state.logged_in} | User: {st.session_state.user_id}")

if not st.session_state.logged_in:
    logger.info("🔐 Displaying home page (user not logged in)")
    
    # Create empty columns on the sides to center the middle content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h3 style='text-align: center;'>👤 User Identification</h3>", unsafe_allow_html=True)
        st.info("Please enter your User ID to continue. We will check if you have an active session for today.")
        
        user_id_input = st.text_input("User ID", autocomplete="off")
        
        if st.button("Continue ➡️", type="primary", use_container_width=True):
            if not user_id_input:
                st.error("❌ Please enter a User ID.")
            else:
                try:
                    mongo_uri = st.secrets.get("mongodb", {}).get("uri")
                    if mongo_uri:
                        mongo_handler = MongoDBHandler(mongo_uri)
                        login_exists = mongo_handler.check_login_today(user_id_input)
                        
                        if login_exists:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id_input
                            
                            db_name = st.secrets["mongodb"]["login_db"]
                            coll_name = st.secrets["mongodb"]["login_collection"]
                            cached_login = mongo_handler.client[db_name][coll_name].find_one(
                                {"data.user_id": user_id_input}
                            )
                            if cached_login:
                                st.session_state.login_response = cached_login
                                st.session_state.tenant_id = cached_login.get("data", {}).get("tenant_id")
                            
                            st.session_state.last_refresh = datetime.now()
                            import time
                            time.sleep(1)
                            st.switch_page("pages/2_Strategy_Selection.py")
                        else:
                            st.session_state.temp_user_id = user_id_input
                            import time
                            time.sleep(1)
                            st.switch_page("pages/1_Login.py")
                    else:
                        st.error("❌ MongoDB URI not configured in secrets.")
                except Exception as e:
                    st.error(f"❌ Database error: {e}")
else:
    logger.info(f"✅ Displaying dashboard for user: {st.session_state.user_id}")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ Logged in as: **{st.session_state.user_id}**")
    with col2:
        if st.button("🚪 Logout", key="logout_main"):
            logger.info(f"🚪 Logout initiated by user: {st.session_state.user_id}")
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.tenant_id = None
            st.session_state.login_response = None
            st.session_state.selected_strategy = None
            st.session_state.login_checked = False
            logger.info("🚪 Logout complete - session cleared")
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 📊 Dashboard
    
    You have successfully logged in! Wait to be redirected or navigate accordingly.
    
    **Last Updated:** """ + st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S"))



logger.info("=" * 80)
logger.info("✅ Page render complete")
logger.info("=" * 80)
