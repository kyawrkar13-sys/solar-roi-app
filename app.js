let ch;

const ids = [
    "monthly_kwh",
    "solar_coverage",
    "capex",
    "degradation",
    "tariff_escalation",
    "annual_om",
    "project_life"
];

const fmt = n => Math.round(n).toLocaleString();

async function calc() {

    let d = {};

    ids.forEach(x => {
        let el = document.getElementById(x);
        if (el) {
            d[x] = el.value;
        }
    });

    let r = await fetch("/calculate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(d)
    });

    let j = await r.json();

    bill.textContent = fmt(j.base_bill) + " MMK";

    ms.textContent =
        fmt(j.first_year_monthly_saving) + " MMK";

    pb.textContent =
        j.simple_payback
        ? j.simple_payback.toFixed(2) + " years"
        : "N/A";

    npv.textContent =
        fmt(j.npv) + " MMK";


    if (j.tiers) {
        tiers.innerHTML =
        j.tiers.map((x,i)=>`
        <div class="tier">
            <span>
            Tier ${i+1}: ${x.kwh} kWh × ${x.rate} MMK
            </span>
            <b>${fmt(x.cost)} MMK</b>
        </div>
        `).join("");
    }


    if (ch) {
        ch.destroy();
    }


    if (j.cashflow) {

        ch = new Chart(chart,{
            type:"bar",
            data:{
                labels:j.cashflow.map(x=>"Y"+x.year),
                datasets:[{
                    label:"Cumulative net position",
                    data:j.cashflow.map(x=>x.cumulative)
                }]
            },
            options:{
                responsive:true
            }
        });

    }
}


ids.forEach(x=>{
    let el=document.getElementById(x);
    if(el){
        el.addEventListener("change",calc);
    }
});


calc();
