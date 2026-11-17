import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Hospitality Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FILES = {
    "performance": DATA_DIR / "agg_hotel_monthly_performance.csv",
    "satisfaction": DATA_DIR / "agg_guest_satisfaction.csv",
    "turnover": DATA_DIR / "agg_employee_turnover.csv",
}

PERFORMANCE_COLS = [
    "hotel_id", "hotel_name", "month_start",
    "available_room_nights", "occupied_room_nights",
    "room_revenue", "occupancy_rate", "ADR", "RevPAR",
]
SATISFACTION_COLS = [
    "hotel_id", "hotel_name", "month_start",
    "total_feedback", "avg_satisfaction_score",
    "positive_feedback", "positive_feedback_rate",
]
TURNOVER_COLS = [
    "hotel_id", "hotel_name", "month_start",
    "opening_headcount", "closing_headcount",
    "employees_exited", "avg_headcount", "turnover_rate",
]

# ============================================================
# 2. PROFESSIONAL STYLING
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background: #f5f7fb;
    }
    [data-testid="stHeader"] {
        background: rgba(245,247,251,0.92);
    }
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }
    [data-testid="stSidebar"] * {
        color: #eef2f7;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] input {
        color: #172033 !important;
    }
    [data-testid="stSidebar"] label {
        font-weight: 600;
    }
    /* Force a consistent light dashboard palette, regardless of browser theme */
    .dashboard-eyebrow {
        color: #526581 !important;
        -webkit-text-fill-color: #526581 !important;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .dashboard-title {
        color: #14243a !important;
        -webkit-text-fill-color: #14243a !important;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin: 0;
    }
    .dashboard-subtitle {
        color: #526581 !important;
        -webkit-text-fill-color: #526581 !important;
        font-size: 0.95rem;
        margin-top: 0.35rem;
        margin-bottom: 1.2rem;
    }
    .section-heading {
        color: #14243a !important;
        -webkit-text-fill-color: #14243a !important;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 0.4rem;
        margin-bottom: 0.15rem;
    }
    .section-caption {
        color: #526581 !important;
        -webkit-text-fill-color: #526581 !important;
        font-size: 0.86rem;
        margin-bottom: 0.8rem;
    }
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {
        color: #26364d !important;
        -webkit-text-fill-color: #26364d !important;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #526581 !important;
        -webkit-text-fill-color: #526581 !important;
        opacity: 1 !important;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: #14243a !important;
        -webkit-text-fill-color: #14243a !important;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e7ebf2;
        border-radius: 13px;
        padding: 17px 18px;
        box-shadow: 0 2px 8px rgba(15,23,42,0.035);
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #111827;
        font-weight: 700;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }
    div[data-testid="stPlotlyChart"] {
        background: #ffffff;
        border: 1px solid #e7ebf2;
        border-radius: 13px;
        padding: 8px;
        box-shadow: 0 2px 8px rgba(15,23,42,0.025);
    }
    div[data-testid="stDataFrame"] {
        background: #ffffff;
        border-radius: 12px;
    }
    hr {
        border-color: #e5eaf1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 3. DATA LOADING AND VALIDATION
# ============================================================
def load_csv(path: Path, required_columns: list, dataset_label: str) -> pd.DataFrame:
    if not path.exists():
        st.error(
            f"Cannot find **{path.name}**. Make sure it is inside the project's "
            f"`data` folder: `{path}`"
        )
        st.stop()

    # The files are small aggregate tables, so reading them on each app rerun
    # keeps the dashboard simple and picks up updated CSV data automatically.
    df = pd.read_csv(path)
    df.columns = df.columns.astype(str).str.strip()
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.dropna(axis=1, how="all")

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"{dataset_label} is missing required columns: {missing}")
        st.stop()

    df = df[required_columns].copy()
    df["month_start"] = pd.to_datetime(df["month_start"], errors="coerce")

    numeric_columns = [
        col for col in required_columns
        if col not in ["hotel_id", "hotel_name", "month_start"]
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["hotel_id", "hotel_name", "month_start"])

    if df.duplicated(["hotel_id", "month_start"]).any():
        st.error(
            f"{dataset_label} contains duplicate hotel/month records. "
            "Please check the aggregate CSV."
        )
        st.stop()

    return df


