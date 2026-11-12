# ForecastFlow Dharwad prototype

## Included
- `app.py`: Streamlit dashboard for groundwater history, rainfall coverage and a persistence-baseline demonstration.
- `ForecastFlow_Dharwad_Updated_Monthly_Merged.csv`: prepared real-data merge.

## Run on Windows / VS Code
Open PowerShell in this folder and run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

A browser tab should open. If it does not, use the local URL printed in the terminal.

## Important scientific caveat
The forecast shown is a persistence baseline for UI/pipeline demonstration only. It is not a trained LUBE model and does not provide calibrated uncertainty or depletion-risk probabilities. The current dataset has incomplete rainfall coverage and very few eligible monthly training rows. Do not use this prototype for operational water-resource decisions.

Before model claims:
1. Verify groundwater units and sign convention.
2. Obtain complete historical rainfall and assess station coverage.
3. Use chronological rolling-origin validation.
4. Compare against persistence and Ridge.
5. Train and calibrate a probabilistic model (LUBE or quantile regression) only when data support evaluation.
