import os

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def solar_generation(pv_kw, psh, pr):

    return pv_kw * psh * 365 * pr

def battery_calculation(capacity, dod, efficiency, load):

    usable = capacity * dod * efficiency

    coverage = (usable / load) * 100 if load else 0

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

def finance(capex, saving, om, life):

    cumulative = -capex

    npv = -capex

    total = 0

    payback = None

    discount = 0.08

    for year in range(1, life + 1):

        net = saving * (1.03 ** (year - 1)) - om

        cumulative += net

        npv += net / ((1 + discount) ** year)

        total += net

        if payback is None and cumulative >= 0:

            payback = year

    roi = ((total - capex) / capex) * 100 if capex else 0

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

        d = request.get_json()

        pv_kw = float(d["pv_kw"])

        psh = float(d["psh"])

        pr = float(d["pr"]) / 100

        pv = solar_generation(pv_kw, psh, pr)

        battery = battery_calculation(

            float(d["battery"]),

            float(d["dod"]) / 100,

            float(d["efficiency"]) / 100,

            float(d["load"])

        )

        solar_saving = pv * float(d["tariff"])

        generator = generator_calculation(

            float(d.get("fuel_consumption", 0)),

            float(d.get("diesel_price", 0)),

            float(d.get("generator_hours", 0)),

            float(d.get("generator_hours_saved", 0))

        )

        total_saving = (

            solar_saving

            + generator["money_saved_year"]

        )

        result = finance(

            float(d["capex"]),

            total_saving,

            float(d["om"]),

            int(d["life"])

        )

        return jsonify({

            "pv_generation": round(pv, 2),

            "battery": battery,

            "generator": generator,

            "finance": result

        })

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500

if name == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT", 5000))