@st.cache_data
def load_all_data(file_signatures: tuple):
    # file_signatures include file modification times, so changed CSV files
    # trigger a fresh read even though Streamlit caching is enabled.
    performance = load_csv(FILES["performance"], PERFORMANCE_COLS, "Hotel performance")
    satisfaction = load_csv(FILES["satisfaction"], SATISFACTION_COLS, "Guest satisfaction")
    turnover = load_csv(FILES["turnover"], TURNOVER_COLS, "Employee turnover")
    return performance, satisfaction, turnover


missing_files = [str(path) for path in FILES.values() if not path.exists()]
if missing_files:
    st.error("The dashboard data files are missing:")
    for missing in missing_files:
        st.write(f"- `{missing}`")
    st.info(
        "Create a folder named `data` beside `app.py` and place these three CSV files inside it."
    )
    st.stop()

file_signatures = tuple((str(path), path.stat().st_mtime) for path in FILES.values())
performance, satisfaction, turnover = load_all_data(file_signatures)

all_dates = pd.concat(
    [performance["month_start"], satisfaction["month_start"], turnover["month_start"]]
).dropna()
min_month = all_dates.min().date()
max_month = all_dates.max().date()

hotel_options = sorted(performance["hotel_name"].dropna().unique().tolist())

# ============================================================
# 4. SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.markdown("## 🏨 Hospitality")
    st.caption("ANALYTICS WORKSPACE")
    st.divider()

    st.markdown("### Dashboard filters")
    st.caption("Selections below update all dashboard sections.")

    if st.button("Reset filters", use_container_width=True):
        for key in ["hotel_filter", "date_filter", "season_filter"]:
            st.session_state.pop(key, None)
        st.rerun()

    selected_hotels = st.multiselect(
        "Hotel",
        options=hotel_options,
        default=hotel_options,
        key="hotel_filter",
        help="Choose one or more hotels. Keep all selected for the portfolio view.",
    )

    selected_dates = st.date_input(
        "Reporting date range",
        value=(min_month, max_month),
        min_value=min_month,
        max_value=max_month,
        key="date_filter",
        help="The source data is monthly. Select the first and last month to include.",
    )

    season_options = ["Peak Season", "Other Months", "Off Season"]
    selected_seasons = st.multiselect(
        "Season",
        options=season_options,
        default=season_options,
        key="season_filter",
        help="Peak: October–January | Off-season: July–September | Other: February–June",
    )

    st.divider()
    st.markdown("### About this dashboard")
    st.caption("Historical sample data · 2021–2025")
    st.caption("Source: MySQL aggregate tables exported as CSV")

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("Select both a start month and an end month in the sidebar.")
    st.stop()

start_date, end_date = selected_dates
if start_date > end_date:
    st.error("The start date must be earlier than the end date.")
    st.stop()

if not selected_hotels:
    st.warning("Select at least one hotel in the sidebar.")
    st.stop()
if not selected_seasons:
    st.warning("Select at least one season in the sidebar.")
    st.stop()


