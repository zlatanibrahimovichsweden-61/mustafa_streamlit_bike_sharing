"""Capital Bikeshare (Washington D.C.) 2011-2012 — hourly demand explorer.

Data: UCI Machine Learning Repository, Bike Sharing Dataset (hour.csv).
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Bike Sharing Demand", page_icon="🪖", layout="wide")

# Egyptian Army desert-camouflage palette
OLIVE, OLIVE_LIGHT, SAND, KHAKI, BROWN, EARTH = (
    "#4B5D23", "#9AA56B", "#D8C9A0", "#BFA978", "#A0712F", "#5C4A2E")
CASUAL, REGISTERED, TOTAL = BROWN, OLIVE, EARTH
CAMO_SCALE = ["#F1EBD8", SAND, KHAKI, "#7E8A4A", OLIVE, "#2F3A16"]
WEEKDAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


# ---------------------------------------------------------------- data
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(Path(__file__).parent / "hour.csv", parse_dates=["dteday"])
    df["year"] = df["yr"].map({0: 2011, 1: 2012})
    df["season_name"] = df["season"].map({1: "Winter", 2: "Spring", 3: "Summer", 4: "Fall"})
    df["weather"] = df["weathersit"].map(
        {1: "Clear", 2: "Mist / cloudy", 3: "Light rain / snow", 4: "Heavy rain / snow"}
    )
    df["day_type"] = df["workingday"].map({1: "Working day", 0: "Weekend / holiday"})
    df["weekday_name"] = df["weekday"].map(dict(enumerate(WEEKDAY_NAMES)))
    df["month_name"] = df["dteday"].dt.strftime("%b")
    # undo the dataset's normalisation so values read in real units
    df["temp_c"] = df["temp"] * 41
    df["feels_c"] = df["atemp"] * 50
    df["humidity_pct"] = df["hum"] * 100
    df["wind_kmh"] = df["windspeed"] * 67
    return df


df = load_data()

# ---------------------------------------------------------------- sidebar filters
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Year", [2011, 2012], default=[2011, 2012])
seasons = st.sidebar.multiselect(
    "Season", ["Winter", "Spring", "Summer", "Fall"], default=["Winter", "Spring", "Summer", "Fall"]
)
months = st.sidebar.slider("Month", 1, 12, (1, 12))
day_types = st.sidebar.multiselect(
    "Day type", ["Working day", "Weekend / holiday"], default=["Working day", "Weekend / holiday"]
)
weathers = st.sidebar.multiselect(
    "Weather",
    ["Clear", "Mist / cloudy", "Light rain / snow", "Heavy rain / snow"],
    default=["Clear", "Mist / cloudy", "Light rain / snow", "Heavy rain / snow"],
)
hours = st.sidebar.slider("Hour of day", 0, 23, (0, 23))
temp_range = st.sidebar.slider("Temperature (°C)", 0.0, 41.0, (0.0, 41.0), step=0.5)
rider = st.sidebar.radio("Riders to count", ["All riders", "Registered", "Casual"])
metric = {"All riders": "cnt", "Registered": "registered", "Casual": "casual"}[rider]
st.sidebar.caption("Every chart and number on the page follows these filters.")

f = df[
    df["year"].isin(years)
    & df["season_name"].isin(seasons)
    & df["mnth"].between(*months)
    & df["day_type"].isin(day_types)
    & df["weather"].isin(weathers)
    & df["hr"].between(*hours)
    & df["temp_c"].between(*temp_range)
]

# ---------------------------------------------------------------- header
st.title("🚲 When and why do people rent bikes?")
st.markdown(
    "Two years (2011–2012) of hourly rentals from **Capital Bikeshare** in Washington D.C. — "
    "17,379 hours, 3.29 million rides. Use the filters on the left to explore."
)

if f.empty:
    st.warning("No hours match these filters. Widen them in the sidebar.")
    st.stop()

# ---------------------------------------------------------------- KPIs
total = int(f[metric].sum())
avg_hour = f[metric].mean()
peak_hr = int(f.groupby("hr")[metric].mean().idxmax())
casual_share = f["casual"].sum() / f["cnt"].sum() * 100 if f["cnt"].sum() else 0
by_year = f.groupby("year")[metric].mean()
yoy = (by_year[2012] / by_year[2011] - 1) * 100 if {2011, 2012} <= set(by_year.index) else None

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total rides", f"{total:,.0f}")
k2.metric("Avg rides / hour", f"{avg_hour:,.0f}")
k3.metric("Busiest hour", f"{peak_hr:02d}:00")
k4.metric("Casual riders' share", f"{casual_share:.0f}%")
k5.metric("2012 vs 2011 (per hour)", f"{yoy:+.0f}%" if yoy is not None else "—",
          help="Average hourly rides in 2012 compared with 2011, for the filtered hours.")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Growth over time", "⏰ Daily rhythm", "👥 Who rides", "🌦️ Weather", "📋 Data"]
)

# Q1 ------------------------------------------------------------- growth
with tab1:
    st.subheader("Q1 · Is the service growing, and how seasonal is it?")
    daily = f.groupby("dteday")[metric].sum().reset_index()
    daily["7-day average"] = daily[metric].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_scatter(x=daily["dteday"], y=daily[metric], mode="lines", name="Daily rides",
                    line=dict(color=SAND, width=1))
    fig.add_scatter(x=daily["dteday"], y=daily["7-day average"], mode="lines",
                    name="7-day average", line=dict(color=REGISTERED, width=2.5))
    fig.update_layout(height=380, yaxis_title="Rides per day", xaxis_title=None,
                      legend=dict(orientation="h", y=1.08), margin=dict(t=30))
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    monthly = f.groupby(["year", "mnth"])[metric].mean().reset_index()
    monthly["Month"] = pd.to_datetime(monthly["mnth"], format="%m").dt.strftime("%b")
    fig = px.bar(monthly, x="Month", y=metric, color=monthly["year"].astype(str), barmode="group",
                 color_discrete_map={"2011": OLIVE_LIGHT, "2012": REGISTERED},
                 labels={metric: "Avg rides / hour", "color": "Year"},
                 title="Average rides per hour, by month")
    fig.update_layout(height=360, legend_title=None)
    c1.plotly_chart(fig, width="stretch")

    season = f.groupby("season_name")[metric].mean().reindex(
        ["Winter", "Spring", "Summer", "Fall"]).dropna().reset_index()
    fig = px.bar(season, x="season_name", y=metric, text_auto=".0f",
                 labels={metric: "Avg rides / hour", "season_name": ""},
                 title="Average rides per hour, by season", color_discrete_sequence=[REGISTERED])
    fig.update_layout(height=360)
    c2.plotly_chart(fig, width="stretch")
    st.info("**Answer:** Ridership grew strongly from 2011 to 2012 (about +63% per hour), and every "
            "month of 2012 beat the same month of 2011. Demand peaks in summer and early fall and "
            "drops by roughly half in winter.")

# Q2 ------------------------------------------------------------- daily rhythm
with tab2:
    st.subheader("Q2 · When during the day do people ride — and do workdays differ from weekends?")
    prof = f.groupby(["day_type", "hr"])[metric].mean().reset_index()
    fig = px.line(prof, x="hr", y=metric, color="day_type", markers=True,
                  color_discrete_map={"Working day": REGISTERED, "Weekend / holiday": CASUAL},
                  labels={"hr": "Hour of day", metric: "Avg rides / hour", "day_type": ""})
    fig.update_layout(height=400, xaxis=dict(dtick=2), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, width="stretch")

    heat = f.pivot_table(index="weekday", columns="hr", values=metric, aggfunc="mean")
    heat.index = [WEEKDAY_NAMES[i] for i in heat.index]
    fig = px.imshow(heat, aspect="auto", color_continuous_scale=CAMO_SCALE,
                    labels=dict(x="Hour of day", y="", color="Avg rides"),
                    title="Average rides by weekday and hour")
    fig.update_layout(height=340)
    st.plotly_chart(fig, width="stretch")
    st.info("**Answer:** Working days have two sharp commuter peaks — around **08:00** and "
            "**17:00–18:00** — while weekends follow a single smooth hump from late morning to "
            "mid-afternoon. The bikes work as a commuting tool on weekdays and a leisure activity "
            "on weekends.")

# Q3 ------------------------------------------------------------- who rides
with tab3:
    st.subheader("Q3 · How do casual and registered riders behave differently?")
    c1, c2 = st.columns(2)
    users = f.groupby("day_type")[["casual", "registered"]].mean().reset_index().melt(
        id_vars="day_type", var_name="Rider", value_name="Avg rides / hour")
    fig = px.bar(users, x="day_type", y="Avg rides / hour", color="Rider", barmode="group",
                 text_auto=".0f", color_discrete_map={"casual": CASUAL, "registered": REGISTERED},
                 labels={"day_type": ""}, title="Average rides per hour by rider type")
    fig.update_layout(height=380)
    c1.plotly_chart(fig, width="stretch")

    hourly_users = f.groupby("hr")[["casual", "registered"]].mean().reset_index()
    fig = go.Figure()
    fig.add_scatter(x=hourly_users["hr"], y=hourly_users["registered"], name="Registered",
                    line=dict(color=REGISTERED, width=2.5))
    fig.add_scatter(x=hourly_users["hr"], y=hourly_users["casual"], name="Casual",
                    line=dict(color=CASUAL, width=2.5))
    fig.update_layout(height=380, title="Hourly pattern by rider type",
                      xaxis_title="Hour of day", yaxis_title="Avg rides / hour", xaxis=dict(dtick=2))
    c2.plotly_chart(fig, width="stretch")

    share = f.groupby("weekday")[["casual", "cnt"]].sum()
    share["Casual share (%)"] = share["casual"] / share["cnt"] * 100
    share.index = [WEEKDAY_NAMES[i] for i in share.index]
    fig = px.bar(share.reset_index(), x="index", y="Casual share (%)", text_auto=".0f",
                 color_discrete_sequence=[CASUAL], labels={"index": ""},
                 title="Share of rides made by casual riders, by weekday")
    fig.update_layout(height=320)
    st.plotly_chart(fig, width="stretch")
    st.info("**Answer:** Registered members make about **81%** of all rides and drive the commuter "
            "peaks. Casual riders are a weekend crowd: their hourly volume more than doubles on "
            "weekends and holidays, and they make roughly a third of Saturday and Sunday rides.")

# Q4 ------------------------------------------------------------- weather
with tab4:
    st.subheader("Q4 · How much do weather and temperature matter?")
    c1, c2 = st.columns(2)
    w = f.groupby("weather")[metric].agg(["mean", "size"]).reindex(
        ["Clear", "Mist / cloudy", "Light rain / snow", "Heavy rain / snow"]).dropna().reset_index()
    fig = px.bar(w, x="weather", y="mean", text_auto=".0f", color_discrete_sequence=[REGISTERED],
                 hover_data={"size": True},
                 labels={"mean": "Avg rides / hour", "weather": "", "size": "Hours observed"},
                 title="Average rides per hour by weather")
    fig.update_layout(height=380)
    c1.plotly_chart(fig, width="stretch")

    t = f.assign(temp_bin=(f["temp_c"] // 2 * 2)).groupby("temp_bin")[metric].agg(
        ["mean", "size"]).reset_index()
    t = t[t["size"] >= 20]
    fig = px.line(t, x="temp_bin", y="mean", markers=True, color_discrete_sequence=[CASUAL],
                  labels={"temp_bin": "Temperature (°C, 2° bins)", "mean": "Avg rides / hour"},
                  title="Average rides per hour by temperature")
    fig.update_layout(height=380)
    c2.plotly_chart(fig, width="stretch")

    hum = f.assign(h_bin=(f["humidity_pct"] // 10 * 10)).groupby("h_bin")[metric].mean().reset_index()
    fig = px.bar(hum, x="h_bin", y=metric, color_discrete_sequence=[KHAKI],
                 labels={"h_bin": "Humidity (%, 10-point bins)", metric: "Avg rides / hour"},
                 title="Average rides per hour by humidity")
    fig.update_layout(height=320)
    st.plotly_chart(fig, width="stretch")
    st.info("**Answer:** Weather is the strongest outside factor. Light rain or snow cuts hourly "
            "rides by about 45% compared with clear skies. Demand climbs steadily with temperature, levels off "
            "around 30–36 °C and drops in the hottest hours, and very humid hours are much quieter.")

# data ----------------------------------------------------------- raw table
with tab5:
    st.subheader("Filtered data")
    cols = ["dteday", "hr", "season_name", "weekday_name", "day_type", "weather", "temp_c",
            "feels_c", "humidity_pct", "wind_kmh", "casual", "registered", "cnt"]
    st.dataframe(f[cols].round({"temp_c": 1, "feels_c": 1, "humidity_pct": 0, "wind_kmh": 1}), width="stretch", hide_index=True)
    st.download_button("Download filtered CSV", f[cols].to_csv(index=False),
                       "bike_sharing_filtered.csv", "text/csv")
    st.caption("Temperature, humidity and wind were stored normalised (0–1) and are converted back "
               "to °C, % and km/h. 165 of the 17,544 hours in 2011–2012 are absent from the source "
               "file.")

# ---------------------------------------------------------------- conclusion
st.divider()
st.header("Conclusion")
st.markdown(
    """
1. **The service is growing fast.** Average hourly rides rose about **63%** from 2011 to 2012, in every month.
2. **It is mainly a commuting system.** On working days demand spikes at **8 AM** and **5–6 PM**; registered members make about **4 of every 5 rides**.
3. **Weekends belong to leisure riders.** Weekend demand is one midday hump, and casual riders' share jumps to about a third.
4. **Weather decides the rest.** Warm, dry, low-humidity hours are busiest; light rain or snow cuts demand by almost half, and winter is the slowest season.

**What this means for operators:** rebalance bikes before the 8 AM and 5 PM commuter peaks, plan maintenance for
winter and rainy days, and aim promotions (and the casual-to-member conversion) at warm weekend afternoons.
"""
)
st.caption("Source: Fanaee-T, H. (2013). Bike Sharing Dataset. UCI Machine Learning Repository. "
           "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset")
