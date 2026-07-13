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


def finance(capex, saving, om, life):

    cashflow = []
    cumulative = -capex
    npv = -capex
    total = 0
    payback = None

    discount = 0.08

    for y in range(1, life + 1):

        net = saving * (1.03 ** (y-1)) - om

        cumulative += net
        npv += net / ((1 + discount) ** y)

        total += net

        if payback is None and cumulative >= 0:
            payback = y

        cashflow.append({
            "year": y,
            "cumulative": round(cumulative,2)
        })


    roi = ((total-capex)/capex)*100 if capex else 0


    return {
        "payback": payback,
        "roi": round(roi,2),
        "npv": round(npv,2),
        "cashflow": cashflow
    }



@app.route("/")
def home():
    return render_template("index.html")



@app.route("/calculate", methods=["POST"])
def calculate():

    try:

        d = request.json


        pv_kw = float(d["pv_kw"])
        psh = float(d["psh"])
        pr = float(d["pr"])/100


        pv = solar_generation(
            pv_kw,
            psh,
            pr
        )


        battery = battery_calculation(
            float(d["battery"]),
            float(d["dod"])/100,
            float(d["efficiency"])/100,
            float(d["load"])
        )


        saving = pv * float(d["tariff"])


        result = finance(
            float(d["capex"]),
            saving,
            float(d["om"]),
            int(d["life"])
        )


        return jsonify({

            "pv_generation": round(pv,2),

            "battery": battery,

            "finance": result

        })


    except Exception as e:

        return jsonify({
            "error":str(e)
        }),500



if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT",5000))
    )
