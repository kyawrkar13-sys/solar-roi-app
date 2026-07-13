[13/07/2026 22:51] Rkar Kyaw: from flask import Flask, render_template, request, jsonify

app = Flask(name)


# =========================
# SOLAR GENERATION
# =========================

def solar_generation(pv_kw, psh, pr):
    return pv_kw * psh * 365 * pr


# =========================
# BATTERY CALCULATION
# =========================

def battery_calculation(capacity, dod, efficiency, load):

    usable = capacity * dod * efficiency

    coverage = (usable / load) * 100 if load else 0

    return {
        "usable_energy": round(usable, 2),
        "coverage": round(coverage, 2)
    }


# =========================
# GENERATOR FUEL SAVING
# =========================

def generator_calculation(
    fuel_consumption,
    diesel_price,
    generator_hours,
    generator_hours_saved
):

    # Saved hours cannot exceed actual generator running hours
    actual_saved_hours = min(
        generator_hours_saved,
        generator_hours
    )

    fuel_saved_day = (
        fuel_consumption *
        actual_saved_hours
    )

    fuel_saved_month = (
        fuel_saved_day * 30
    )

    fuel_saved_year = (
        fuel_saved_day * 365
    )


    money_saved_day = (
        fuel_saved_day *
        diesel_price
    )

    money_saved_month = (
        fuel_saved_month *
        diesel_price
    )

    money_saved_year = (
        fuel_saved_year *
        diesel_price
    )


    return {

        "hours_saved_day":
            round(actual_saved_hours, 2),

        "fuel_saved_day":
            round(fuel_saved_day, 2),

        "fuel_saved_month":
            round(fuel_saved_month, 2),

        "fuel_saved_year":
            round(fuel_saved_year, 2),

        "money_saved_day":
            round(money_saved_day, 2),

        "money_saved_month":
            round(money_saved_month, 2),

        "money_saved_year":
            round(money_saved_year, 2)

    }


# =========================
# FINANCIAL CALCULATION
# =========================

def finance(
    capex,
    solar_saving,
    generator_saving,
    om,
    life
):

    cashflow = []

    cumulative = -capex

    npv = -capex

    total = 0

    payback = None

    discount = 0.08


    # Total annual saving
    total_annual_saving = (
        solar_saving +
        generator_saving
    )


    for y in range(1, life + 1):

        # 3% yearly energy price escalation
        annual_saving = (
            total_annual_saving *
            (1.03  (y - 1))
        )

        net = (
            annual_saving -
            om
        )


        cumulative += net


        npv += (
            net /
            ((1 + discount)  y)
        )


        total += net


        if (
            payback is None
            and cumulative >= 0
        ):
            payback = y


        cashflow.append({

            "year":
                y,

            "annual_saving":
                round(annual_saving, 2),

            "net_cashflow":
                round(net, 2),

            "cumulative":
                round(cumulative, 2)

        })


    roi = (
        ((total - capex) / capex) * 100
        if capex
        else 0
    )


    return {

        "solar_saving_year":
            round(solar_saving, 2),

        "generator_saving_year":
            round(generator_saving, 2),

        "total_saving_year":
            round(total_annual_saving, 2),

        "payback":
            payback,

        "roi":
            round(roi, 2),

        "npv":
            round(npv, 2),

        "cashflow":
            cashflow

    }


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================
# CALCULATE API
# =========================

@app.route(
    "/calculate",
    methods=["POST"]
)

def calculate():

    try:

        d = request.get_json()


        # -------------------------
        # SOLAR INPUT
        # -------------------------

        pv_kw = float(
            d["pv_kw"]
        )
[13/07/2026 22:52] Rkar Kyaw: pr = (
            float(d["pr"]) /
            100
        )


        # -------------------------
        # SOLAR GENERATION
        # -------------------------

        pv = solar_generation(
            pv_kw,
            psh,
            pr
        )


        # -------------------------
        # BATTERY
        # -------------------------

        battery = battery_calculation(

            float(d["battery"]),

            float(d["dod"]) / 100,

            float(d["efficiency"]) / 100,

            float(d["load"])

        )


        # -------------------------
        # SOLAR ELECTRICITY SAVING
        # -------------------------

        tariff = float(
            d["tariff"]
        )


        solar_saving = (
            pv *
            tariff
        )


        # -------------------------
        # GENERATOR INPUT
        # -------------------------

        fuel_consumption = float(
            d.get(
                "fuel_consumption",
                0
            )
        )


        diesel_price = float(
            d.get(
                "diesel_price",
                0
            )
        )


        generator_hours = float(
            d.get(
                "generator_hours",
                0
            )
        )


        generator_hours_saved = float(
            d.get(
                "generator_hours_saved",
                0
            )
        )


        # -------------------------
        # GENERATOR CALCULATION
        # -------------------------

        generator = generator_calculation(

            fuel_consumption,

            diesel_price,

            generator_hours,

            generator_hours_saved

        )


        generator_saving = (
            generator[
                "money_saved_year"
            ]
        )


        # -------------------------
        # FINANCIAL ANALYSIS
        # -------------------------

        result = finance(

            float(d["capex"]),

            solar_saving,

            generator_saving,

            float(d["om"]),

            int(d["life"])

        )


        # -------------------------
        # RETURN RESULT
        # -------------------------

        return jsonify({

            "pv_generation":
                round(pv, 2),

            "battery":
                battery,

            "generator":
                generator,

            "finance":
                result

        })


    except Exception as e:

        return jsonify({

            "error":
                str(e)

        }), 500


# =========================
# RUN SERVER
# =========================

if name == "main":

    app.run(

        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )

    )
