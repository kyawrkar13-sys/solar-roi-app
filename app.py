from flask import Flask,render_template,request,jsonify
app=Flask(__name__)
TARIFF=[(50,50),(50,100),(100,150),(float("inf"),300)]
def bill(kwh):
    r=max(0,float(kwh)); total=0; rows=[]
    for cap,rate in TARIFF:
        use=min(r,cap); cost=use*rate
        if use>0: rows.append({"kwh":round(use,2),"rate":rate,"cost":round(cost,2)})
        total+=cost;r-=use
        if r<=0: break
    return total,rows
def model(d):
    load=float(d["monthly_kwh"]); coverage=float(d["solar_coverage"])/100
    capex=float(d["capex"]); deg=float(d["degradation"])/100
    escalation=float(d["tariff_escalation"])/100; om=float(d["annual_om"])
    life=int(d["project_life"]); discount=float(d["discount_rate"])/100
    base_bill,tiers=bill(load); cash=[]; cum=-capex; npv=-capex; break_even=None
    for y in range(1,life+1):
        solar_kwh=load*coverage*((1-deg)**(y-1))
        grid=max(0,load-solar_kwh)
        old,_=bill(load); new,_=bill(grid)
        factor=(1+escalation)**(y-1)
        saving=(old-new)*12*factor
        net=saving-om
        cum+=net; npv+=net/((1+discount)**y)
        if break_even is None and cum>=0: break_even=y
        cash.append({"year":y,"solar_kwh_month":solar_kwh,"grid_kwh_month":grid,"annual_saving":saving,"net_cash":net,"cumulative":cum})
    first=cash[0]
    simple=capex/first["net_cash"] if first["net_cash"]>0 else None
    roi=(sum(x["net_cash"] for x in cash)-capex)/capex*100 if capex else 0
    return {"base_bill":base_bill,"tiers":tiers,"first_year_monthly_saving":first["annual_saving"]/12,
    "first_year_annual_saving":first["annual_saving"],"simple_payback":simple,"break_even_year":break_even,
    "lifetime_roi":roi,"npv":npv,"cashflow":cash}
@app.route("/")
def index(): return render_template("index.html")
@app.post("/calculate")
def calculate(): return jsonify(model(request.get_json()))
if __name__=="__main__": app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
