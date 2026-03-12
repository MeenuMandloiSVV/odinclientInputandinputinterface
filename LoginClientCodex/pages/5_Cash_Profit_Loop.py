import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Cash Profit Loop Parameters",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
    /* HIDE STREAMLIT SIDEBAR MENU AND TOGGLES */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }

    .main {
        background: linear-gradient(135deg, #f8fafc, #efeafe);
    }

    .block-container {
        max-width: 950px;
        padding-top: 2rem;
    }

    .header-card {
        padding: 24px 0;
        margin-bottom: 24px;
        color: #0f172a;
    }
    
    .header-card h2 {
        font-weight: 800 !important;
        font-size: 2.8rem !important;
        color: #0f172a !important;
        letter-spacing: -0.02em;
    }
    
    .header-card p {
        color: #334155 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        opacity: 0.9;
    }

    div[data-testid="stForm"] {
        background: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e0e7ff;
    }

    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #f1f5f9 !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
        text-align: center !important;
        justify-content: center !important;
        border-bottom: 2px solid #cbd5e1 !important;
    }

    /* Style the Add Row / Delete Row button for data editor */
    [data-testid="stDataFrame"] button {
        background-color: #f1f5f9;
        border-radius: 4px;
    }
    
    button[kind="primary"], .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #4f46e5, #9333ea) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }

    button[kind="primary"]:hover, .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(79, 70, 229, 0.4) !important;
    }

    /* Hide Streamlit default page navigation in sidebar */
    section[data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
st.markdown(
    """
    <div class="header-card">
        <h2 style="margin:0">🔄 Cash Profit Loop Inputs</h2>
        <p style="margin:5px 0 0 0; opacity:0.9;">Configure strategy parameters: Symbol Name, Profit Amount, and Investment Amount</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- NAVIGATION ----------------
col_nav1, col_nav2, col_nav3 = st.columns([7.6, 1.2, 1.2])
with col_nav2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
with col_nav3:
    if st.button("⬅️ Back", use_container_width=True):
        st.switch_page("pages/2_Strategy_Selection.py")

# ---------------- LOAD SECRETS ----------------
try:
    MONGO_URI = st.secrets["mongodb"]["uri"]
    COLLECTION_NAME = st.secrets["mongodb"].get("collection", "Selected_Strategies_Inputs")
    MASTER_DB_NAME = st.secrets["mongodb"].get("master_db", "OdinMasterData")
    MASTER_COL_NAME = st.secrets["mongodb"].get("master_collection", "MasterData")
except KeyError:
    st.error("❌ Missing MongoDB configuration in secrets")
    st.stop()
STRATEGY_ID = "CST0007"

# ---------------- CHECK LOGIN ----------------
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first!")
    st.switch_page("app.py")
    st.stop()
    
if not st.session_state.get("selected_strategy"):
    st.error("❌ Please select a strategy first!")
    st.switch_page("pages/2_Strategy_Selection.py")
    st.stop()

# ---------------- CLIENT ID ----------------
client_id = st.session_state.user_id

# ---------------- MONGO CONNECTION ----------------
@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGO_URI)

client = get_mongo_client()
db = client[client_id]
collection = db[COLLECTION_NAME]

@st.cache_data(ttl=3600)
def get_symbol_list():
    try:
        conn = MongoClient(MONGO_URI)
        master_db = conn[MASTER_DB_NAME]
        master_col = master_db[MASTER_COL_NAME]
        docs = master_col.find({"ser": "EQ"}, {"sym": 1, "_id": 0})
        # Extract unique symbols and sort them
        syms = sorted(list(set(d["sym"] for d in docs if "sym" in d)))
        return syms
    except Exception as e:
        return []

valid_symbols = get_symbol_list()

# ---------------- FETCH DATA ----------------
doc = collection.find_one(
    {"StrategyID": STRATEGY_ID},
    {"_id": 0, "Symbol": 1}
)

symbol_data = doc.get("Symbol", {}) if doc else {}
today_str = datetime.now().strftime("%Y-%m-%d")

# Construct initial DataFrame based on MongoDB doc shape
df_data = []
for sym, val in symbol_data.items():
    if isinstance(val, dict):
        item_date = val.get("Date", "")
        if item_date == today_str:
            df_data.append({
                "Symbol_Name": sym,
                "Profit_Amount": float(val.get("Profit_Amount", val.get("Profit Amount", 0.0))),
                "Investment_Amount": float(val.get("Investment_Amount", val.get("Investment Amount", 0.0))),
                "Order_Side": val.get("Order_Side", "BUY").upper(),
                "Date": item_date
            })
    else:
        # Fallback for old data - not loaded for today's view
        pass

if df_data:
    df = pd.DataFrame(df_data)
else:
    df = pd.DataFrame(columns=["Symbol_Name", "Profit_Amount", "Investment_Amount", "Order_Side", "Date"])

# ---------------- FORM ----------------
with st.form("symbol_form"):
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        column_config={
            "Symbol_Name": st.column_config.SelectboxColumn(
                "Stock", 
                help="Select or type stock symbol",
                options=valid_symbols,
                required=True
            ),
            "Profit_Amount": st.column_config.NumberColumn(
                "Profit Amount (₹)", 
                help="Expected profit amount", 
                min_value=0.0, 
                required=True, 
                format="%.2f",
                step=1.0
            ),
            "Investment_Amount": st.column_config.NumberColumn(
                "Investment Amount (₹)", 
                help="Amount allocated for investment", 
                min_value=0.0, 
                required=True, 
                format="%.2f",
                step=1.0
            ),
            "Order_Side": st.column_config.SelectboxColumn(
                "Order Side",
                help="Select BUY or SELL",
                options=["BUY", "SELL"],
                required=True,
                default="BUY"
            ),
            "Date": st.column_config.TextColumn(
                "Date",
                help="Auto-assigned to today's date",
                disabled=True,
                default=today_str
            )
        }
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    save = st.form_submit_button("✅ Save Configuration", use_container_width=True)

# ---------------- SAVE ----------------
if save:
    new_symbol_data = {}
    
    # Preserve symbols from other dates
    for sym, val in symbol_data.items():
        if isinstance(val, dict):
            if val.get("Date", "") != today_str:
                new_symbol_data[sym] = val
    
    # Process dataframe to dict for today's dates
    for index, row in edited_df.iterrows():
        sym_name = str(row["Symbol_Name"]).strip()
        
        # Validations before adding
        if sym_name and sym_name != "None" and sym_name != "nan":
            profit = float(row["Profit_Amount"]) if pd.notnull(row["Profit_Amount"]) else 0.0
            investment = float(row["Investment_Amount"]) if pd.notnull(row["Investment_Amount"]) else 0.0
            order_side = str(row.get("Order_Side", "BUY")).strip().upper() if pd.notnull(row.get("Order_Side")) else "BUY"
            if order_side not in ["BUY", "SELL"]:
                order_side = "BUY"
            
            new_symbol_data[sym_name] = {
                "Profit_Amount": profit,
                "Investment_Amount": investment,
                "Order_Side": order_side,
                "Date": today_str
            }

    # Update MongoDB
    collection.update_one(
        {"StrategyID": STRATEGY_ID},
        {
            "$set": {
                "Symbol": new_symbol_data
            }
        },
        upsert=True
    )

    st.success("🎉 **Success!** Strategy inputs updated and saved to the database.")
    # Minor aesthetic: re-show updated results 
    st.balloons()