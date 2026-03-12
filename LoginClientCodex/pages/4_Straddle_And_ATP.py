# app.py
import streamlit as st
from datetime import datetime, time, timedelta
from pymongo import MongoClient, ReturnDocument
from zoneinfo import ZoneInfo

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Strategy Control Panel",
    page_icon="🟢",
    layout="wide"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
/* HIDE STREAMLIT SIDEBAR MENU AND TOGGLES */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.inline-label {
    white-space: nowrap;
    font-size: 0.85rem;
    line-height: 2.2;
}
div[data-testid="column"] {
    padding-top: 0px;
    padding-bottom: 0px;
}
input, select {
    height: 38px !important;
}
input::-webkit-calendar-picker-indicator {
    display: none !important;
}
/* Hide Streamlit default page navigation in sidebar */
section[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


class StrategyApp:

    STRATEGIES = {
        "Straddle Shift": "CST0005",
        "ATP": "CST0003"
    }

    MIN_T = time(9, 15, 0)
    MAX_T = time(15, 30, 0)
    DEFAULT_START = time(9, 15, 0)
    DEFAULT_END = time(15, 15, 0)

    def __init__(self):
        try:
            self.MONGO_URI = st.secrets["mongodb"]["uri"]
            self.COLLECTION_NAME = st.secrets["mongodb"].get("collection", "Selected_Strategies_Inputs")
        except KeyError:
            st.error("❌ Missing MongoDB URI in secrets")
            st.stop()
            
        self.mongo_client = MongoClient(
            self.MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        self.allowed_times, self.allowed_labels = self._build_time_options(self.MIN_T, self.MAX_T)
        self.STRATEGY_ID = None

    # ---------------- TIME UTILS ----------------
    def _build_time_options(self, min_t, max_t):
        base = datetime(2000, 1, 1)
        cur = datetime.combine(base.date(), min_t)
        end = datetime.combine(base.date(), max_t)
        times = []
        while cur <= end:
            times.append(cur.time())
            cur += timedelta(minutes=1)
        labels = [t.strftime("%H:%M:%S") for t in times]
        return times, labels

    def _time_to_index(self, t):
        try:
            return self.allowed_times.index(t)
        except ValueError:
            return 0

    # ---------------- MONGO ----------------
    def _get_collection(self, db_name):
        return self.mongo_client[db_name][self.COLLECTION_NAME]

    def _load_existing(self, db_name):
        return self._get_collection(db_name).find_one(
            {"StrategyID": self.STRATEGY_ID}
        )

    def _upsert(self, db_name, doc):
        return self._get_collection(db_name).find_one_and_update(
            {"StrategyID": self.STRATEGY_ID},
            {"$set": doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    # ---------------- INLINE UI HELPERS ----------------
    def _inline_label(self, text):
        st.markdown(f"<div class='inline-label'>{text}</div>", unsafe_allow_html=True)

    def _inline_checkbox(self, label, key, value=False):
        l, r = st.columns([1, 1.3])
        with l:
            self._inline_label(label)
        with r:
            return st.checkbox("", value=value, key=key, label_visibility="collapsed")

    def _inline_number(self, label, key, value=0, min_value=0):
        l, r = st.columns([1, 1.3])
        with l:
            self._inline_label(label)
        with r:
            return int(st.number_input(
                "", value=int(value), min_value=min_value,
                step=1, key=key, label_visibility="collapsed"
            ))

    def _inline_text(self, label, key, value=""):
        l, r = st.columns([1, 1.3])
        with l:
            self._inline_label(label)
        with r:
            return st.text_input(
                "", value=value, key=key,
                label_visibility="collapsed",
                autocomplete="off"
            )

    def _inline_select(self, label, key, options, index=0):
        l, r = st.columns([1, 1.3])
        with l:
            self._inline_label(label)
        with r:
            return st.selectbox("", options, index=index, key=key, label_visibility="collapsed")

    # ---------------- STRADDLE SHIFT ----------------
    def straddle_shift_form(self, client_id):

        existing = self._load_existing(client_id) or {}
        k = client_id.replace(" ", "_")

        with st.form(f"straddle_form_{k}"):

            st.subheader("Straddle Shift Strategy Inputs")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                Start = self._inline_checkbox("Start", f"Start_{k}", existing.get("Start", False))
                Pause = self._inline_checkbox("Pause", f"Pause_{k}", existing.get("Pause", False))
                Stop = self._inline_checkbox("Stop", f"Stop_{k}", existing.get("Stop", False))

            with c2:
                CallEntry = self._inline_checkbox("CallEntry", f"CallEntry_{k}", existing.get("CallEntry", False))
                PutEntry = self._inline_checkbox("PutEntry", f"PutEntry_{k}", existing.get("PutEntry", False))
                ShiftHedge = self._inline_checkbox("ShiftHedge", f"ShiftHedge_{k}", existing.get("ShiftHedge", False))
                FirstEntry = self._inline_checkbox("FirstEntry", f"FirstEntry_{k}", existing.get("FirstEntry", False))

            with c3:
                OTMPoints = self._inline_number("OTMPoints", f"OTM_{k}", existing.get("OTMPoints", 0))
                HedgePoints = self._inline_number("HedgePoints", f"Hedge_{k}", existing.get("HedgePoints", 0))
                ShiftPoints = self._inline_number("ShiftPoints", f"Shift_{k}", existing.get("ShiftPoints", 0))

            with c4:
                Symbol = self._inline_text("Symbol", f"Symbol_{k}", existing.get("Symbol", ""))
                ExpiryNo = self._inline_number("ExpiryNo", f"Expiry_{k}", existing.get("ExpiryNo", 0))
                OrderLot = self._inline_number("OrderLot", f"Lot_{k}", existing.get("OrderLot", 1), 1)

            st.subheader("Timing")

            StartLabel = self._inline_select(
                "StartTime", f"ST_{k}",
                self.allowed_labels,
                self._time_to_index(self.DEFAULT_START)
            )
            EndLabel = self._inline_select(
                "EndTime", f"ET_{k}",
                self.allowed_labels,
                self._time_to_index(self.DEFAULT_END)
            )

            submit = st.form_submit_button("Save Inputs")

        if submit:
            doc = {
                "StrategyID": self.STRATEGY_ID,
                "Start": Start,
                "Pause": Pause,
                "Stop": Stop,
                "CallEntry": CallEntry,
                "PutEntry": PutEntry,
                "ShiftHedge": ShiftHedge,
                "FirstEntry": FirstEntry,
                "OTMPoints": OTMPoints,
                "HedgePoints": HedgePoints,
                "ShiftPoints": ShiftPoints,
                "Symbol": Symbol,
                "ExpiryNo": ExpiryNo,
                "OrderLot": OrderLot,
                "StartTime": StartLabel,
                "EndTime": EndLabel,
                "updated_at": datetime.utcnow()
            }
            self._upsert(client_id, doc)
            st.success("Straddle Shift saved successfully")

    # ---------------- ATP UI ONLY ----------------
    def atp_form(self, existing, k):

        st.subheader("ATP Strategy Inputs")

        c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.6, 1.4, 1.4])

        with c1:
            Start = self._inline_checkbox("Start", f"Start_{k}", existing.get("Start", False))
            Pause = self._inline_checkbox("Pause", f"Pause_{k}", existing.get("Pause", False))
            Stop = self._inline_checkbox("Stop", f"Stop_{k}", existing.get("Stop", False))

        with c2:
            Active = self._inline_checkbox("Active", f"Active_{k}", existing.get("Active", False))
            FirstEntry = self._inline_checkbox("FirstEntry", f"FirstEntry_{k}", existing.get("FirstEntry", False))
            ReEntryActive = self._inline_checkbox("ReEntryActive", f"ReEntryActive_{k}", existing.get("ReEntryActive", False))

        with c3:
            Symbol = self._inline_text("Symbol", f"Symbol_{k}", existing.get("Symbol", ""))
            OrderLot = self._inline_number("OrderLot", f"OrderLot_{k}", existing.get("OrderLot", 1), 1)
            ExpiryNo = self._inline_number("ExpiryNo", f"ExpiryNo_{k}", existing.get("ExpiryNo", 0))

        with c4:
            sl_cost = self._inline_number("SL to Cost", f"sl_cost_{k}", existing.get("sl_to_cost_points", 0))
            sl_trail = self._inline_number("SL Trail", f"sl_trail_{k}", existing.get("sl_trail_points", 0))

        with c5:
            t1 = self._inline_number("Target 1", f"t1_{k}", existing.get("target_1st_140_points", 0))
            t2 = self._inline_number("Target 2", f"t2_{k}", existing.get("target_2nd_190_points", 0))

        st.divider()

        # -------- SAME ROW: ReEntry + LTP --------
        c6, c7, c8, c9, c10 = st.columns(5)

        with c6:
            ReEntryATP = st.number_input(
                "ReEntry ATP",
                value=float(existing.get("ReEntryATP", 0.0)),
                key=f"ReEntryATP_{k}"
            )

        with c7:
            ReEntryLevel = st.number_input(
                "ReEntry Level",
                value=int(existing.get("ReEntryLevel", 0)),
                step=1,
                key=f"ReEntryLevel_{k}"
            )

        with c8:
            ReEntrySide = st.selectbox(
                "ReEntry Side",
                ["BUY", "SELL"],
                index=0 if existing.get("ReEntrySide", "BUY") == "BUY" else 1,
                key=f"ReEntrySide_{k}"
            )

        with c9:
            LTP_931 = st.number_input(
                "LTP 9:31",
                value=float(existing.get("ltp_931", 0.0)),
                key=f"ltp_931_{k}"
            )

        with c10:
            LTP_931_time = st.text_input(
                "LTP 9:31 Time",
                value=existing.get("ltp_931_time", ""),
                key=f"ltp_931_time_{k}"
            )

        return {
            "Start": Start,
            "Pause": Pause,
            "Stop": Stop,
            "Active": Active,
            "FirstEntry": FirstEntry,
            "ReEntryActive": ReEntryActive,
            "Symbol": Symbol,
            "ExpiryNo": ExpiryNo,
            "OrderLot": OrderLot,
            "sl_to_cost_points": sl_cost,
            "sl_trail_points": sl_trail,
            "target_1st_140_points": t1,
            "target_2nd_190_points": t2,
            "ReEntryATP": ReEntryATP,
            "ReEntryLevel": ReEntryLevel,
            "ReEntrySide": ReEntrySide,
            "ltp_931": LTP_931,
            "ltp_931_time": LTP_931_time
        }


    # ---------------- ATP WRAPPER ----------------
    def atp_strategy_form(self, client_id):

        existing = self._load_existing(client_id) or {}
        k = client_id.replace(" ", "_")

        with st.form(f"atp_form_{k}"):
            inputs = self.atp_form(existing, k)
            submit = st.form_submit_button("Save Inputs")

        if submit:
            doc = {
                "StrategyID": self.STRATEGY_ID,
                **inputs,
                "updated_at": datetime.utcnow()
            }
            self._upsert(client_id, doc)
            st.success("ATP Strategy saved successfully")

    def run(self):

        st.title("Strategy Control Panel")

        col1, col2, col3 = st.columns([7.6, 1.2, 1.2])
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_resource.clear()
                st.rerun()
        with col3:
            if st.button("⬅️ Back", use_container_width=True):
                st.switch_page("pages/2_Strategy_Selection.py")

        if not st.session_state.get("logged_in"):
            st.error("❌ Please login first!")
            st.switch_page("app.py")
            return
            
        client_id = st.session_state.user_id
        
        self.STRATEGY_ID = st.session_state.get("selected_strategy")
        if not self.STRATEGY_ID:
            st.error("❌ Please select a strategy first!")
            st.switch_page("pages/2_Strategy_Selection.py")
            return

        st.markdown(f"**Client ID:** {client_id} | **Selected Strategy:** {self.STRATEGY_ID}")

        if self.STRATEGY_ID == "CST0005":
            self.straddle_shift_form(client_id)
        elif self.STRATEGY_ID == "CST0003":
            self.atp_strategy_form(client_id)
        else:
            st.error(f"❌ Unknown or unhandled Strategy ID: {self.STRATEGY_ID}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    StrategyApp().run()
