"""
MongoDB Integration Module — QuantumTrio
Connects to real Zomathon MongoDB database

Usage: Set USE_MONGODB=true environment variable to switch from
       simulated data to live MongoDB data.

Database: zomathon
Collections: kpt-data, restaurant-data
"""

import os
from datetime import datetime
from dateutil import parser as dateparser

MONGO_URL = "mongodb://root:viuVisi5ENJxWxbMr1drz7z0B10Pc87KnpYEMbEIu011bw9B6eCGvTWB5LnM9ZiT@31.97.232.35:27020/?directConnection=true"


def get_mongo_client():
    """Get pymongo client"""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        return client
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        return None


def parse_dt(val):
    """Parse any datetime format"""
    if isinstance(val, datetime):
        return val
    try:
        return dateparser.parse(str(val))
    except:
        return None


def load_restaurants_from_mongo(client):
    """Load restaurant data from MongoDB"""
    db = client["zomathon"]
    restaurants = list(db["restaurant-data"].find({}, {"_id": 0}))
    print(f"📦 Loaded {len(restaurants)} restaurants from MongoDB")
    return restaurants


def load_kpt_orders_from_mongo(client, limit=10000):
    """Load KPT order data from MongoDB and compute derived signals"""
    db = client["zomathon"]
    raw_orders = list(db["kpt-data"].find({}, {"_id": 0}).limit(limit))
    print(f"📦 Loaded {len(raw_orders)} raw orders from MongoDB")

    enriched = []
    for o in raw_orders:
        try:
            order_time = parse_dt(o.get("order_time"))
            confirm_time = parse_dt(o.get("confirm_time"))
            merchant_ready = parse_dt(o.get("merchant_ready_time"))
            actual_ready = parse_dt(o.get("actual_ready_time"))
            rider_assigned = parse_dt(o.get("rider_assigned_time"))
            rider_arrival = parse_dt(o.get("rider_arrival_time"))
            pickup_time = parse_dt(o.get("pickup_time"))

            if not all([confirm_time, merchant_ready, actual_ready, rider_arrival, pickup_time]):
                continue

            # Derived signals
            true_kpt = (actual_ready - confirm_time).total_seconds() / 60
            marked_kpt = (merchant_ready - confirm_time).total_seconds() / 60
            for_bias = (merchant_ready - actual_ready).total_seconds() / 60
            prep_gap = (rider_arrival - merchant_ready).total_seconds() / 60
            rider_idle = max(0, (pickup_time - rider_arrival).total_seconds() / 60)
            active_orders = o.get("active_orders", 5)
            staff_count = o.get("staff_count", 3)
            load_index = active_orders / max(staff_count, 1)
            hour = confirm_time.hour if confirm_time else 12

            enriched.append({
                "order_id": str(o.get("order_id", "")),
                "restaurant_id": int(o.get("restaurant_id", 0)),
                "order_time": str(order_time),
                "confirm_time": str(confirm_time),
                "merchant_ready_time": str(merchant_ready),
                "actual_ready_time": str(actual_ready),
                "rider_assigned_time": str(rider_assigned),
                "rider_arrival_time": str(rider_arrival),
                "pickup_time": str(pickup_time),
                "active_orders": active_orders,
                "staff_count": staff_count,
                "peak_hour": int(o.get("peak_hour", 0)),
                "distance_km": float(o.get("distance_km", 3.0)),
                "true_kpt_minutes": round(true_kpt, 2),
                "marked_kpt_minutes": round(marked_kpt, 2),
                "for_bias_minutes": round(for_bias, 2),
                "prep_gap_minutes": round(prep_gap, 2),
                "rider_idle_minutes": round(rider_idle, 2),
                "load_index": round(load_index, 2),
                "hour_of_day": hour,
                # Bias type derived from prep_gap
                "merchant_bias_type": classify_bias(for_bias, prep_gap),
                "city": "Unknown",  # Will be enriched from restaurant-data join
            })
        except Exception as e:
            continue

    print(f"✅ Enriched {len(enriched)} orders with derived signals")
    return enriched


def classify_bias(for_bias, prep_gap):
    """Classify merchant bias type from signal patterns"""
    if abs(for_bias) < 1.5:
        return "reliable"
    elif abs(prep_gap) < 0.5 and for_bias > 2:
        return "rider_triggered"
    elif for_bias > 3:
        return "systematic_delay"
    else:
        return "peak_manipulator"


def enrich_orders_with_restaurants(orders, restaurants):
    """Join restaurant city/metadata into orders"""
    rest_map = {r["restaurant_id"]: r for r in restaurants}
    for o in orders:
        rest = rest_map.get(o["restaurant_id"], {})
        o["restaurant_name"] = rest.get("restaurant_name", f"Restaurant #{o['restaurant_id']}")
        o["city"] = rest.get("city", "Unknown")
        o["cuisine_type"] = rest.get("cuisine_type", "Unknown")
    return orders


if __name__ == "__main__":
    client = get_mongo_client()
    if client:
        rests = load_restaurants_from_mongo(client)
        orders = load_kpt_orders_from_mongo(client)
        orders = enrich_orders_with_restaurants(orders, rests)
        print(f"\n📊 Sample enriched order:")
        import json
        print(json.dumps(orders[0] if orders else {}, indent=2, default=str))
