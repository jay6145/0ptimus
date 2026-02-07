"""
Demo data generator with realistic patterns and anomalies
"""
import random
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from ..models import (
    Store, SKU, InventorySnapshot, SalesDaily, ReceiptsDaily,
    Transfer, CycleCount, Supplier, SKUSupplier, AnomalyEvent,
    TransferRecommendation, StoreDistance
)
from ..database import SessionLocal, engine, Base
import math


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def generate_demo_data(
    num_stores: int = 5,
    num_skus: int = 200,
    days_history: int = 60
):
    """
    Generate comprehensive demo data with realistic patterns
    """
    print("🚀 Starting demo data generation...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("🗑️  Clearing existing data...")
        db.query(TransferRecommendation).delete()
        db.query(AnomalyEvent).delete()
        db.query(CycleCount).delete()
        db.query(Transfer).delete()
        db.query(ReceiptsDaily).delete()
        db.query(SalesDaily).delete()
        db.query(InventorySnapshot).delete()
        db.query(SKUSupplier).delete()
        db.query(Supplier).delete()
        db.query(SKU).delete()
        db.query(StoreDistance).delete()
        db.query(Store).delete()
        db.commit()
        
        # 1. Create Stores
        print(f"🏪 Creating {num_stores} stores...")
        store_data = [
            {"name": "Atlanta Store", "location": "Atlanta, GA", "lat": 33.7490, "lon": -84.3880},
            {"name": "Boston Store", "location": "Boston, MA", "lat": 42.3601, "lon": -71.0589},
            {"name": "Chicago Store", "location": "Chicago, IL", "lat": 41.8781, "lon": -87.6298},
            {"name": "Denver Store", "location": "Denver, CO", "lat": 39.7392, "lon": -104.9903},
            {"name": "Seattle Store", "location": "Seattle, WA", "lat": 47.6062, "lon": -122.3321},
        ]
        
        stores = []
        for i in range(min(num_stores, len(store_data))):
            store = Store(**store_data[i])
            db.add(store)
            stores.append(store)
        db.commit()
        
        # Calculate store distances
        print("📏 Calculating store distances...")
        for i, store1 in enumerate(stores):
            for j, store2 in enumerate(stores):
                if i != j:
                    distance = calculate_distance(
                        store1.latitude, store1.longitude,
                        store2.latitude, store2.longitude
                    )
                    cost = distance * 0.05  # $0.05 per km
                    
                    store_dist = StoreDistance(
                        from_store_id=store1.id,
                        to_store_id=store2.id,
                        distance_km=round(distance, 2),
                        transfer_cost=round(cost, 2)
                    )
                    db.add(store_dist)
        db.commit()
        
        # 2. Create SKUs
        print(f"📦 Creating {num_skus} SKUs...")
        categories = {
            "Beverages": 40,
            "Snacks": 35,
            "Dairy": 25,
            "Produce": 20,
            "Frozen": 20,
            "Bakery": 15,
            "Meat": 15,
            "Household": 30
        }
        
        sku_names = {
            "Beverages": ["Coca-Cola 12pk", "Pepsi 12pk", "Orange Juice 64oz", "Water 24pk", "Energy Drink"],
            "Snacks": ["Potato Chips", "Pretzels", "Cookies", "Crackers", "Candy Bar"],
            "Dairy": ["Milk 1gal", "Yogurt 6pk", "Cheese Block", "Butter 1lb", "Eggs Dozen"],
            "Produce": ["Bananas", "Apples", "Lettuce", "Tomatoes", "Carrots"],
            "Frozen": ["Ice Cream", "Frozen Pizza", "Frozen Vegetables", "Frozen Chicken", "Frozen Fries"],
            "Bakery": ["Bread Wheat", "Bread White", "Bagels", "Muffins", "Donuts"],
            "Meat": ["Ground Beef", "Chicken Breast", "Pork Chops", "Steak", "Bacon"],
            "Household": ["Paper Towels", "Toilet Paper", "Dish Soap", "Laundry Detergent", "Trash Bags"]
        }
        
        skus = []
        sku_count = 0
        for category, count in categories.items():
            base_names = sku_names.get(category, ["Product"])
            for i in range(count):
                if sku_count >= num_skus:
                    break
                    
                name = f"{random.choice(base_names)} {random.choice(['Brand A', 'Brand B', 'Brand C', 'Generic'])}"
                cost = round(random.uniform(1.0, 20.0), 2)
                price = round(cost * random.uniform(1.3, 2.0), 2)
                is_perishable = category in ["Produce", "Dairy", "Meat", "Bakery"]
                
                sku = SKU(
                    name=name,
                    category=category,
                    unit="each",
                    cost=cost,
                    price=price,
                    is_perishable=is_perishable
                )
                db.add(sku)
                skus.append(sku)
                sku_count += 1
        
        db.commit()
        print(f"✅ Created {len(skus)} SKUs")
        
        # 3. Create Suppliers
        print("🚚 Creating suppliers...")
        suppliers = []
        supplier_names = ["Sysco", "US Foods", "Coca-Cola Distributor", "PepsiCo", "Local Farms"]
        for name in supplier_names:
            supplier = Supplier(
                name=name,
                avg_lead_time_days=random.randint(2, 7),
                lead_time_std_days=random.randint(1, 3)
            )
            db.add(supplier)
            suppliers.append(supplier)
        db.commit()
        
        # Link SKUs to suppliers
        for sku in skus:
            supplier = random.choice(suppliers)
            sku_supp = SKUSupplier(
                sku_id=sku.id,
                supplier_id=supplier.id,
                case_pack=random.choice([6, 12, 24, 48]),
                min_order_qty=random.choice([1, 2, 5, 10])
            )
            db.add(sku_supp)
        db.commit()
        
        # 4. Generate historical data
        print(f"📊 Generating {days_history} days of sales history...")
        
        start_date = datetime.now().date() - timedelta(days=days_history)
        
        # Track inventory for each store/sku
        inventory_tracker = {}
        
        for store in stores:
            for sku in skus:
                # Initialize inventory
                initial_inventory = random.randint(20, 100)
                inventory_tracker[(store.id, sku.id)] = initial_inventory
                
                # Base demand varies by category and store
                base_demand = {
                    "Beverages": random.uniform(5, 15),
                    "Snacks": random.uniform(4, 12),
                    "Dairy": random.uniform(3, 10),
                    "Produce": random.uniform(2, 8),
                    "Frozen": random.uniform(2, 6),
                    "Bakery": random.uniform(3, 9),
                    "Meat": random.uniform(2, 7),
                    "Household": random.uniform(1, 5)
                }.get(sku.category, 3)
                
                # Store multiplier (some stores are busier)
                store_multiplier = 1.0 + (store.id % 3) * 0.2
                base_demand *= store_multiplier
                
                for day_offset in range(days_history):
                    current_date = start_date + timedelta(days=day_offset)
                    
                    # Weekday vs weekend pattern
                    is_weekend = current_date.weekday() >= 5
                    weekend_multiplier = 1.3 if is_weekend else 1.0
                    
                    # Calculate sales with noise
                    daily_sales = int(base_demand * weekend_multiplier * random.uniform(0.7, 1.3))
                    daily_sales = max(0, min(daily_sales, inventory_tracker[(store.id, sku.id)]))
                    
                    # Record sales
                    if daily_sales > 0:
                        sales = SalesDaily(
                            store_id=store.id,
                            sku_id=sku.id,
                            ts_date=current_date,
                            qty_sold=daily_sales
                        )
                        db.add(sales)
                    
                    # Update inventory
                    inventory_tracker[(store.id, sku.id)] -= daily_sales
                    
                    # Receive shipments periodically
                    receipts = 0
                    if random.random() < 0.15:  # 15% chance of receipt
                        receipts = int(base_demand * random.uniform(5, 10))
                        receipt = ReceiptsDaily(
                            store_id=store.id,
                            sku_id=sku.id,
                            ts_date=current_date,
                            qty_received=receipts
                        )
                        db.add(receipt)
                        inventory_tracker[(store.id, sku.id)] += receipts
                    
                    # Record inventory snapshot
                    snapshot = InventorySnapshot(
                        store_id=store.id,
                        sku_id=sku.id,
                        ts_date=current_date,
                        on_hand=max(0, inventory_tracker[(store.id, sku.id)])
                    )
                    db.add(snapshot)
        
        db.commit()
        print("✅ Sales history generated")
        
        # 5. Inject anomalies
        print("⚠️  Injecting anomalies...")
        anomaly_count = 0
        
        # Select random store/sku combinations for anomalies
        anomaly_targets = random.sample(
            [(s.id, sk.id) for s in stores for sk in random.sample(skus, 10)],
            min(15, len(stores) * 10)
        )
        
        for store_id, sku_id in anomaly_targets:
            # Pick a random recent date
            anomaly_date = start_date + timedelta(days=random.randint(days_history - 30, days_history - 1))
            
            # Get the inventory snapshot
            snapshot = db.query(InventorySnapshot).filter(
                InventorySnapshot.store_id == store_id,
                InventorySnapshot.sku_id == sku_id,
                InventorySnapshot.ts_date == anomaly_date
            ).first()
            
            if snapshot:
                # Create unexplained drop
                residual = -random.randint(5, 20)
                severity = "critical" if residual < -15 else "high" if residual < -10 else "medium"
                
                explanation = f"Unexplained inventory drop of {abs(residual)} units. Possible shrink or unrecorded transaction."
                
                anomaly = AnomalyEvent(
                    store_id=store_id,
                    sku_id=sku_id,
                    ts_date=anomaly_date,
                    residual=residual,
                    severity=severity,
                    explanation_hint=explanation
                )
                db.add(anomaly)
                anomaly_count += 1
        
        db.commit()
        print(f"✅ Injected {anomaly_count} anomalies")
        
        # 6. Generate cycle counts
        print("📋 Generating cycle counts...")
        count_coverage = 0.2  # 20% of SKUs counted
        
        for store in stores:
            counted_skus = random.sample(skus, int(len(skus) * count_coverage))
            for sku in counted_skus:
                count_date = start_date + timedelta(days=random.randint(0, days_history - 1))
                
                # Get expected inventory
                snapshot = db.query(InventorySnapshot).filter(
                    InventorySnapshot.store_id == store.id,
                    InventorySnapshot.sku_id == sku.id,
                    InventorySnapshot.ts_date == count_date
                ).first()
                
                if snapshot:
                    # Count might differ slightly
                    counted = snapshot.on_hand + random.randint(-3, 3)
                    counted = max(0, counted)
                    
                    cycle_count = CycleCount(
                        store_id=store.id,
                        sku_id=sku.id,
                        ts_date=count_date,
                        counted_qty=counted
                    )
                    db.add(cycle_count)
        
        db.commit()
        print("✅ Cycle counts generated")
        
        # 7. Create transfer opportunities
        print("🔄 Creating transfer scenarios...")
        # Find SKUs with imbalanced inventory
        today = datetime.now().date()
        
        for sku in random.sample(skus, min(20, len(skus))):
            store_inventories = []
            for store in stores:
                snapshot = db.query(InventorySnapshot).filter(
                    InventorySnapshot.store_id == store.id,
                    InventorySnapshot.sku_id == sku.id,
                    InventorySnapshot.ts_date == today - timedelta(days=1)
                ).first()
                
                if snapshot:
                    store_inventories.append((store.id, snapshot.on_hand))
            
            if len(store_inventories) >= 2:
                # Sort by inventory level
                store_inventories.sort(key=lambda x: x[1])
                
                # If there's significant imbalance, create recommendation
                if store_inventories[-1][1] > store_inventories[0][1] * 3:
                    from_store_id = store_inventories[-1][0]
                    to_store_id = store_inventories[0][0]
                    qty = min(20, store_inventories[-1][1] // 4)
                    
                    recommendation = TransferRecommendation(
                        from_store_id=from_store_id,
                        to_store_id=to_store_id,
                        sku_id=sku.id,
                        qty=qty,
                        urgency_score=random.uniform(0.6, 0.95),
                        rationale=f"Receiver has low stock ({store_inventories[0][1]} units), donor has excess ({store_inventories[-1][1]} units). Transfer prevents stockout.",
                        status="pending"
                    )
                    db.add(recommendation)
        
        db.commit()
        print("✅ Transfer recommendations created")
        
        # Summary
        stats = {
            "stores": len(stores),
            "skus": len(skus),
            "days_history": days_history,
            "total_snapshots": db.query(InventorySnapshot).count(),
            "total_sales": db.query(SalesDaily).count(),
            "total_receipts": db.query(ReceiptsDaily).count(),
            "anomalies": db.query(AnomalyEvent).count(),
            "cycle_counts": db.query(CycleCount).count(),
            "transfer_recommendations": db.query(TransferRecommendation).count()
        }
        
        print("\n" + "="*50)
        print("✅ DEMO DATA GENERATION COMPLETE!")
        print("="*50)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("="*50 + "\n")
        
        return stats
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating demo data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_demo_data()
