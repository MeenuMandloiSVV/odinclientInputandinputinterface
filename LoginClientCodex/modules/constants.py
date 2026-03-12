# Strategy Mapping
STRATEGY_MAPPING = {
    "CST0007": "Cash Profit Loop",
    "CST0005": "Straddle Shift",
    "CST0003": "ATP Strategy"
}

# Reverse mapping for easy lookup
STRATEGY_ID_BY_NAME = {v: k for k, v in STRATEGY_MAPPING.items()}

# Strategy Input Field Configurations
STRATEGY_FIELDS = {
    "CST0005": {  # Straddle Shift
        "name": "Straddle Shift",
        "fields": {
            "min_time": {"type": "time", "label": "Minimum Time", "default": "09:15:00"},
            "max_time": {"type": "time", "label": "Maximum Time", "default": "15:30:00"},
            "start_time": {"type": "time", "label": "Start Time", "default": "09:15:00"},
            "end_time": {"type": "time", "label": "End Time", "default": "15:15:00"},
            "qty_per_leg": {"type": "number", "label": "Quantity Per Leg", "default": 100},
            "premium_threshold": {"type": "number", "label": "Premium Threshold (%)", "default": 5.0},
            "enabled": {"type": "checkbox", "label": "Enable Strategy", "default": True},
        }
    },
    "CST0003": {  # ATP Strategy
        "name": "ATP Strategy",
        "fields": {
            "min_time": {"type": "time", "label": "Minimum Time", "default": "09:15:00"},
            "max_time": {"type": "time", "label": "Maximum Time", "default": "15:30:00"},
            "qty_per_trade": {"type": "number", "label": "Quantity Per Trade", "default": 50},
            "profit_target": {"type": "number", "label": "Profit Target (%)", "default": 2.0},
            "stop_loss": {"type": "number", "label": "Stop Loss (%)", "default": 1.0},
            "enabled": {"type": "checkbox", "label": "Enable Strategy", "default": True},
        }
    },
    "CST0007": {  # Cash Profit Loop
        "name": "Cash Profit Loop",
        "fields": {
            "min_time": {"type": "time", "label": "Minimum Time", "default": "09:15:00"},
            "max_time": {"type": "time", "label": "Maximum Time", "default": "15:30:00"},
            "lot_size": {"type": "number", "label": "Lot Size", "default": 1},
            "profit_target": {"type": "number", "label": "Daily Profit Target (₹)", "default": 5000},
            "enabled": {"type": "checkbox", "label": "Enable Strategy", "default": True},
        }
    }
}

# Odin API Endpoints (will be in secrets)
ODIN_ENDPOINTS = {
    "login": "/api/login",
    "logout": "/api/logout",
    "order": "/api/order"
}
