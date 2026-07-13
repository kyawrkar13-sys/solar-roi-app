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


def generator_calculation(fuel_per_hour, running_hours, diesel_price, solar_offset):
    fuel_used_day = fuel_per_hour * running_hours
    fuel_saved_day = fuel_used_day * (solar_offset / 100)

    saving_day = fuel_saved_day * diesel_price
    saving_month = saving_day * 30
    saving_year = saving_day * 365

    return {
        "fuel_saved_day": round(fuel_saved_day, 2),
        "saving_day": round(saving_day, 2),
        "saving_month": round(saving_month, 2),
        "saving_year": round(saving_year, 2)
    }


def financial_model(capex, annual_saving, om, life, discount):
    cashflow = []
    cumulative = -capex
    npv = -capex
    payback = None
    total = 0

    for y in range(1, life + 1):
        net = annual_saving * ((1.03) ** (y - 1)) - om

        cumulative += net
        npv += net / ((1 + discount) ** y)
        total += net

        if payback is None and cumulative >= 0:
            payback = y

        cashflow.append({
            "year": y,
            "cash": round(net, 2),
            "cumulative": round(cumulative, 2)
        })

    roi = ((total - capex) / capex) * 100 if capex > 0 else 0

    return {
        "payback": payback,
        "roi": round(roi, 2),
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
            float(d["battery"]),
            float(d["dod"]) / 100,
            float(d["efficiency"]) / 100,
            float(d["load"])
        )

        solar_saving = pv_year * float(d["tariff"])

        generator = generator_calculation(
            float(d["fuel_per_hour"]),
            float(d["running_hours"]),
            float(d["diesel_price"]),
            float(d["solar_offset"])
        )

        total_annual_saving = solar_saving + generator["saving_year"]

        finance = financial_model(
            float(d["capex"]),
            total_annual_saving,
            float(d["om"]),
            int(d["life"]),
            float(d["discount"]) / 100
        )

        return jsonify({
            "pv_generation": round(pv_year, 2),
            "battery": battery,
            "generator": generator,
            "solar_annual_saving": round(solar_saving, 2),
            "total_annual_saving": round(total_annual_saving, 2),
            "finance": finance
        })

    except (KeyError, TypeError, ValueError) as e:
        return jsonify({
            "error": str(e)
        }), 400


if name == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
