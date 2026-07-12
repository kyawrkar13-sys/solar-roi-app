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


def financial_model(capex, annual_saving, om, life):

    cashflow = []
    cumulative = -capex
    npv = -capex
    total = 0
    payback = None

    discount = 0.08

    for year in range(1, life + 1):

        net = annual_saving * (1.03 ** (year - 1)) - om

        cumulative += net
        npv += net / ((1 + discount) ** year)
        total += net

        if payback is None and cumulative >= 0:
            payback = year

        cashflow.append({
            "year": year,
            "cash": round(net, 2),
            "cumulative": round(cumulative, 2)
        })


    roi = ((total - capex) / capex) * 100 if capex else 0

    return {
        "payback": payback,
        "roi": round(roi, 2),
        "npv": round(npv, 2),
        "cashflow": cashflow
    }



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/calculate", methods=["POST"])
def calculate():

    try:
        d = request.get_json()

        pv_kw = float(d.get("pv_kw", 0))
        psh = float(d.get("psh", 0))
        pr = float(d.get("pr", 0)) / 100

        pv_year = solar_generation(
            pv_kw,
            psh,
            pr
        )


        battery = battery_calculation(
            float(d.get("battery", 0)),
            float(d.get("dod", 0)) / 100,
            float(d.get("efficiency", 0)) / 100,
            float(d.get("load", 0))
        )


        annual_saving = pv_year * float(d.get("tariff", 0))


        finance = financial_model(
            float(d.get("capex", 0)),
            annual_saving,
            float(d.get("om", 0)),
            int(d.get("life", 1))
        )


        return jsonify({
            "pv_generation": round(pv_year, 2),
            "battery": battery,
            "finance": finance
        })


    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



if name == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
