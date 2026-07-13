import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def solar_generation(pv_kw, psh, pr):
    return pv_kw * psh * 365 * pr

def battery_calculation(capacity, dod, efficiency, monthly_load):
    usable = capacity * dod * efficiency
    coverage = (usable / monthly_load) * 100 if monthly_load > 0 else 0
    return {
        "usable_energy": round(usable, 2),
        "monthly_coverage": round(coverage, 2)
    }

def financial_model(capex, annual_saving, om, life, discount):
    cashflow = []
    cumulative = -capex
    npv = -capex
    payback = None
    total = 0
    
    prev_cumulative = -capex

    for y in range(1, life + 1):
        net = annual_saving * ((1.03) ** (y - 1)) - om
        
        # Payback calculation: Linear interpolation
        if payback is None and (cumulative + net) >= 0:
            # Formula: Year before + (abs(prev_cumulative) / current_year_net)
            payback = (y - 1) + (abs(prev_cumulative) / net)
        
        prev_cumulative = cumulative
        cumulative += net
        npv += net / ((1 + discount) ** y)
        total += net

        cashflow.append({
            "year": y,
            "cash": round(net, 2),
            "cumulative": round(cumulative, 2)
        })

    return {
        "payback": round(payback, 2) if payback else None,
        "roi": round(((total - capex) / capex) * 100, 2) if capex > 0 else 0,
        "npv": round(npv, 2),
        "cashflow": cashflow
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/calculate")
def calculate():
    try:
        d = request.get_json()
        
        pv_kw = float(d["pv_kw"])
        psh = float(d["psh"])
        pr = float(d["pr"]) / 100
        
        pv_year = solar_generation(pv_kw, psh, pr)
        
        battery = battery_calculation(
            float(d["battery"]), float(d["dod"]) / 100,
            float(d["efficiency"]) / 100, float(d["load"])
        )
        
        annual_saving = pv_year * float(d["tariff"])
        
        finance = financial_model(
            float(d["capex"]), annual_saving, float(d["om"]),
            int(d["life"]), float(d["discount"]) / 100
        )
        
        return jsonify({"pv_generation": round(pv_year, 2), "battery": battery, "finance": finance})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if name == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
