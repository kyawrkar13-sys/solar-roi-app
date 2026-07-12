let ch;const ids=["monthly_kwh","solar_coverage","capex","degradation","tariff_escalation","annual_om","project_life",];
const fmt=n=>Math.round(n).toLocaleString();
async function calc(){let d={};ids.forEach(x=>d[x]=document.getElementById(x).value);
let r=await fetch("/calculate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)}),j=await r.json();
bill.textContent=fmt(j.base_bill)+" MMK";ms.textContent=fmt(j.first_year_monthly_saving)+" MMK";
pb.textContent=j.simple_payback?j.simple_payback.toFixed(2)+" years":"N/A";npv.textContent=fmt(j.npv)+" MMK";
tiers.innerHTML=j.tiers.map((x,i)=>`<div class="tier"><span>Tier ${i+1}: ${x.kwh} kWh × ${x.rate} MMK</span><b>${fmt(x.cost)} MMK</b></div>`).join("");
if(ch)ch.destroy();ch=new Chart(chart,{type:"bar",data:{labels:j.cashflow.map(x=>"Y"+x.year),datasets:[
{label:"Cumulative net position",data:j.cashflow.map(x=>x.cumulative),backgroundColor:j.cashflow.map(x=>x.cumulative>=0?"#16b981":"#ef4444")} ]},
options:{responsive:true,plugins:{legend:{labels:{color:"#cbd5e1"}}},scales:{x:{ticks:{color:"#94a3b8"}},y:{ticks:{color:"#94a3b8"}}}}});}
ids.forEach(x=>document.getElementById(x).addEventListener("change",calc));calc();
