# Solar Engineering ROI v2

Run:
1. `pip install -r requirements.txt`
2. `python app.py`
3. Open `http://127.0.0.1:5000`

Model:
- Progressive domestic tariff: 1–50 kWh @ 50 MMK; next 50 @ 100; next 100 @ 150; above 200 @ 300.
- Solar energy offsets monthly grid-import energy.
- Remaining grid energy is re-billed progressively.
- Includes annual PV degradation, annual O&M, tariff escalation, project life, discount rate and NPV.

Important engineering limitation:
This version uses monthly energy balance. It does NOT yet simulate hourly load-vs-PV coincidence, export compensation, inverter clipping, battery round-trip losses, shading, temperature losses, availability, or module orientation. For bankable PV sizing, use interval load data and a site-specific PV yield model.

## Deploy on Render
This package is deployment-ready. Push the folder to GitHub, then create a Render Blueprint/Web Service. `render.yaml` contains the build and start commands.
