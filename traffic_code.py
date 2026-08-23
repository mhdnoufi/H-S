import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Traffic Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .dashboard-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .kpi {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        min-height: 100px;
    }

    .kpi-label {
        font-size: 13px;
        color: #6b7280;
    }

    .kpi-value {
        font-size: 27px;
        font-weight: 700;
        margin-top: 7px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_csv(
        "rows.csv",
        low_memory=False
    )

    data.columns = (
        data.columns
        .astype(str)
        .str.strip()
    )

    data["Published Date"] = pd.to_datetime(
        data["Published Date"],
        errors="coerce",
        utc=True
    )

    data["Status Date"] = pd.to_datetime(
        data["Status Date"],
        errors="coerce",
        utc=True
    )

    data["Latitude"] = pd.to_numeric(
        data["Latitude"],
        errors="coerce"
    )

    data["Longitude"] = pd.to_numeric(
        data["Longitude"],
        errors="coerce"
    )

    text_columns = [
        "Traffic Report ID",
        "Issue Reported",
        "Location",
        "Address",
        "Status",
        "Agency"
    ]

    for col in text_columns:

        data[col] = (
            data[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        data.loc[
            data[col].isin(
                ["", "nan", "None", "NaN"]
            ),
            col
        ] = "Unknown"

    return data


# ============================================================
# LOAD
# ============================================================

try:

    df = load_data()

except Exception as error:

    st.error(
        "Unable to load rows.csv"
    )

    st.code(str(error))

    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🚦 Traffic Dashboard")

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Filters")


with st.sidebar.form("filter_form"):

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    dates = df["Published Date"].dropna()

    if not dates.empty:

        min_date = dates.min().date()
        max_date = dates.max().date()

        date_range = st.date_input(
            "Published Date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    else:

        date_range = None


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_list = sorted(
        df["Status"].unique().tolist()
    )

    selected_status = st.multiselect(
        "Status",
        status_list
    )


    # --------------------------------------------------------
    # AGENCY
    # --------------------------------------------------------

    agency_list = sorted(
        df["Agency"].unique().tolist()
    )

    selected_agency = st.multiselect(
        "Agency",
        agency_list
    )


    # --------------------------------------------------------
    # ISSUE
    # --------------------------------------------------------

    issue_list = sorted(
        df["Issue Reported"].unique().tolist()
    )

    selected_issue = st.multiselect(
        "Issue Reported",
        issue_list
    )


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    location_list = sorted(
        df["Location"].unique().tolist()
    )

    selected_location = st.multiselect(
        "Location",
        location_list
    )


    st.form_submit_button(
        "🔍 Apply Filters",
        use_container_width=True
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if (
    date_range is not None
    and isinstance(date_range, (tuple, list))
    and len(date_range) == 2
):

    start = pd.Timestamp(
        date_range[0],
        tz="UTC"
    )

    end = (
        pd.Timestamp(
            date_range[1],
            tz="UTC"
        )
        + pd.Timedelta(days=1)
    )

    filtered_df = filtered_df[
        (filtered_df["Published Date"] >= start)
        &
        (filtered_df["Published Date"] < end)
    ]


if selected_status:

    filtered_df = filtered_df[
        filtered_df["Status"].isin(
            selected_status
        )
    ]


if selected_agency:

    filtered_df = filtered_df[
        filtered_df["Agency"].isin(
            selected_agency
        )
    ]


if selected_issue:

    filtered_df = filtered_df[
        filtered_df["Issue Reported"].isin(
            selected_issue
        )
    ]


if selected_location:

    filtered_df = filtered_df[
        filtered_df["Location"].isin(
            selected_location
        )
    ]


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    '🚦 Traffic Report Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Page 1 — Traffic Overview'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# EMPTY DATA
# ============================================================

if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ============================================================
# KPIs
# ============================================================

total = len(filtered_df)

unique_reports = (
    filtered_df["Traffic Report ID"]
    .nunique()
)

locations = (
    filtered_df["Location"]
    .nunique()
)

issues = (
    filtered_df["Issue Reported"]
    .nunique()
)

agencies = (
    filtered_df["Agency"]
    .nunique()
)

open_reports = (
    filtered_df["Status"]
    .str.lower()
    .str.contains(
        "open",
        na=False
    )
    .sum()
)


st.markdown(
    '<div class="section-title">'
    '📊 Key Performance Indicators'
    '</div>',
    unsafe_allow_html=True
)


c1, c2, c3, c4, c5, c6 = st.columns(6)


kpis = [
    ("Total Reports", total),
    ("Unique Reports", unique_reports),
    ("Locations", locations),
    ("Issues", issues),
    ("Agencies", agencies),
    ("Open Reports", open_reports)
]


for column, (label, value) in zip(
    [c1, c2, c3, c4, c5, c6],
    kpis
):

    with column:

        st.markdown(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {label}
                </div>

                <div class="kpi-value">
                    {value:,}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# STATUS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📌 Status Analysis'
    '</div>',
    unsafe_allow_html=True
)


status_data = (
    filtered_df["Status"]
    .value_counts()
    .reset_index()
)

status_data.columns = [
    "Status",
    "Count"
]


c1, c2 = st.columns(2)


with c1:

    fig = px.pie(
        status_data,
        names="Status",
        values="Count",
        hole=0.45,
        title="Reports by Status"
    )

    fig.update_layout(
        height=380
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with c2:

    fig = px.bar(
        status_data,
        x="Status",
        y="Count",
        text="Count",
        title="Status Distribution"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=380
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ISSUE ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '⚠️ Traffic Issues'
    '</div>',
    unsafe_allow_html=True
)


issue_data = (
    filtered_df["Issue Reported"]
    .value_counts()
    .head(15)
    .reset_index()
)

issue_data.columns = [
    "Issue Reported",
    "Count"
]


fig = px.bar(
    issue_data.sort_values("Count"),
    x="Count",
    y="Issue Reported",
    orientation="h",
    text="Count",
    title="Top 15 Traffic Issues"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# AGENCY
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🏢 Agency Analysis'
    '</div>',
    unsafe_allow_html=True
)


agency_data = (
    filtered_df["Agency"]
    .value_counts()
    .head(15)
    .reset_index()
)

agency_data.columns = [
    "Agency",
    "Count"
]


c1, c2 = st.columns(2)


with c1:

    fig = px.bar(
        agency_data,
        x="Agency",
        y="Count",
        text="Count",
        title="Reports by Agency"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=430,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with c2:

    fig = px.pie(
        agency_data.head(10),
        names="Agency",
        values="Count",
        hole=0.4,
        title="Agency Share"
    )

    fig.update_layout(
        height=430
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# LOCATION
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📍 Location Analysis'
    '</div>',
    unsafe_allow_html=True
)


location_data = (
    filtered_df["Location"]
    .value_counts()
    .head(15)
    .reset_index()
)

location_data.columns = [
    "Location",
    "Count"
]


fig = px.bar(
    location_data.sort_values("Count"),
    x="Count",
    y="Location",
    orientation="h",
    text="Count",
    title="Top 15 Locations"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# DATE TREND
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📅 Report Trend'
    '</div>',
    unsafe_allow_html=True
)


trend = filtered_df[
    filtered_df["Published Date"].notna()
].copy()


if not trend.empty:

    trend["Date"] = (
        trend["Published Date"]
        .dt.date
    )

    daily = (
        trend
        .groupby("Date")
        .size()
        .reset_index(
            name="Reports"
        )
    )

    fig = px.line(
        daily,
        x="Date",
        y="Reports",
        markers=True,
        title="Daily Traffic Reports"
    )

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# MONTHLY TREND
# ============================================================

if not trend.empty:

    trend["Month"] = (
        trend["Published Date"]
        .dt.strftime("%Y-%m")
    )

    monthly = (
        trend
        .groupby("Month")
        .size()
        .reset_index(
            name="Reports"
        )
    )

    fig = px.bar(
        monthly,
        x="Month",
        y="Reports",
        text="Reports",
        title="Monthly Traffic Reports"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    f"Traffic Dashboard • "
    f"{len(filtered_df):,} filtered records "
    f"out of {len(df):,}"
)