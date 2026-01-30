# Minimal Architecture - Performance Guide

## 🎯 What Changed

### Before (app.py)
- **4900+ lines** - monolithic file
- **All modules imported** at top level
- **All tabs rendered** simultaneously
- **Maps/charts auto-loaded** on every refresh
- **Result:** 10-30 second startup, continuous spinner

### After (app_minimal.py + ui/)
- **120 lines** in main file
- **Lazy imports** - only load what's needed
- **One tab at a time** - only render active tab
- **Optional features** - maps/charts behind buttons
- **Result:** < 5 second startup target

## 🏗️ Architecture

```
app_minimal.py (120 lines)
├── @st.cache_resource: get_shipment_data()  # Load ONCE per session
├── Tab: Sender → ui/sender.py (lazy import)
├── Tab: Manager → ui/manager.py (lazy import)
├── Tab: Supervisor → ui/supervisor.py (lazy import)
├── Tab: Viewer → ui/viewer.py (lazy import)
├── Tab: Receiver → ui/receiver.py (lazy import)
└── COO Dashboard (behind button) → ui/coo.py (lazy import)
```

## 🚀 Performance Rules

### 1. Main File < 200 Lines ✅
- `app_minimal.py`: 120 lines
- Only tab navigation and data caching

### 2. NO Global Imports ✅
```python
# ❌ OLD: Imports at top
import pandas as pd
import plotly.express as px

# ✅ NEW: Lazy imports when needed
def render_analytics():
    import pandas as pd  # Only when called
    import plotly.express as px
```

### 3. NO Auto-Load Heavy UI ✅
```python
# ❌ OLD: Map loads on startup
render_map(shipments)

# ✅ NEW: Map behind button
if st.button("Load Map"):
    render_map(shipments)
```

### 4. Load Data ONCE ✅
```python
@st.cache_resource
def get_shipment_data():
    """Loads ONCE per session, never again"""
    return get_all_shipments_by_state()
```

### 5. Render ONE Area at a Time ✅
```python
# Only active tab imports its module
with tabs[0]:  # Sender
    from ui.sender import render_sender  # Import ONLY when tab active
    render_sender()
```

## 📦 Module Structure

### ui/sender.py (~70 lines)
- Form for creating shipments
- "Load My Shipments" button (NOT auto-loaded)
- Limit: 10 recent shipments

### ui/manager.py (~90 lines)
- Simple metrics (count-based only)
- Approval interface (max 20 shipments)
- Analytics behind "Load Analytics Dashboard" button

### ui/supervisor.py (~50 lines)
- Dispatch interface (max 15 shipments)
- Two-transition workflow (approve → in-transit)
- No heavy computation

### ui/viewer.py (~70 lines)
- Search by shipment ID
- Timeline behind button (lazy load history)
- Recent shipments behind button (max 50)

### ui/receiver.py (~60 lines)
- Acknowledgment interface (max 20 arrivals)
- In-transit view behind button (max 30)
- Simple metrics only

### ui/coo.py (~130 lines)
- Basic metrics (count-based)
- ALL analytics behind buttons:
  - State distribution chart
  - Geographic map
  - Detailed table
- Heavy imports (pandas, plotly, pydeck) ONLY when features used

## 🎯 Why This Works

### Streamlit Execution Model
Streamlit re-executes the **ENTIRE script** on every interaction:
- Button click → Full rerun
- Text input → Full rerun
- Tab switch → Full rerun

### The Problem
A 4900-line monolith means:
- All 4900 lines execute on EVERY interaction
- All imports load on EVERY execution
- All tabs render on EVERY rerun
- Result: 10-30 second lag

### The Solution
Minimal main file + lazy modules:
- Only 120 lines execute on every interaction
- Only active tab imports its module
- Heavy features behind buttons
- Result: < 5 second startup

## 🧪 Testing

```bash
# Run minimal app
streamlit run app_minimal.py

# Expected results:
# ✅ Startup < 5 seconds
# ✅ No continuous spinner
# ✅ Tab switching instant
# ✅ Forms work correctly
# ✅ Analytics load only when requested
```

## 📊 Performance Comparison

| Metric | Old (app.py) | New (app_minimal.py) |
|--------|--------------|----------------------|
| Main file lines | 4900+ | 120 |
| Startup time | 10-30s | < 5s target |
| Imports on load | All modules | None (lazy) |
| Tabs rendered | All 6 | 1 (active) |
| Maps/charts | Auto-load | Behind buttons |
| Data loading | Every rerun | Once per session |

## 🔧 Maintenance

### Adding New Features
1. Keep main file minimal
2. Add feature to appropriate ui/ module
3. Put heavy features behind buttons
4. Use lazy imports for heavy libraries

### Performance Rules
- List views: Max 20 items
- Search results: Max 50 items
- Maps: Max 100 data points
- Tables: Max 100 rows
- Cache data with @st.cache_resource
- Put analytics behind buttons

## 🎓 Key Lessons

1. **Streamlit is NOT a traditional web framework**
   - No background execution
   - No persistent server memory
   - Full script rerun on every interaction

2. **Large apps WILL ALWAYS LAG**
   - Solution: Radical minimization
   - Keep main file tiny
   - Lazy load everything

3. **Optional features are performance wins**
   - Don't auto-load maps/charts
   - Let users request heavy UI
   - Default to simple, fast UI

4. **Data loading is expensive**
   - Cache with @st.cache_resource
   - Load once per session
   - Never reload on every rerun

## 🚦 Status

- ✅ Created app_minimal.py (120 lines)
- ✅ Created ui/ modules (all 6)
- ✅ Implemented lazy imports
- ✅ Put heavy features behind buttons
- ⏳ Testing required
- ⏳ Production deployment

## 📝 Next Steps

1. Test app_minimal.py
2. Verify < 5s startup
3. Test all workflows (create, approve, dispatch, etc.)
4. Monitor performance in production
5. Iterate based on real usage
