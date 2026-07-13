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
}
</style>

</head>

<body>

<div class="box">

<h2>Generator Fuel Saving Calculator</h2>

<form method="post">

Fuel L/hour:
<input name="fuel" value="40">

Hours/day:
<input name="hours" value="10">

Diesel $/L:
<input name="price" value="1.2">

Solar Offset %:
<input name="offset" value="50">

System Cost $:
<input name="cost" value="80000">

<button>Calculate</button>

</form>

{{result}}

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

        saving_day = fuel_day * price

        saving_month = saving_day * 30

        saving_year = saving_month * 12

        payback = cost / saving_year

        roi = saving_year / cost * 100


        result = f"""
        <div class='result'>
        Fuel Saving: {fuel_day:.2f} L/day<br><br>
        Daily Saving: ${saving_day:.2f}<br>
        Monthly Saving: ${saving_month:.2f}<br>
        Yearly Saving: ${saving_year:.2f}<br><br>
        Payback: {payback:.2f} Years<br>
        ROI: {roi:.2f}%
        </div>
        """


    return HTML.replace("{{result}}", result)


if name == "__main__":
    app.run(host="0.0.0.0", port=5000)
