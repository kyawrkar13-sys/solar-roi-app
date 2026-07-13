from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    result = None

    if request.method == "POST":

        fuel = float(request.form["fuel"])
        price = float(request.form["price"])
        hours = float(request.form["hours"])
        offset = float(request.form["offset"])
        cost = float(request.form["cost"])

        # Fuel saving calculation
        fuel_saved_day = fuel * hours * (offset / 100)

        money_saved_day = fuel_saved_day * price

        money_saved_month = money_saved_day * 30

        money_saved_year = money_saved_month * 12

        payback = cost / money_saved_year

        roi = (money_saved_year / cost) * 100


        result = {
            "fuel_day": round(fuel_saved_day,2),
            "day": round(money_saved_day,2),
            "month": round(money_saved_month,2),
            "year": round(money_saved_year,2),
            "payback": round(payback,2),
            "roi": round(roi,2)
        }


    return render_template(
        "index.html",
        result=result
    )


if name == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
