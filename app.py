[13/07/2026 19:42] Rkar Kyaw: import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def solar_generation(pv_kw, psh, pr):
    return pv_kw * psh * 365 * pr


def battery_calculation(capacity, dod, efficiency, load):
    usable = capacity * dod * efficiency
    coverage = (usable / load) * 100 if load > 0 else 0

    return {
        "usable_energy": round(usable, 2),
        "coverage": round(coverage, 2)
    }


def generator_calculation(
    fuel_consumption,
    diesel_price,
    generator_hours,
    generator_hours_saved
):
    saved_hours = min(generator_hours_saved, generator_hours)

    fuel_saved_day = fuel_consumption * saved_hours
    fuel_saved_month = fuel_saved_day * 30
    fuel_saved_year = fuel_saved_day * 365

    money_saved_day = fuel_saved_day * diesel_price
    money_saved_month = fuel_saved_month * diesel_price
    money_saved_year = fuel_saved_year * diesel_price

    return {
        "fuel_saved_day": round(fuel_saved_day, 2),
        "fuel_saved_month": round(fuel_saved_month, 2),
        "fuel_saved_year": round(fuel_saved_year, 2),
        "money_saved_day": round(money_saved_day, 2),
        "money_saved_month": round(money_saved_month, 2),
        "money_saved_year": round(money_saved_year, 2)
    }


def finance(capex, annual_saving, om, life):
    cumulative = -capex
    npv = -capex
    total_net_cashflow = 0
    payback = None
    discount_rate = 0.08

    for year in range(1, life + 1):
        yearly_saving = annual_saving * (1.03 ** (year - 1))
        net_cashflow = yearly_saving - om

        cumulative += net_cashflow
        total_net_cashflow += net_cashflow

        npv += net_cashflow / ((1 + discount_rate) ** year)

        if payback is None and cumulative >= 0:
            payback = year

    roi = (
        ((total_net_cashflow - capex) / capex) * 100
        if capex > 0
        else 0
    )

    return {
        "payback": payback,
        "roi": round(roi, 2),
        "npv": round(npv, 2)
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()

        pv_kw = float(data.get("pv_kw", 0))
        psh = float(data.get("psh", 0))
        pr = float(data.get("pr", 0)) / 100

        monthly_load = float(data.get("load", 0))
        battery_capacity = float(data.get("battery", 0))
        dod = float(data.get("dod", 0)) / 100
        efficiency = float(data.get("efficiency", 0)) / 100

        tariff = float(data.get("tariff", 0))
        capex = float(data.get("capex", 0))
        om = float(data.get("om", 0))
        life = int(float(data.get("life", 25)))

        fuel_consumption = float(
            data.get("fuel_consumption", 0)
        )

        diesel_price = float(
            data.get("diesel_price", 0)
        )

        generator_hours = float(
            data.get("generator_hours", 0)
        )

        generator_hours_saved = float(
            data.get("generator_hours_saved", 0)
        )

        if generator_hours_saved > generator_hours:
            return jsonify({
                "error": "Solar reduced generator hours cannot be greater than generator running hours."
            }), 400

        pv_generation = solar_generation(
            pv_kw,
            psh,
            pr
        )

        battery = battery_calculation(
            battery_capacity,
            dod,
            efficiency,
            monthly_load
        )

        generator = generator_calculation(
            fuel_consumption,
            diesel_price,
            generator_hours,
            generator_hours_saved
        )

        solar_saving_year = pv_generation * tariff
        generator_saving_year = generator["money_saved_year"]

        total_annual_saving = (
            solar_saving_year +
            generator_saving_year
        )

        finance_result = finance(
            capex,
            total_annual_saving,
            om,
            life
        )

        return jsonify({
[13/07/2026 19:42] Rkar Kyaw: "pv_generation": round(pv_generation, 2),

            "battery": battery,

            "generator": generator,

            "finance": finance_result
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


if name == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