def add_season(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    month = result["month_start"].dt.month
    result["season"] = "Other Months"
    result.loc[month.isin([10, 11, 12, 1]), "season"] = "Peak Season"
    result.loc[month.isin([7, 8, 9]), "season"] = "Off Season"
    return result


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    result = add_season(df)
    mask = (
        (result["month_start"].dt.date >= start_date)
        & (result["month_start"].dt.date <= end_date)
        & (result["hotel_name"].isin(selected_hotels))
        & (result["season"].isin(selected_seasons))
    )
    return result.loc[mask].copy()


perf = apply_filters(performance)
sat = apply_filters(satisfaction)
emp = apply_filters(turnover)

if perf.empty and sat.empty and emp.empty:
    st.warning("No records match the selected filters. Try widening the date range or changing the hotel/season.")
    st.stop()

# ============================================================
# 5. KPI CALCULATIONS
# ============================================================
def safe_divide(numerator, denominator):
    if pd.isna(denominator) or denominator == 0:
        return None
    return numerator / denominator


def calculate_kpis(p, s, e):
    occupied = p["occupied_room_nights"].sum()
    available = p["available_room_nights"].sum()
    revenue = p["room_revenue"].sum()

    feedback_count = s["total_feedback"].sum()
    weighted_rating = (s["avg_satisfaction_score"] * s["total_feedback"]).sum()

    exits = e["employees_exited"].sum()
    average_headcount = e["avg_headcount"].sum()

    occupancy = safe_divide(occupied, available)
    turnover_rate = safe_divide(exits, average_headcount)

    return {
        "Occupancy Rate": occupancy * 100 if occupancy is not None else None,
        "ADR": safe_divide(revenue, occupied),
        "RevPAR": safe_divide(revenue, available),
        "Guest Satisfaction": safe_divide(weighted_rating, feedback_count),
        "Employee Turnover": turnover_rate * 100 if turnover_rate is not None else None,
    }


def format_kpi(name, value):
    if value is None or pd.isna(value):
        return "N/A"
    if name in ["Occupancy Rate", "Employee Turnover"]:
        return f"{value:.2f}%"
    if name == "Guest Satisfaction":
        return f"{value:.2f} / 5"
    return f"₹{value:,.2f}"


current_kpis = calculate_kpis(perf, sat, emp)

# Compare against the immediately preceding same number of calendar months.
month_count = (
    (end_date.year - start_date.year) * 12
    + end_date.month - start_date.month + 1
)
current_start_month = pd.Timestamp(start_date).replace(day=1)
previous_end_month = current_start_month - pd.offsets.MonthBegin(1)
previous_start_month = previous_end_month - pd.DateOffset(months=month_count - 1)

def previous_filter(df):
    result = add_season(df)
    mask = (
        (result["month_start"] >= previous_start_month)
        & (result["month_start"] <= previous_end_month)
        & (result["hotel_name"].isin(selected_hotels))
        & (result["season"].isin(selected_seasons))
    )
    return result.loc[mask].copy()

previous_kpis = calculate_kpis(
    previous_filter(performance),
    previous_filter(satisfaction),
    previous_filter(turnover),
)


def kpi_delta(name, current, previous):
    if current is None or previous is None:
        return None
    if pd.isna(current) or pd.isna(previous):
        return None
    difference = current - previous
    if name in ["Occupancy Rate", "Employee Turnover"]:
        return f"{difference:+.2f} pp"
    if name == "Guest Satisfaction":
        return f"{difference:+.2f} points"
    return f"₹{difference:+,.2f}"


# ============================================================
# 6. DASHBOARD HEADER AND EXECUTIVE OVERVIEW
# ============================================================
st.markdown('<div class="dashboard-eyebrow">Hospitality performance intelligence</div>', unsafe_allow_html=True)
st.markdown('<h1 class="dashboard-title">Hospitality Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">A consolidated view of hotel operations, revenue, guest experience and workforce performance.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">Executive overview</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-caption">Showing {start_date.strftime("%b %Y")} – {end_date.strftime("%b %Y")} · '
    f'{len(selected_hotels)} hotel(s) · {len(selected_seasons)} season group(s)</div>',
    unsafe_allow_html=True,
)

kpi_names = [
    "Occupancy Rate", "ADR", "RevPAR", "Guest Satisfaction", "Employee Turnover"
]
kpi_cols = st.columns(5)
for col, name in zip(kpi_cols, kpi_names):
    col.metric(
        name,
        format_kpi(name, current_kpis[name]),
        delta=kpi_delta(name, current_kpis[name], previous_kpis[name]),
        help="Change is compared with the previous period of the same number of months, when data is available.",
    )

st.caption("Rate changes are shown in percentage points (pp). Revenue values are in INR. Previous-period comparison may show N/A when earlier data is unavailable.")

# ============================================================
# 7. CHART HELPERS
# ============================================================
PLOT_CONFIG = {"displayModeBar": False}
PLOT_TEMPLATE = "plotly_white"

def polish(fig, height=360):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=height,
        margin=dict(l=24, r=24, t=62, b=28),
        title=dict(font=dict(size=16, color="#172033"), x=0.02, xanchor="left"),
        font=dict(family="DM Sans, sans-serif", color="#475569"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    # Dark, readable axis titles and tick labels on every chart
    fig.update_xaxes(
        showgrid=False,
        linecolor="#d9e1ec",
        title_font=dict(color="#26364d", size=12),
        tickfont=dict(color="#526581", size=11),
    )
    fig.update_yaxes(
        gridcolor="#edf1f6",
        zerolinecolor="#edf1f6",
        title_font=dict(color="#26364d", size=12),
        tickfont=dict(color="#526581", size=11),
    )
    return fig


def monthly_performance(df):
    if df.empty:
        return pd.DataFrame()
    result = df.groupby("month_start", as_index=False).agg(
        available=("available_room_nights", "sum"),
        occupied=("occupied_room_nights", "sum"),
        revenue=("room_revenue", "sum"),
    )
    result["occupancy_rate"] = result["occupied"] / result["available"].replace(0, float("nan")) * 100
    result["ADR"] = result["revenue"] / result["occupied"].replace(0, float("nan"))
    result["RevPAR"] = result["revenue"] / result["available"].replace(0, float("nan"))
    return result


def monthly_satisfaction(df):
    if df.empty:
        return pd.DataFrame()
    temp = df.copy()
    temp["weighted_rating"] = temp["avg_satisfaction_score"] * temp["total_feedback"]
    result = temp.groupby("month_start", as_index=False).agg(
        total_feedback=("total_feedback", "sum"),
        weighted_rating=("weighted_rating", "sum"),
        positive_feedback=("positive_feedback", "sum"),
    )
    result["avg_satisfaction_score"] = result["weighted_rating"] / result["total_feedback"].replace(0, float("nan"))
    result["positive_feedback_rate"] = result["positive_feedback"] / result["total_feedback"].replace(0, float("nan")) * 100
    return result


def monthly_turnover(df):
    if df.empty:
        return pd.DataFrame()
    result = df.groupby("month_start", as_index=False).agg(
        employees_exited=("employees_exited", "sum"),
        avg_headcount=("avg_headcount", "sum"),
        opening_headcount=("opening_headcount", "sum"),
        closing_headcount=("closing_headcount", "sum"),
    )
    result["turnover_rate"] = result["employees_exited"] / result["avg_headcount"].replace(0, float("nan")) * 100
    return result


# ============================================================
# 8. OPERATIONS AND REVENUE
# ============================================================
st.divider()
st.markdown('<div class="section-heading">01 · Operations & revenue</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Monitor room utilization, pricing performance and revenue contribution.</div>', unsafe_allow_html=True)

mp = monthly_performance(perf)
if not mp.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(mp, x="month_start", y="occupancy_rate", markers=True, title="Monthly occupancy rate",
                      labels={"month_start": "Month", "occupancy_rate": "Occupancy (%)"})
        fig.update_traces(line_width=3)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mp["month_start"], y=mp["ADR"], name="ADR", mode="lines+markers", line=dict(width=3)))
        fig.add_trace(go.Scatter(x=mp["month_start"], y=mp["RevPAR"], name="RevPAR", mode="lines+markers", line=dict(width=3)))
        fig.update_layout(title="ADR vs RevPAR trend", xaxis_title="Month", yaxis_title="Revenue (₹)")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)

    c1, c2 = st.columns(2)
    revenue_hotel = perf.groupby("hotel_name", as_index=False)["room_revenue"].sum().sort_values("room_revenue", ascending=True)
    with c1:
        fig = px.bar(revenue_hotel, x="room_revenue", y="hotel_name", orientation="h",
                     title="Room revenue by hotel", labels={"room_revenue": "Room revenue (₹)", "hotel_name": "Hotel"})
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        hotel_occ = perf.groupby("hotel_name", as_index=False).agg(
            occupied=("occupied_room_nights", "sum"), available=("available_room_nights", "sum")
        )
        hotel_occ["occupancy_rate"] = hotel_occ["occupied"] / hotel_occ["available"].replace(0, float("nan")) * 100
        hotel_occ = hotel_occ.sort_values("occupancy_rate", ascending=True)
        fig = px.bar(hotel_occ, x="occupancy_rate", y="hotel_name", orientation="h",
                     title="Occupancy rate by hotel", labels={"occupancy_rate": "Occupancy (%)", "hotel_name": "Hotel"})
        fig.update_xaxes(ticksuffix="%")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
