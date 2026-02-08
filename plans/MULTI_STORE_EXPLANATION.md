# Multi-Store Inventory Display - Explanation & Fix

## Issue Reported
**User Question**: "On our homepage, many ingredients show up multiple times. Why is that? They also have different stats."

## Root Cause (This is CORRECT Behavior!)

The "duplicate" ingredients are **not actually duplicates** - they represent the **same SKU at different stores**. This is the correct behavior for a multi-store inventory management system.

### Why Same Ingredient Shows Multiple Times:

1. **Multi-Store System**: Your system tracks 5 different Chipotle locations
   - Chipotle Athens Downtown
   - Chipotle Athens Eastside
   - Chipotle Athens West
   - Chipotle Athens North
   - Chipotle Athens South

2. **Each Store Has Independent Inventory**:
   - "Chicken" at Downtown store might have 50 units on hand
   - "Chicken" at Eastside store might have 20 units on hand
   - They're the same SKU but different inventory records

3. **Different Stats Per Location**:
   - **On Hand**: Different stock levels at each store
   - **Daily Demand**: Different sales velocity per location (Downtown might be busier)
   - **Days of Cover**: Based on local demand and stock
   - **Risk Level**: One store might be critical, another might be safe
   - **Confidence Score**: Based on local anomalies and cycle counts

## Example Scenario

```
Row 1: Chicken | Downtown  | 50 units | 25/day demand | 2.0 days cover | CRITICAL
Row 2: Chicken | Eastside  | 100 units | 15/day demand | 6.7 days cover | LOW
Row 3: Chicken | West      | 35 units | 20/day demand | 1.8 days cover | CRITICAL
```

All three rows are "Chicken", but they represent:
- **Different physical locations**
- **Different inventory levels**
- **Different demand patterns**
- **Different risk levels**

This is exactly what you'd see in a real multi-store inventory dashboard like NCR's system.

---

## UI Improvements Made

To make this clearer to users, I've implemented the following improvements:

### 1. **Made Store Name More Prominent** ✅
- Store name is now bold and larger font
- Added "Store ID: X" below store name for clarity
- Each row is visually clearer about which store it represents

### 2. **Added Store Filter Dropdown** ✅
```
Store: [All Stores ▼]
       Downtown
       Eastside
       West
       North
       South
```
- Users can now filter to see only ONE store at a time
- Default: "All Stores" (shows multi-store view)
- Selecting a store shows only that location's inventory

### 3. **Added Informational Note** ✅
```
💡 Multi-Store View: Each row represents inventory at a specific store. 
The same ingredient may appear multiple times because each store has different 
stock levels, demand, and risk. Use the store filter above to view a single location.
```

### 4. **Fixed Row Keys** ✅
- Changed from `key={idx}` to `key={store_id}-${sku_id}`
- Ensures proper React reconciliation
- Prevents UI glitches during filtering

---

## How to Use the New Features

### Viewing All Stores (Default)
1. Go to homepage
2. See all inventory across all stores
3. Notice same SKUs appear multiple times (one per store)
4. Each row shows store name clearly

### Viewing Single Store
1. Go to homepage
2. Click "Store" dropdown in filters section
3. Select a specific store (e.g., "Downtown")
4. Now you'll only see inventory for that one store
5. No more "duplicates" - each SKU appears once

### Understanding the Data
- **Same SKU, Different Store** = Different row = Correct!
- **Different Stats** = Each store has different conditions = Correct!
- **Transfer Recommendations** = Move inventory between these stores to balance stock

---

## Why This Design is Important

### For Chipotle Restaurant Managers
1. **Store Manager View**: Filter to their store to see only their inventory
2. **Regional Manager View**: See all stores to spot problems across locations
3. **Transfer Decisions**: Identify which stores have surplus and which need inventory

### For the Transfer Optimizer
The system uses this multi-store view to recommend transfers:
```
Example:
- Downtown: Chicken at 1.8 days cover (CRITICAL)
- Eastside: Chicken at 6.7 days cover (LOW risk)
→ Recommendation: Transfer 30 units from Eastside to Downtown
```

Without seeing both stores, you couldn't make smart transfer decisions!

---

## Demo Talking Points (For Judges)

**If a judge asks about duplicates:**

> "Great observation! These aren't duplicates - each row represents inventory at a specific store. 
> Notice 'Chicken' appears at Downtown, Eastside, West, etc. - each with different stock levels and risk.
> 
> This is the key to our **Cross-Store Transfer Optimizer**: By tracking each store independently, 
> we can identify that Eastside has surplus chicken while Downtown is running out, and recommend 
> a transfer between them.
> 
> You can use the store filter [point to dropdown] to view just one location, or see all stores 
> for regional management. This multi-store view is how real inventory systems like NCR's work."

**Turn it into a feature demo:**
> "Let me show you something cool - see how Downtown has 1.8 days of chicken left (critical), 
> but Eastside has 6.7 days (plenty)? Our transfer optimizer will automatically suggest moving 
> chicken from Eastside to Downtown, preventing a stockout without placing a new order. 
> Click 'View Transfers' to see the recommendation!"

---

## Technical Details

### Frontend Changes
- **File**: `frontend/src/app/page.tsx`
- **Added**: Store filter dropdown state management
- **Added**: Store list extraction from API response
- **Updated**: Filter UI with store selector
- **Added**: Info note explaining multi-store behavior
- **Improved**: Store column styling (bold, two-line display)
- **Fixed**: React keys for proper reconciliation

### Backend (No Changes Needed)
- Current implementation is correct
- Returns one row per store-SKU combination
- Store filter already supported via `store_id` query param

### Data Model (Correct)
```sql
inventory_snapshots (
    store_id,    -- Different for each location
    sku_id,      -- Same SKU across stores
    on_hand,     -- Different per store
    ...
)
```

---

## Testing Checklist

- [x] View all stores - multiple entries for same SKU
- [x] Select single store - only one entry per SKU
- [x] Store column shows clear location name
- [x] Info note explains multi-store behavior
- [x] Filter by store works correctly
- [x] "All Stores" option resets filter
- [x] Stats differ between same SKU at different stores

---

## Status

✅ **FIXED** - UI now clearly indicates multi-store inventory view
✅ **ENHANCED** - Added store filter for single-location view
✅ **DOCUMENTED** - Info note explains behavior to users
✅ **DEMO READY** - Can now explain this as a feature, not a bug!

---

**Last Updated**: 2026-02-07
**Status**: Complete and Demo Ready
