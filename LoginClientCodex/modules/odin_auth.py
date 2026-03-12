import pyotp
from datetime import datetime
import logging
from pycloudrestapi import IBTConnect

logger = logging.getLogger(__name__)
logger.info("🔑 Odin Auth module loaded")

class OdinAuth:
    """Handle Odin platform authentication"""
    
    def __init__(self, api_url: str, api_key: str):
        logger.info("⏳ Initializing OdinAuth...")
        self.api_url = api_url
        self.api_key = api_key
        self.ibt_connect = None
        self.tenant_id = None
        logger.info(f"✅ OdinAuth initialized with API URL: {api_url}")
    
    def login(self, user_id: str, password: str, totp_secret: str, cached_data=None) -> dict:
        """Authenticate with Odin platform
        
        Args:
            user_id: Trading account user ID
            password: Account password
            totp_secret: TOTP secret key
            cached_data: Previous login response (optional)
        
        Returns:
            Dictionary with login response or error details
        """
        try:
            logger.info(f"🔐 Starting Odin authentication for user {user_id}...")
            
            # Generate TOTP
            logger.info("🔢 Generating TOTP...")
            totp = pyotp.TOTP(totp_secret).now()
            logger.info(f"✅ TOTP generated: {totp}")
            
            # Initialize connection
            logger.info(f"🔗 Initializing IBTConnect with API URL: {self.api_url}...")
            self.ibt_connect = IBTConnect(params={
                "baseurl": self.api_url,
                "api_key": self.api_key,
                "debug": True
            })
            logger.info("✅ IBTConnect initialized")
            
            # Prepare login params
            login_params = {
                "userId": user_id,
                "password": password,
                "totp": totp
            }
            
            # Use cached data if available
            if cached_data:
                login_params["data"] = cached_data
                logger.info(f"📦 Using cached data for user {user_id}")
            
            # Perform login
            logger.info(f"🔓 Calling Odin login API for user {user_id}...")
            response = self.ibt_connect.login(params=login_params)
            logger.info(f"📡 Odin API response received")
            
            if response.get("data") is not None:
                self.tenant_id = response.get("data", {}).get("tenant_id")
                logger.info(f"✅ Odin login SUCCESSFUL for user {user_id}, Tenant ID: {self.tenant_id}")
                return {
                    "success": True,
                    "data": response,
                    "tenant_id": self.tenant_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"⚠️ Odin login failed - No data in response for user {user_id}")
                return {
                    "success": False,
                    "error": "Login failed - invalid credentials or service error",
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"❌ Odin authentication EXCEPTION for user {user_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def logout(self) -> bool:
        """Logout from Odin platform"""
        try:
            logger.info("🚪 Logging out from Odin...")
            if self.ibt_connect:
                self.ibt_connect.logout()
                logger.info("✅ Successfully logged out from Odin")
                return True
            logger.warning("⚠️ No active Odin connection to logout from")
            return False
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if authenticated"""
        is_auth = self.ibt_connect is not None and self.tenant_id is not None
        logger.info(f"🔍 Authentication status check: {is_auth}")
        return is_auth
