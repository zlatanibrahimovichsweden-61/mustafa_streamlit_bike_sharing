# 🚲 Bike Sharing Demand Explorer

An interactive Streamlit app that explores **when and why people rent bikes**, using two years (2011–2012) of hourly rental data from Capital Bikeshare in Washington D.C.

**Live app:** https://<your-app>.streamlit.app

## What the app shows

- **KPIs:** total rides, average rides per hour, busiest hour, casual riders' share, and 2012-vs-2011 growth.
- **Four questions, each with charts and a plain-language answer:**
  1. *Growth over time:* daily rides with a 7-day average, monthly comparison by year, and seasonality.
  2. *Daily rhythm:* hourly profile for working days vs weekends, plus a weekday × hour heatmap.
  3. *Who rides:* casual vs registered riders by day type, by hour, and by weekday.
  4. *Weather:* rides by weather type, temperature, and humidity.
- **Filters** (sidebar): year, season, month, day type, weather, hour of day, temperature, and rider type. Every chart and KPI updates with them.
- **Data tab:** the filtered rows, downloadable as CSV.
- **Conclusion:** the main findings and what they mean for operators.

## Key findings

- Ridership grew about **63%** per hour from 2011 to 2012, and every month of 2012 beat the same month of 2011.
- Working days show two commuter peaks (**8 AM** and **5–6 PM**). Registered members make about **81%** of rides.
- Weekends are a single midday hump, and casual riders make about a third of weekend rides.
- Light rain or snow cuts demand by about **45%**. Summer is the busiest season and winter the slowest.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data

`hour.csv` from the [UCI Bike Sharing Dataset](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) (Fanaee-T, 2013). 17,379 hourly records. Temperature, humidity and wind speed are stored normalised (0–1) and the app converts them back to °C, % and km/h.
