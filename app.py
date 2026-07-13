from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Generator Fuel Saving Calculator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{ font-family:Arial; background:#f2f2f2; padding:20px; }
        .box{ max-width:500px; margin:auto; background:white; padding:20px; border-radius:15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input, button { width:100%; padding:12px; margin-top:10px; box-sizing: border-box; }
        button{ background:green; color:white; border:0; border-radius:8px; cursor:pointer; font-weight:bold; }
        .result{ margin-top:20px; background:#e8ffe8; padding:15px; border-radius: 8px; border-left: 5px solid green; }
        .error{ margin-top:20px; background:#ffe8e8; padding:15px; border-radius: 8px; color: red; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Generator Fuel Saving Calculator</h2>
        <form method="post">
            Fuel L/hour: <input type="number" step="any" name="fuel" value="{{ fuel or 40 }}" required>
            Hours/day: <input type="number" step="any" name="hours" value="{{ hours or 10 }}" required>
            Diesel $/L: <input type="number" step="any" name="price" value="{{ price or 1.2 }}" required>
            Solar Offset %: <input type="number" step="any" name="offset" value="{{ offset or 50 }}" required>
            System Cost $: <input type="number" step="any" name="cost" value="{{ cost or 80000 }}" required>
            <button type="submit">Calculate</button>
        </form>
        
        {% if result %}
            <div class='result'>
                {{ result|safe }}
            </div>
        {% elif error %}
            <div class='error'>
                {{ error }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            fuel = float(request.form["fuel"])
            hours = float(request.form["hours"])
            price = float(request.form["price"])
            offset = float(request.form["offset"])
            cost = float(request.form["cost"])

            fuel_day = fuel * hours * (offset / 100)
            saving_day = fuel_day * price
            saving_month = saving_day * 30
            saving_year = saving_month * 12
            
            payback = cost / saving_year if saving_year > 0 else 0
            roi = (saving_year / cost) * 100 if cost > 0 else 0

            result_text = f"""
            <strong>Results:</strong><br>
            Fuel Saving: {fuel_day:.2f} L/day<br>
            Daily Saving: ${saving_day:.2f}<br>
            Monthly Saving: ${saving_month:.2f}<br>
            Yearly Saving: ${saving_year:.2f}<br><br>
            Payback: {payback:.2f} Years<br>
            ROI: {roi:.2f}%
            """
            return render_template_string(HTML_TEMPLATE, result=result_text, fuel=fuel, hours=hours, price=price, offset=offset, cost=cost)
        
        except:
            return render_template_string(HTML_TEMPLATE, error="Invalid input. ဂဏန်းများသာ ထည့်ပေးပါ။")

    return render_template_string(HTML_TEMPLATE)

if name == "__main__":
    app.run(host="0.0.0.0", port=5000)