else:
    st.info("No operations and revenue records match these filters.")

# ============================================================
# 9. GUEST EXPERIENCE
# ============================================================
st.divider()
st.markdown('<div class="section-heading">02 · Guest experience</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Track guest ratings, positive feedback and the relationship between occupancy and satisfaction.</div>', unsafe_allow_html=True)

ms = monthly_satisfaction(sat)
if not ms.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(ms, x="month_start", y="avg_satisfaction_score", markers=True,
                      title="Monthly guest satisfaction",
                      labels={"month_start": "Month", "avg_satisfaction_score": "Average rating"})
        fig.update_traces(line_width=3)
        fig.update_yaxes(range=[0, 5])
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        fig = px.line(ms, x="month_start", y="positive_feedback_rate", markers=True,
                      title="Positive feedback rate",
                      labels={"month_start": "Month", "positive_feedback_rate": "Positive feedback (%)"})
        fig.update_traces(line_width=3)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)

    c1, c2 = st.columns(2)
    feedback_hotel = sat.groupby("hotel_name", as_index=False)["total_feedback"].sum().sort_values("total_feedback", ascending=True)
    with c1:
        fig = px.bar(feedback_hotel, x="total_feedback", y="hotel_name", orientation="h",
                     title="Guest feedback volume by hotel",
                     labels={"total_feedback": "Feedback responses", "hotel_name": "Hotel"})
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        combined = perf.merge(sat, on=["hotel_id", "hotel_name", "month_start"], how="inner")
        if not combined.empty:
            combined["occupancy_rate"] = combined["occupied_room_nights"] / combined["available_room_nights"].replace(0, float("nan")) * 100
            fig = px.scatter(combined, x="occupancy_rate", y="avg_satisfaction_score",
                             color="hotel_name", hover_data=["month_start", "total_feedback"],
                             title="Occupancy vs guest satisfaction",
                             labels={"occupancy_rate": "Occupancy (%)", "avg_satisfaction_score": "Average rating", "hotel_name": "Hotel"})
            fig.update_yaxes(range=[0, 5])
            st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info("Not enough matching hotel-month records for the occupancy/satisfaction comparison.")
