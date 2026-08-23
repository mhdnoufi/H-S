import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Traffic Detailed Analysis",
    page_icon="🗺️",
    layout="wide"
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
# SIDEBAR
# ============================================================

st.sidebar.title("🗺️ Detailed Analysis")

st.sidebar.markdown(
    "Filters for geographic and detailed analysis."
)

st.sidebar.markdown("---")


with st.sidebar.form(
    "detail_filter_form"
):

    # DATE

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


    # STATUS

    selected_status = st.multiselect(
        "Status",
        sorted(
            df["Status"]
            .unique()
            .tolist()
        )
    )


    # AGENCY

    selected_agency = st.multiselect(
        "Agency",
        sorted(
            df["Agency"]
            .unique()
            .tolist()
        )
    )


    # ISSUE

    selected_issue = st.multiselect(
        "Issue Reported",
        sorted(
            df["Issue Reported"]
            .unique()
            .tolist()
        )
    )


    # LOCATION

    selected_location = st.multiselect(
        "Location",
        sorted(
            df["Location"]
            .unique()
            .tolist()
        )
    )


    st.form_submit_button(
        "🔍 Apply Filters",
        use_container_width=True
    )


# ============================================================
# FILTER
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

st.title(
    "🗺️ Traffic Detailed Analysis"
)

st.caption(
    "Page 2 — Geographic and detailed traffic analysis"
)


# ============================================================
# EMPTY
# ============================================================

if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ============================================================
# MAP
# ============================================================

st.header(
    "🗺️ Traffic Report Map"
)


map_df = filtered_df[
    filtered_df["Latitude"].notna()
    &
    filtered_df["Longitude"].notna()
].copy()


map_df = map_df[
    (map_df["Latitude"] >= -90)
    &
    (map_df["Latitude"] <= 90)
    &
    (map_df["Longitude"] >= -180)
    &
    (map_df["Longitude"] <= 180)
]


if not map_df.empty:

    # Limit map points to avoid browser overload

    max_points = 5000

    if len(map_df) > max_points:

        map_df = map_df.sample(
            max_points,
            random_state=42
        )

        st.info(
            "Showing a sample of 5,000 locations "
            "to keep the map responsive."
        )


    fig = px.scatter_map(
        map_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Location",
        hover_data={
            "Traffic Report ID": True,
            "Issue Reported": True,
            "Status": True,
            "Agency": True,
            "Address": True,
            "Latitude": False,
            "Longitude": False
        },
        zoom=9,
        height=600
    )

    fig.update_layout(
        map_style="open-street-map",
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "No valid latitude/longitude coordinates."
    )


# ============================================================
# ISSUE VS STATUS
# ============================================================

st.header(
    "🔎 Issue vs Status"
)


issue_status = pd.crosstab(
    filtered_df["Issue Reported"],
    filtered_df["Status"]
)


issue_status["Total"] = (
    issue_status.sum(axis=1)
)


issue_status = (
    issue_status
    .sort_values(
        "Total",
        ascending=False
    )
    .head(15)
    .drop(
        columns="Total"
    )
)


if not issue_status.empty:

    fig = px.imshow(
        issue_status,
        text_auto=True,
        aspect="auto",
        title="Top Traffic Issues by Status"
    )

    fig.update_layout(
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AGENCY VS STATUS
# ============================================================

st.header(
    "🏢 Agency vs Status"
)


agency_status = pd.crosstab(
    filtered_df["Agency"],
    filtered_df["Status"]
)


agency_status["Total"] = (
    agency_status.sum(axis=1)
)


agency_status = (
    agency_status
    .sort_values(
        "Total",
        ascending=False
    )
    .head(15)
    .drop(
        columns="Total"
    )
)


if not agency_status.empty:

    fig = px.bar(
        agency_status,
        barmode="stack",
        title="Agency Status Distribution"
    )

    fig.update_layout(
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# STATUS DATE
# ============================================================

st.header(
    "⏱️ Status Date Analysis"
)


status_df = filtered_df[
    filtered_df["Status Date"].notna()
].copy()


if not status_df.empty:

    status_df["Month"] = (
        status_df["Status Date"]
        .dt.strftime("%Y-%m")
    )

    monthly = (
        status_df
        .groupby("Month")
        .size()
        .reset_index(
            name="Reports"
        )
    )

    fig = px.line(
        monthly,
        x="Month",
        y="Reports",
        markers=True,
        title="Reports by Status Date"
    )

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# DETAILED TABLE
# ============================================================

st.header(
    "📋 Detailed Traffic Reports"
)


st.dataframe(
    filtered_df,
    use_container_width=True,
    height=450
)


# ============================================================
# DOWNLOAD
# ============================================================

download_df = filtered_df.copy()

download_df["Published Date"] = (
    download_df["Published Date"]
    .astype(str)
)

download_df["Status Date"] = (
    download_df["Status Date"]
    .astype(str)
)


csv_data = download_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "⬇️ Download Filtered Data",
    data=csv_data,
    file_name="traffic_detailed_analysis.csv",
    mime="text/csv"
)