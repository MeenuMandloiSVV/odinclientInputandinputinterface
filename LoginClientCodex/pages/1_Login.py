import streamlit as st
import sys
from datetime import datetime
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
from modules.logging_config import setup_logging
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("📄 LOGIN PAGE LOADED")
logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 80)

from modules.mongodb_handler import MongoDBHandler
from modules.odin_auth import OdinAuth

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Login - Odin Platform",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 Odin Platform Login")
st.markdown("---")

# -------- DISABLE AUTOCOMPLETE GLOBALLY --------
st.markdown("""
<style>
/* HIDE STREAMLIT SIDEBAR MENU AND TOGGLES */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

input[type="text"], input[type="password"] {
    -webkit-autofill: none !important;
    -webkit-autofill:hover !important;
    -webkit-autofill:focus !important;
}
input[type="text"]::-webkit-autofill,
input[type="password"]::-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px white inset !important;
    box-shadow: 0 0 0 1000px white inset !important;
}
/* Hide Streamlit default page navigation in sidebar */
section[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# -------- GET SECRETS --------
try:
    logger.info("🔑 Retrieving secrets from configuration...")
    mongo_uri = st.secrets["mongodb"]["uri"]
    api_url = st.secrets["odin"]["api_url"]
    logger.info("✅ All secrets retrieved successfully")
except KeyError as e:
    logger.error(f"❌ Missing secret: {str(e)}")
    st.error("❌ Missing secrets configuration. Please set up .streamlit/secrets.toml")
    st.info("Required secrets:\n- mongodb.uri\n- odin.api_url")
    st.stop()

# -------- MONGODB HANDLER --------
@st.cache_resource
def get_mongo_handler():
    logger.info("🔗 Initializing MongoDB handler...")
    try:
        handler = MongoDBHandler(mongo_uri)
        logger.info("✅ MongoDB handler initialized successfully")
        return handler
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)}")
        st.error(f"❌ MongoDB connection failed: {str(e)}")
        return None

mongo_handler = get_mongo_handler()
logger.info(f"📊 Mongo handler status: {'Connected' if mongo_handler else 'Failed'}")

# -------- LOGIN FORM --------
st.subheader("📋 Enter Your Credentials")
logger.info("📝 Displaying login form")

col1, col2 = st.columns([1, 1])

with col1:
    user_id = st.text_input(
        "User ID",
        value=st.session_state.get("temp_user_id", ""),
        key="login_user_id",
        autocomplete="off"
    )

with col2:
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password",
        key="login_password",
        autocomplete="off"
    )

col1, col2 = st.columns([1, 1])

with col1:
    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="Enter API key",
        key="login_api_key",
        autocomplete="off"
    )

with col2:
    totp_secret = st.text_input(
        "TOTP Secret",
        type="password",
        placeholder="Enter TOTP secret",
        key="login_totp",
        autocomplete="off"
    )

# -------- LOGIN LOGIC --------
st.markdown("---")

login_button = st.button("🔓 Login", use_container_width=True, type="primary")

st.markdown("---")
st.info("ℹ️ Please login first to access the platform.")

if login_button:
    logger.info("=" * 80)
    logger.info("🔐 LOGIN ATTEMPT INITIATED")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    if not all([user_id, password, api_key_input, totp_secret]):
        logger.warning(f"❌ Missing credentials - User ID: {user_id}, Password: {'*' * len(password)}, API Key: {'***'}, TOTP: {'***'}")
        st.error("❌ All fields are required!")
        st.stop()
    
    st.markdown("---")
    status_container = st.container()
    
    with status_container:
        
        if not mongo_handler:
            st.error("❌ MongoDB connection failed")
            st.stop()
        
        try:
            logger.info("🔍 **STEP 1:** Checking MongoDB for today's login...")
            login_exists = mongo_handler.check_login_today(user_id)
            logger.info(f"📊 MongoDB check result: Login exists today = {login_exists}")
            
            if login_exists:
                logger.info(f"✅ Today's login FOUND for user {user_id} - using cached session")
                
                # Store session state
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                logger.info(f"📝 Session state updated - logged_in=True, user_id={user_id}")
                
                # Get cached login data
                db_name = st.secrets["mongodb"]["login_db"]
                coll_name = st.secrets["mongodb"]["login_collection"]
                cached_login = mongo_handler.client[db_name][coll_name].find_one(
                    {"data.user_id": user_id}
                )
                if cached_login:
                    st.session_state.login_response = cached_login
                    st.session_state.tenant_id = cached_login.get("data", {}).get("tenant_id")
                    logger.info(f"✅ Cached login data loaded for user {user_id}")
                
                st.session_state.last_refresh = datetime.now()
                logger.info(f"✅ Last refresh timestamp set: {st.session_state.last_refresh}")
                
                import time
                time.sleep(1)
                logger.info(f"🚀 Redirecting user {user_id} to Strategy Selection page")
                st.switch_page("pages/2_Strategy_Selection.py")
            
            else:
                logger.info(f"⚠️ No login found today for user {user_id} - proceeding with Odin authentication")
                
                # Step 2: Odin Authentication
                logger.info("🔐 **STEP 2:** Authenticating with Odin platform...")
                
                odin_auth = OdinAuth(api_url, api_key_input)
                logger.info(f"🔑 OdinAuth object created for user {user_id}")
                
                login_result = odin_auth.login(user_id, password, totp_secret)
                logger.info(f"🔐 Odin authentication result: {login_result.get('success')}")
                
                if login_result["success"]:
                    logger.info(f"✅ Odin authentication SUCCESSFUL for user {user_id}")
                    
                    # Step 3: Save to MongoDB
                    logger.info("💾 **STEP 3:** Saving login to MongoDB...")
                    
                    save_result = mongo_handler.save_login(user_id, login_result["data"])
                    logger.info(f"💾 MongoDB save result: {save_result}")
                    
                    if save_result:
                        logger.info(f"✅ Login SUCCESSFULLY saved to MongoDB for user {user_id}")
                        
                        # Store session state
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.login_response = login_result["data"]
                        st.session_state.tenant_id = login_result.get("tenant_id")
                        st.session_state.last_refresh = datetime.now()
                        logger.info(f"📝 Session state updated - All fields set for user {user_id}")
                        
                        import time
                        time.sleep(1)
                        logger.info(f"🚀 Login complete - Redirecting user {user_id} to Strategy Selection")
                        logger.info("=" * 80)
                        st.switch_page("pages/2_Strategy_Selection.py")
                    else:
                        logger.error(f"❌ Failed to save login to MongoDB for user {user_id}")
                        st.error("❌ Failed to save login to MongoDB")
                else:
                    logger.error(f"❌ Odin authentication FAILED for user {user_id}: {login_result.get('error')}")
                    st.error(f"❌ Odin authentication failed: {login_result.get('error')}")
        
        except Exception as e:
            logger.error(f"❌ LOGIN ERROR for user {user_id}: {str(e)}")
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Full traceback:\n{error_trace}")
            st.error(f"❌ Login error: {str(e)}")
            st.error(error_trace)

# -------- HELP SECTION --------
st.markdown("---")
with st.expander("❓ Need Help?"):
    st.markdown("""
    ### Login Information
    - **User ID**: Your Odin trading account ID
    - **Password**: Your Odin account password
    - **API Key**: Your Odin API credentials
    - **TOTP Secret**: Your Time-based One-Time Password secret
    
    ### Security Notes
    - All credentials are sent directly to Odin (not stored)
    - Login credentials are verified through TOTP
    - MongoDB stores only authentication tokens, not passwords
    """)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.caption("🔒 Secure Login Portal")