else:
    st.info("No guest satisfaction records match these filters.")

# ============================================================
# 10. WORKFORCE PERFORMANCE
# ============================================================
st.divider()
st.markdown('<div class="section-heading">03 · Workforce performance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Understand employee exits, turnover trends and headcount movement.</div>', unsafe_allow_html=True)

me = monthly_turnover(emp)
if not me.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(me, x="month_start", y="turnover_rate", markers=True,
                      title="Monthly employee turnover rate",
                      labels={"month_start": "Month", "turnover_rate": "Turnover (%)"})
        fig.update_traces(line_width=3)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        fig = px.bar(me, x="month_start", y="employees_exited",
                     title="Monthly employee exits",
                     labels={"month_start": "Month", "employees_exited": "Employees exited"})
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)

    c1, c2 = st.columns(2)
    exits_hotel = emp.groupby("hotel_name", as_index=False)["employees_exited"].sum().sort_values("employees_exited", ascending=True)
    with c1:
        fig = px.bar(exits_hotel, x="employees_exited", y="hotel_name", orientation="h",
                     title="Employee exits by hotel",
                     labels={"employees_exited": "Employees exited", "hotel_name": "Hotel"})
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=me["month_start"], y=me["opening_headcount"], name="Opening headcount", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=me["month_start"], y=me["closing_headcount"], name="Closing headcount", mode="lines+markers"))
        fig.update_layout(title="Opening vs closing headcount", xaxis_title="Month", yaxis_title="Employees")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
else:
    st.info("No workforce records match these filters.")

# ============================================================
# 11. SEASONAL ANALYSIS
# ============================================================
st.divider()
st.markdown('<div class="section-heading">04 · Seasonal analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">Compare performance across peak, off-peak and other months within the selected reporting period.</div>', unsafe_allow_html=True)

season_order = ["Peak Season", "Other Months", "Off Season"]

