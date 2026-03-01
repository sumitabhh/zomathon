# KPT Signal Intelligence Platform — QuantumTrio

**Zomathon Hackathon · Problem Statement 1**
*Improving Kitchen Prep Time (KPT) Prediction to Optimize Rider Assignment and Customer ETA at Zomato*

---

## Team
| Role | Name |
|------|------|
| Team Leader | Pranamika Kalita |
| Member | Porinistha Barooa |
| Member | Sumitabh Shyamal |

---

## Quick Start

### Prerequisites
```bash
pip install flask pymongo pandas numpy scikit-learn python-dateutil
```

### Run (Simulated Data)
```bash
cd kpt-mvp
python run.py
# Open: http://localhost:5000
```

### Run (Live MongoDB)
```bash
USE_MONGODB=true python run.py
```

---

## Architecture Overview

```
Layer 1: Data Ingestion
  ├── Order Events (Kafka)
  ├── Rider GPS Events
  ├── Merchant Mx App (FOR signals)
  └── External Enrichment APIs

Layer 2: Signal Enrichment & Bias Detection
  ├── Time Alignment Engine
  ├── Merchant Bias Profiler
  ├── Prep Gap Engine (rider_arrival - merchant_FOR)
  └── Idle Signal Analyzer

Layer 3: Kitchen Rush Intelligence
  ├── Load Index (active_orders / staff_count)
  ├── City Scale Adapter (Tier 1/2/3)
  ├── Rush Proxy Engine
  └── External Signal Injector (weather, festivals)

Layer 4: Feature Engineering & Confidence Scoring
  ├── Reliability Score (0-1 per restaurant)
  ├── Confidence-Weighted KPT
  └── Feature Store Writer

Layer 5: Downstream Impact
  ├── Rider Dispatch Engine
  ├── Customer ETA Service
  └── Operations Dashboard
```

## Core Innovation: Signal Correction Formula

```python
# Step 1: Detect Prep Gap
prep_gap = rider_arrival_time - merchant_FOR_time

# Step 2: Classify Bias
if abs(for_bias) < 1.5:       → RELIABLE
if prep_gap ≈ 0 consistently  → RIDER-TRIGGERED (mark when rider arrives)
if for_bias > 3 consistently  → SYSTEMATIC DELAY

# Step 3: Reliability Weight
reliability_score = normalize(|avg_bias| × 0.6 + avg_idle × 0.4)
weight = 1 - (reliability_score × 0.3)

# Step 4: Corrected KPT
corrected_kpt = raw_kpt × weight - (avg_bias × 0.7)
```

## MongoDB Schema

### kpt-data collection
```json
{
  "order_id": "uuid",
  "restaurant_id": 415,
  "order_time": "06-02-2026 22.54",
  "confirm_time": "06-02-2026 22.55",
  "merchant_ready_time": "2026-02-06 23:14:24",
  "actual_ready_time": "2026-02-06 23:10:24",
  "rider_assigned_time": "06-02-2026 23.03",
  "rider_arrival_time": "06-02-2026 23.13",
  "pickup_time": "2026-02-06 23:13:04",
  "active_orders": 8,
  "staff_count": 3,
  "peak_hour": 0,
  "distance_km": 4.58
}
```

### restaurant-data collection
```json
{
  "restaurant_id": 1,
  "restaurant_name": "Shree Mandir",
  "cuisine_type": "Chettinad",
  "rating": 2.9,
  "city": "Ahmedabad",
  "state": "Gujarat",
  ...
}
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/overview` | System KPIs and team info |
| `GET /api/restaurants` | Paginated restaurant profiles with bias |
| `GET /api/restaurant/:id` | Single restaurant detail + hourly pattern |
| `GET /api/city-analytics` | City-level KPT and signal analysis |
| `GET /api/hourly-patterns` | 24-hour signal degradation patterns |
| `GET /api/signal-flow` | Sample signal correction timeline |
| `GET /api/rush-index` | Kitchen rush index per restaurant |
| `GET /api/bias-heatmap` | City-wise bias distribution |
| `GET /api/simulation` | Before/after correction simulation |
| `POST /api/predict-kpt` | Real-time KPT prediction |

## Expected Business Impact

| Metric | Projected Improvement |
|--------|-----------------------|
| ETA P50 Error | ↓ ~35% |
| ETA P90 Error | ↓ ~32% |
| Rider Idle Time | ↓ ~31% |
| Order Cancellations | ↓ ~14% |
| FOR Signal Reliability | ↑ ~35% |

## Key Differentiators from Competitors

1. **Signal-layer first** — fixes data quality before the model, no model redesign needed
2. **Per-restaurant bias profiling** — clusters all 300K+ merchants into bias types automatically
3. **Kitchen rush proxy** — captures dine-in load without hardware using observable Zomato signals
4. **National scale adapter** — Tier 1/2/3 city normalization for India-wide deployment
5. **Confidence-weighted KPT** — feeds reliability scores directly into feature vector

## Project Structure

```
kpt-mvp/
├── backend/
│   ├── app.py              # Flask API server + analytics engine
│   └── mongo_connector.py  # MongoDB integration module
├── frontend/
│   └── index.html          # Full SPA dashboard (Chart.js)
├── requirements.txt
├── run.py                  # Startup script
└── README.md
```
