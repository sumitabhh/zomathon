"""
QuantumTrio KPT Signal Intelligence Platform
Run: python run.py
Open: http://localhost:5000
"""

import os
import sys

print("""
+--------------------------------------------------------------+
|      KPT Signal Intelligence Platform  -  QuantumTrio       |
|      Zomathon  .  Problem Statement 1                        |
+--------------------------------------------------------------+
|  Team Leader : Pranamika Kalita                              |
|  Members     : Porinistha Barooa  .  Sumitabh Shyamal        |
+--------------------------------------------------------------+
""")

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, BACKEND_DIR)

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server running at: http://localhost:{port}")
    print("-" * 60)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