if not perf.empty:
    seasonal_perf = perf.groupby("season", as_index=False).agg(
        occupied=("occupied_room_nights", "sum"),
        available=("available_room_nights", "sum"),
        revenue=("room_revenue", "sum"),
    )
    seasonal_perf["occupancy_rate"] = seasonal_perf["occupied"] / seasonal_perf["available"].replace(0, float("nan")) * 100
    seasonal_perf["ADR"] = seasonal_perf["revenue"] / seasonal_perf["occupied"].replace(0, float("nan"))
    seasonal_perf["RevPAR"] = seasonal_perf["revenue"] / seasonal_perf["available"].replace(0, float("nan"))
    seasonal_perf["season"] = pd.Categorical(seasonal_perf["season"], categories=season_order, ordered=True)
    seasonal_perf = seasonal_perf.sort_values("season")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(seasonal_perf, x="season", y="occupancy_rate", text_auto=".2f",
                     title="Occupancy rate by season",
                     labels={"season": "Season", "occupancy_rate": "Occupancy (%)"})
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=seasonal_perf["season"].astype(str), y=seasonal_perf["ADR"], name="ADR"))
        fig.add_trace(go.Bar(x=seasonal_perf["season"].astype(str), y=seasonal_perf["RevPAR"], name="RevPAR"))
        fig.update_layout(title="ADR vs RevPAR by season", xaxis_title="Season", yaxis_title="Revenue (₹)", barmode="group")
        st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)

    c1, c2 = st.columns(2)
    if not sat.empty:
        seasonal_sat = sat.copy()
        seasonal_sat["weighted_rating"] = seasonal_sat["avg_satisfaction_score"] * seasonal_sat["total_feedback"]
        seasonal_sat = seasonal_sat.groupby("season", as_index=False).agg(
            feedback=("total_feedback", "sum"), weighted_rating=("weighted_rating", "sum")
        )
        seasonal_sat["satisfaction_score"] = seasonal_sat["weighted_rating"] / seasonal_sat["feedback"].replace(0, float("nan"))
        seasonal_sat["season"] = pd.Categorical(seasonal_sat["season"], categories=season_order, ordered=True)
        seasonal_sat = seasonal_sat.sort_values("season")
        with c1:
            fig = px.bar(seasonal_sat, x="season", y="satisfaction_score", text_auto=".2f",
                         title="Guest satisfaction by season",
                         labels={"season": "Season", "satisfaction_score": "Average rating (/5)"})
            fig.update_yaxes(range=[0, 5])
            st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
    if not emp.empty:
        seasonal_emp = emp.groupby("season", as_index=False).agg(
            exits=("employees_exited", "sum"), avg_headcount=("avg_headcount", "sum")
        )
        seasonal_emp["turnover_rate"] = seasonal_emp["exits"] / seasonal_emp["avg_headcount"].replace(0, float("nan")) * 100
        seasonal_emp["season"] = pd.Categorical(seasonal_emp["season"], categories=season_order, ordered=True)
        seasonal_emp = seasonal_emp.sort_values("season")
        with c2:
            fig = px.bar(seasonal_emp, x="season", y="turnover_rate", text_auto=".2f",
                         title="Employee turnover by season",
                         labels={"season": "Season", "turnover_rate": "Turnover (%)"})
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(polish(fig), use_container_width=True, config=PLOT_CONFIG)
else:
    st.info("No performance records available for seasonal analysis.")

# ============================================================
# 12. DATA DETAILS AND FOOTER
# ============================================================
st.divider()
st.markdown('<div class="section-heading">Data overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-caption">A quick view of the data currently included after applying your filters.</div>', unsafe_allow_html=True)

d1, d2, d3 = st.columns(3)
d1.metric("Hotels selected", perf["hotel_id"].nunique() if not perf.empty else 0)
d2.metric("Monthly performance rows", len(perf))
d3.metric("Guest feedback responses", f"{int(sat['total_feedback'].sum()):,}" if not sat.empty else "0")

with st.expander("View filtered hotel performance data"):
    st.dataframe(perf.drop(columns=["season"], errors="ignore"), use_container_width=True, hide_index=True)
with st.expander("View filtered guest satisfaction data"):
    st.dataframe(sat.drop(columns=["season"], errors="ignore"), use_container_width=True, hide_index=True)
with st.expander("View filtered employee turnover data"):
    st.dataframe(emp.drop(columns=["season"], errors="ignore"), use_container_width=True, hide_index=True)

st.divider()
st.caption("Hospitality Analytics Platform · Sample historical dataset 2021–2025 · Python · Pandas · Streamlit · Plotly")
