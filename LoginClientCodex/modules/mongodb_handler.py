import asyncio
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime
import logging
import streamlit as st

logger = logging.getLogger(__name__)
logger.info("🔗 MongoDB Handler module loaded")

class MongoDBHandler:
    """Handle all MongoDB operations"""
    
    def __init__(self, mongo_uri: str):
        logger.info("⏳ Initializing MongoDBHandler...")
        self.mongo_uri = mongo_uri
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            logger.info("🔗 Connecting to MongoDB...")
            self.client = MongoClient(
                self.mongo_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=5000
            )
            # Verify connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful and verified")
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ MongoDB connection timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    def check_login_today(self, user_id: str) -> bool:
        """Check if user already logged in today"""
        try:
            logger.info(f"🔍 Checking login record for user {user_id}...")
            
            # Fetch names from secrets, with safe defaults
            db_name = st.secrets["mongodb"]["login_db"]
            coll_name = st.secrets["mongodb"]["login_collection"]
            
            db = self.client[db_name]
            collection = db[coll_name]
            
            today = datetime.today().strftime("%Y-%b-%d")
            logger.info(f"📅 Checking for login on date: {today}")
            
            result = collection.find_one({
                "data.user_id": user_id,
                "data.login_time": {"$regex": today}
            })
            
            if result:
                logger.info(f"✅ Login found TODAY for user {user_id}")
                return True
            else:
                logger.info(f"⚠️ No login found today for user {user_id}")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking login for {user_id}: {e}")
            return False
    
    def save_login(self, user_id: str, login_response: dict) -> bool:
        """Save login response to MongoDB"""
        try:
            logger.info(f"💾 Saving login response for user {user_id}...")
            db_name = st.secrets["mongodb"]["login_db"]
            coll_name = st.secrets["mongodb"]["login_collection"]
            
            db = self.client[db_name]
            collection = db[coll_name]
            
            collection.replace_one(
                {"data.user_id": user_id},
                login_response,
                upsert=True
            )
            logger.info(f"✅ Login saved successfully for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving login for {user_id}: {e}")
            return False
    
    def get_user_strategies(self, user_id: str) -> list:
        """Get list of strategies for user from their MongoDB database"""
        try:
            logger.info(f"📊 Fetching strategies for user {user_id}...")
            
            coll_name = st.secrets["mongodb"]["strategy_collection"]
            db = self.client[user_id]  # Database name is user ID
            collection = db[coll_name]
            
            results = collection.find({}, {"StrategyID": 1})
            strategy_ids = [doc.get("StrategyID") for doc in results if "StrategyID" in doc]
            
            logger.info(f"✅ Found {len(strategy_ids)} strategies for user {user_id}: {strategy_ids}")
            return strategy_ids
        except Exception as e:
            logger.error(f"❌ Error getting strategies for {user_id}: {e}")
            return []
    
    def get_strategy_data(self, user_id: str, strategy_id: str) -> dict:
        """Get existing data for a specific strategy"""
        try:
            logger.info(f"📄 Fetching strategy data for {user_id}/{strategy_id}...")
            
            coll_name = st.secrets["mongodb"]["strategy_collection"]
            db = self.client[user_id]  # Database name is user ID
            collection = db[coll_name]
            
            result = collection.find_one({"StrategyID": strategy_id})
            if result:
                logger.info(f"✅ Strategy data found for {strategy_id}")
            else:
                logger.info(f"⚠️ No data found for strategy {strategy_id}")
            return result if result else {}
        except Exception as e:
            logger.error(f"❌ Error getting strategy data for {user_id}/{strategy_id}: {e}")
            return {}
    
    def save_strategy_data(self, user_id: str, strategy_id: str, data: dict) -> bool:
        """Save or update strategy data"""
        try:
            logger.info(f"💾 Saving strategy data for {user_id}/{strategy_id}...")
            
            coll_name = st.secrets["mongodb"]["strategy_collection"]
            db = self.client[user_id]  # Database name is user ID
            collection = db[coll_name]
            
            doc = {
                "StrategyID": strategy_id,
                **data,
                "updated_at": datetime.utcnow()
            }
            
            collection.find_one_and_update(
                {"StrategyID": strategy_id},
                {"$set": doc},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            logger.info(f"✅ Strategy data saved successfully for {user_id}/{strategy_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving strategy data for {user_id}/{strategy_id}: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")
