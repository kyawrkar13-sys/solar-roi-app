from flask import Flask, request

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Generator Fuel Saving Calculator</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body{
    font-family:Arial;
    background:#f2f2f2;
    padding:20px;
}

.box{
    max-width:500px;
    margin:auto;
    background:white;
    padding:20px;
    border-radius:15px;
}

input,button{
    width:100%;
    padding:12px;
    margin-top:10px;
    font-size:16px;
}

button{
    background:green;
    color:white;
    border:0;
    border-radius:8px;
}

.result{
    margin-top:20px;
    background:#e8ffe8;
    padding:15px;
    border-radius:10px;
}
</style>

</head>

<body>

<div class="box">

<h2>Generator Fuel Saving Calculator</h2>

<form method="post">

<label>Generator Fuel (L/hour)</label>
<input name="fuel" value="40" type="number" step="0.01">

<label>Running Hours / Day</label>
<input name="hours" value="10" type="number" step="0.01">

<label>Diesel Price ($/L)</label>
<input name="price" value="1.2" type="number" step="0.01">

<label>Solar Offset (%)</label>
<input name="offset" value="50" type="number" step="0.01">

<label>Solar System Cost ($)</label>
<input name="cost" value="80000" type="number" step="0.01">

<button type="submit">Calculate</button>

</form>

{%RESULT%}

</div>

</body>
</html>
"""


@app.route("/", methods=["GET","POST"])
def home():

    result = ""

    if request.method == "POST":

        fuel = float(request.form["fuel"])
        hours = float(request.form["hours"])
        price = float(request.form["price"])
        offset = float(request.form["offset"])
        cost = float(request.form["cost"])


        fuel_day = fuel * hours * offset / 100

        money_day = fuel_day * price

        money_month = money_day * 30

        money_year = money_month * 12

        payback = cost / money_year

        roi = money_year / cost * 100


        result = f"""
        <div class='result'>
        <b>Fuel Saving:</b> {fuel_day:.2f} L/day<br><br>

        <b>Daily Saving:</b> ${money_day:.2f}<br>
        <b>Monthly Saving:</b> ${money_month:.2f}<br>
        <b>Yearly Saving:</b> ${money_year:.2f}<br><br>

        <b>Payback:</b> {payback:.2f} Years<br>
        <b>ROI:</b> {roi:.2f} %

        </div>
        """


    return HTML.replace("{%RESULT%}", result)



if name == "__main__":
    app.run(host="0.0.0.0", port=5000)
