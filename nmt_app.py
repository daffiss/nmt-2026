import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import duckdb


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NMT 2026 Explorer",
    page_icon=None,
    layout="wide"
)


# ============================================================
# COLOR SYSTEM
# ============================================================

SUBJECT_PALETTE = [
    "#2563EB",
    "#7C3AED",
    "#059669",
    "#DB2777",
    "#0891B2",
    "#EA580C",
    "#4F46E5",
    "#65A30D",
    "#9333EA",
    "#0F766E",
    "#DC2626",
    "#475569"
]

MAIN_BLUE = "#2563EB"
DARK_NAVY = "#172033"
VIOLET = "#7C3AED"
MINT = "#059669"
PINK = "#DB2777"

HEATMAP_SCALE = [
    [0, "#F1F5F9"],
    [0.2, "#DBEAFE"],
    [0.4, "#BFDBFE"],
    [0.6, "#818CF8"],
    [0.8, "#6366F1"],
    [1, "#312E81"]
]

dashboard_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#334155",
            family="Arial"
        ),
        colorway=SUBJECT_PALETTE,
        xaxis=dict(
            gridcolor="#E8EDF5",
            zerolinecolor="#CBD5E1",
            linecolor="#CBD5E1"
        ),
        yaxis=dict(
            gridcolor="#E8EDF5",
            zerolinecolor="#CBD5E1",
            linecolor="#CBD5E1"
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#CBD5E1",
            font_color="#172033"
        )
    )
)

px.defaults.template = dashboard_template
px.defaults.color_discrete_sequence = SUBJECT_PALETTE


# ============================================================
# CUSTOM DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(37, 99, 235, 0.07),
                transparent 28%
            ),
            radial-gradient(
                circle at 0% 25%,
                rgba(124, 58, 237, 0.05),
                transparent 25%
            ),
            #F8FAFC;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 1500px;
    }

    h1 {
        color: #172033 !important;
        font-weight: 850 !important;
        letter-spacing: -1.5px;
        font-size: 2.7rem !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        color: #172033 !important;
        font-weight: 750 !important;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #64748B;
        font-size: 1.02rem;
        margin-top: 0.2rem;
        margin-bottom: 1.8rem;
        line-height: 1.6;
    }

    .section-header {
        margin-top: 1.8rem;
        margin-bottom: 0.3rem;
        padding: 0.85rem 1.1rem;
        border-radius: 14px;
        background: linear-gradient(
            90deg,
            #EFF6FF,
            #F5F3FF
        );
        border-left: 4px solid #2563EB;
        color: #172033;
        font-size: 1.18rem;
        font-weight: 800;
    }

    .section-description {
        color: #64748B;
        margin-top: 0.3rem;
        margin-bottom: 1rem;
        font-size: 0.91rem;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 6px 22px rgba(15, 23, 42, 0.05);
        min-height: 120px;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #172033 !important;
        font-weight: 850 !important;
        font-size: 1.8rem !important;
    }

    div[data-baseweb="select"] > div {
        border: 1px solid #CBD5E1 !important;
        border-radius: 11px !important;
        background-color: #FFFFFF !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #2563EB !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        background: #FFFFFF;
    }

    div[data-testid="stExpander"] summary {
        color: #172033;
        font-weight: 650;
    }

    hr {
        border-color: #E2E8F0 !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
    }

    .filter-label {
        color: #475569;
        font-size: 0.85rem;
        font-weight: 650;
        margin-bottom: 0.4rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUBJECTS
# ============================================================

subjects = {
    "Українська мова": "UkrBlockBall100",
    "Історія України": "HistBlockBall100",
    "Математика": "MathBlockBall100",
    "Фізика": "PhysBlockBall100",
    "Хімія": "ChemBlockBall100",
    "Біологія": "BioBlockBall100",
    "Географія": "GeoBlockBall100",
    "Англійська мова": "EngBlockBall100",
    "Французька мова": "FraBlockBall100",
    "Німецька мова": "DeuBlockBall100",
    "Іспанська мова": "SpaBlockBall100",
    "Українська література": "UkrLitBlockBall100"
}


# ============================================================
# LOAD DATA WITH DUCKDB
# ============================================================

@st.cache_resource
def get_connection():

    con = duckdb.connect("nmt.duckdb")

    con.execute("""
        CREATE TABLE IF NOT EXISTS nmt AS
        SELECT *
        FROM read_csv_auto(
            'OData2026.csv',
            header=true,
            nullstr='null'
        )
    """)

    con.execute("""
        CREATE OR REPLACE VIEW nmt_clean AS
        SELECT
            *,
            TRY_CAST(
                REPLACE(CAST("UkrBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS UkrScore,

            TRY_CAST(
                REPLACE(CAST("HistBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS HistScore,

            TRY_CAST(
                REPLACE(CAST("MathBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS MathScore,

            TRY_CAST(
                REPLACE(CAST("PhysBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS PhysScore,

            TRY_CAST(
                REPLACE(CAST("ChemBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS ChemScore,

            TRY_CAST(
                REPLACE(CAST("BioBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS BioScore,

            TRY_CAST(
                REPLACE(CAST("GeoBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS GeoScore,

            TRY_CAST(
                REPLACE(CAST("EngBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS EngScore,

            TRY_CAST(
                REPLACE(CAST("FraBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS FraScore,

            TRY_CAST(
                REPLACE(CAST("DeuBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS DeuScore,

            TRY_CAST(
                REPLACE(CAST("SpaBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS SpaScore,

            TRY_CAST(
                REPLACE(CAST("UkrLitBlockBall100" AS VARCHAR), ',', '.')
                AS DOUBLE
            ) AS UkrLitScore,

            2026 - TRY_CAST("Birth" AS INTEGER) AS Age

        FROM nmt
    """)

    return con


con = get_connection()


# ============================================================
# SCORE COLUMN MAPPING
# ============================================================

score_columns = {
    "Українська мова": "UkrScore",
    "Історія України": "HistScore",
    "Математика": "MathScore",
    "Фізика": "PhysScore",
    "Хімія": "ChemScore",
    "Біологія": "BioScore",
    "Географія": "GeoScore",
    "Англійська мова": "EngScore",
    "Французька мова": "FraScore",
    "Німецька мова": "DeuScore",
    "Іспанська мова": "SpaScore",
    "Українська література": "UkrLitScore"
}


# ============================================================
# HEADER
# ============================================================

st.title("NMT 2026 Explorer")

st.markdown(
    """
    <div class="hero-subtitle">
        Explore NMT 2026 results across subjects, regions and participant groups.
        Use the filters below to investigate patterns in the data.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILTER OPTIONS
# ============================================================

region_options = ["All"] + [
    x[0] for x in con.execute("""
        SELECT DISTINCT TRIM(CAST("RegName" AS VARCHAR))
        FROM nmt_clean
        WHERE "RegName" IS NOT NULL
            AND TRIM(CAST("RegName" AS VARCHAR)) != ''
        ORDER BY 1
    """).fetchall()
]

gender_options = ["All"] + [
    x[0] for x in con.execute("""
        SELECT DISTINCT TRIM(CAST("SexTypeName" AS VARCHAR))
        FROM nmt_clean
        WHERE "SexTypeName" IS NOT NULL
            AND TRIM(CAST("SexTypeName" AS VARCHAR)) != ''
        ORDER BY 1
    """).fetchall()
]

reg_type_options = ["All"] + [
    x[0] for x in con.execute("""
        SELECT DISTINCT TRIM(CAST("RegTypeName" AS VARCHAR))
        FROM nmt_clean
        WHERE "RegTypeName" IS NOT NULL
            AND TRIM(CAST("RegTypeName" AS VARCHAR)) != ''
        ORDER BY 1
    """).fetchall()
]


# ============================================================
# FILTERS
# ============================================================

st.markdown(
    """
    <div class="section-header">
        Explore results
    </div>

    <div class="section-description">
        Select a region, participant group, gender or subject to update the analysis.
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_region = st.selectbox(
        "Region",
        region_options
    )

with col2:
    selected_gender = st.selectbox(
        "Gender",
        gender_options
    )

with col3:
    selected_reg_type = st.selectbox(
        "Participant type",
        reg_type_options
    )

with col4:
    subject_options = ["All"] + list(subjects.keys())

    selected_subject = st.selectbox(
        "Subject",
        subject_options
    )


# ============================================================
# SQL FILTER
# ============================================================

conditions = []

if selected_region != "All":
    region_value = selected_region.replace("'", "''")

    conditions.append(
        f'TRIM(CAST("RegName" AS VARCHAR)) = \'{region_value}\''
    )

if selected_gender != "All":
    gender_value = selected_gender.replace("'", "''")

    conditions.append(
        f'TRIM(CAST("SexTypeName" AS VARCHAR)) = \'{gender_value}\''
    )

if selected_reg_type != "All":
    reg_type_value = selected_reg_type.replace("'", "''")

    conditions.append(
        f'TRIM(CAST("RegTypeName" AS VARCHAR)) = \'{reg_type_value}\''
    )

where_clause = ""

if conditions:
    where_clause = "WHERE " + " AND ".join(conditions)


# ============================================================
# INTERACTIVE ANALYSIS
# ============================================================

st.markdown(
    """
    <div class="section-header">
        Interactive analysis
    </div>

    <div class="section-description">
        These visualizations respond to the filters selected above.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPI SECTION
# ============================================================

st.divider()

if selected_subject != "All":

    score_col = score_columns[selected_subject]

    kpi_query = f"""
        SELECT
            COUNT("{score_col}") AS participants,
            AVG("{score_col}") AS average_score,
            MEDIAN("{score_col}") AS median_score,

            SUM(
                CASE
                    WHEN "{score_col}" >= 180
                    THEN 1 ELSE 0
                END
            ) AS high_score,

            SUM(
                CASE
                    WHEN "{score_col}" >= 200
                    THEN 1 ELSE 0
                END
            ) AS perfect_score

        FROM nmt_clean

        {where_clause}
    """

else:

    score_parts = []

    for score_col in score_columns.values():

        score_parts.append(
            f"""
            SELECT "{score_col}" AS score
            FROM nmt_clean
            {where_clause}
            """
        )

    all_scores_query = " UNION ALL ".join(score_parts)

    kpi_query = f"""
        WITH scores AS (
            {all_scores_query}
        )

        SELECT
            COUNT(*) AS participants,
            AVG(score) AS average_score,
            MEDIAN(score) AS median_score,

            SUM(
                CASE
                    WHEN score >= 180
                    THEN 1 ELSE 0
                END
            ) AS high_score,

            SUM(
                CASE
                    WHEN score >= 200
                    THEN 1 ELSE 0
                END
            ) AS perfect_score

        FROM scores
        WHERE score IS NOT NULL
    """


kpi = con.execute(kpi_query).fetchone()

total_participants = int(kpi[0] or 0)
average_score = float(kpi[1] or 0)
median_score = float(kpi[2] or 0)
high_score_count = int(kpi[3] or 0)
perfect_score_count = int(kpi[4] or 0)


k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Participants",
        f"{total_participants:,}"
    )

with k2:
    st.metric(
        "Average score",
        f"{average_score:.1f}"
    )

with k3:
    st.metric(
        "180+ results",
        f"{high_score_count:,}"
    )

with k4:
    st.metric(
        "200-point results",
        f"{perfect_score_count:,}"
    )


# ============================================================
# SCORE DISTRIBUTION
# ============================================================

st.divider()

st.subheader("Score distribution")


if selected_subject == "All":

    union_parts = []

    for subject_name, score_col in score_columns.items():

        union_parts.append(
            f"""
            SELECT
                '{subject_name}' AS Subject,
                CAST(
                    FLOOR("{score_col}" / 10
                ) * 10 AS INTEGER) AS Score,
                COUNT(*) AS Count

            FROM nmt_clean

            {where_clause}

            AND "{score_col}" IS NOT NULL

            GROUP BY Score
            """
            if where_clause
            else
            f"""
            SELECT
                '{subject_name}' AS Subject,
                CAST(
                    FLOOR("{score_col}" / 10
                ) * 10 AS INTEGER) AS Score,
                COUNT(*) AS Count

            FROM nmt_clean

            WHERE "{score_col}" IS NOT NULL

            GROUP BY Score
            """
        )

    distribution_df = con.execute(
        " UNION ALL ".join(union_parts)
        + " ORDER BY Subject, Score"
    ).df()

    if not distribution_df.empty:

        fig = px.bar(
            distribution_df,
            x="Score",
            y="Count",
            color="Subject",
            barmode="group",
            color_discrete_sequence=SUBJECT_PALETTE
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b>"
                "<br>Number of results: %{y:,}"
                "<extra></extra>"
            ),
            marker_line_width=0
        )

        fig.update_layout(
            xaxis=dict(
                type="category",
                title="Score range"
            ),
            yaxis=dict(
                title="Number of results",
                tickformat=","
            ),
            legend_title="Subject",
            height=550,
            margin=dict(l=20, r=20, t=30, b=30)
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

else:

    score_col = score_columns[selected_subject]

    distribution_df = con.execute(f"""
        SELECT
            CAST(
                FLOOR("{score_col}" / 10) * 10
                AS INTEGER
            ) AS Score,

            COUNT(*) AS Count

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "{score_col}" IS NOT NULL

        GROUP BY Score
        ORDER BY Score
    """).df()

    if not distribution_df.empty:

        fig = px.bar(
            distribution_df,
            x="Score",
            y="Count",
            color_discrete_sequence=[MAIN_BLUE]
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Number of participants: %{y:,}"
                "<extra></extra>"
            ),
            marker_line_width=0
        )

        fig.update_layout(
            xaxis=dict(
                type="category",
                title="Score range"
            ),
            yaxis=dict(
                title="Number of participants",
                tickformat=","
            ),
            height=550,
            margin=dict(l=20, r=20, t=30, b=30)
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:
        st.info("No score data available for the selected filters.")


# ============================================================
# SCORE RANGES
# ============================================================

st.divider()

st.subheader("Score ranges overview")

if not distribution_df.empty:

    score_ranges = distribution_df.copy()

    score_ranges["Score range"] = pd.cut(
        score_ranges["Score"],
        bins=[
            -1,
            99,
            119,
            139,
            159,
            179,
            199,
            200
        ],
        labels=[
            "Below 100",
            "100–119",
            "120–139",
            "140–159",
            "160–179",
            "180–199",
            "200"
        ],
        include_lowest=True
    )

    score_ranges = (
        score_ranges
        .groupby(
            "Score range",
            observed=False
        )["Count"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        score_ranges,
        names="Score range",
        values="Count",
        hole=0.58,
        color_discrete_sequence=[
            "#CBD5E1",
            "#93C5FD",
            "#60A5FA",
            "#818CF8",
            "#7C3AED",
            "#C026D3",
            "#059669"
        ]
    )

    fig.update_traces(
        textposition="outside",
        textinfo="percent",
        marker=dict(
            line=dict(
                color="#FFFFFF",
                width=3
            )
        ),
        hovertemplate=(
            "<b>%{label}</b>"
            "<br>Results: %{value:,}"
            "<br>Share: %{percent}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=500,
        legend_title="Score range",
        margin=dict(l=20, r=20, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# AGE ANALYSIS
# ============================================================

st.divider()

st.subheader("Age and performance")

if selected_subject != "All":

    score_col = score_columns[selected_subject]

    age_performance = con.execute(f"""
        SELECT
            Age,
            COUNT("{score_col}") AS Participants

        FROM nmt_clean

        {where_clause}

        GROUP BY Age

        HAVING Age IS NOT NULL

        ORDER BY Age
    """).df()

else:

    age_union = []

    for score_col in score_columns.values():

        age_union.append(
            f"""
            SELECT
                Age,
                COUNT("{score_col}") AS Participants

            FROM nmt_clean

            {where_clause}

            GROUP BY Age

            HAVING Age IS NOT NULL
            """
        )

    age_performance = con.execute(
        f"""
        SELECT
            Age,
            SUM(Participants) AS Participants

        FROM (
            {" UNION ALL ".join(age_union)}
        )

        GROUP BY Age
        ORDER BY Age
        """
    ).df()


if not age_performance.empty:

    age_performance["Age group"] = pd.cut(
        age_performance["Age"],
        bins=[0, 16, 18, 20, 25, 100],
        labels=["≤16", "17–18", "19–20", "21–25", "26+"]
    )

    age_grouped = (
        age_performance
        .groupby(
            "Age group",
            observed=False
        )["Participants"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        age_grouped,
        x="Age group",
        y="Participants",
        color="Age group",
        color_discrete_sequence=[
            "#2563EB",
            "#4F46E5",
            "#7C3AED",
            "#9333EA",
            "#C026D3"
        ],
        labels={
            "Age group": "Age group",
            "Participants": "Number of participants"
        }
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Age group: %{x}</b>"
            "<br>Participants: %{y:,}"
            "<extra></extra>"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(type="category"),
        yaxis=dict(
            title="Number of participants",
            tickformat=","
        ),
        height=500,
        margin=dict(l=20, r=20, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# GENDER COMPARISON
# ============================================================

st.divider()

st.subheader("NMT results by gender")


if selected_subject != "All":

    score_col = score_columns[selected_subject]

    gender_data = con.execute(f"""
        SELECT
            TRIM(CAST("SexTypeName" AS VARCHAR)) AS SexTypeName,

            CAST(
                FLOOR("{score_col}" / 10) * 10
                AS INTEGER
            ) AS Score,

            COUNT(*) AS Participants

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "SexTypeName" IS NOT NULL

        AND "{score_col}" IS NOT NULL

        GROUP BY
            SexTypeName,
            Score

        ORDER BY Score
    """).df()

else:

    gender_union = []

    for score_col in score_columns.values():

        gender_union.append(
            f"""
            SELECT
                TRIM(CAST("SexTypeName" AS VARCHAR))
                    AS SexTypeName,

                CAST(
                    FLOOR("{score_col}" / 10) * 10
                    AS INTEGER
                ) AS Score,

                COUNT(*) AS Participants

            FROM nmt_clean

            {where_clause}

            {"AND" if where_clause else "WHERE"}
            "SexTypeName" IS NOT NULL

            AND "{score_col}" IS NOT NULL

            GROUP BY
                SexTypeName,
                Score
            """
        )

    gender_data = con.execute(
        f"""
        SELECT
            SexTypeName,
            Score,
            SUM(Participants) AS Participants

        FROM (
            {" UNION ALL ".join(gender_union)}
        )

        GROUP BY
            SexTypeName,
            Score

        ORDER BY Score
        """
    ).df()


if not gender_data.empty:

    gender_colors = [
        MAIN_BLUE,
        PINK,
        VIOLET,
        MINT
    ]

    fig = px.bar(
        gender_data,
        x="Score",
        y="Participants",
        color="SexTypeName",
        barmode="group",
        color_discrete_sequence=gender_colors
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b>"
            "<br>Participants: %{y:,}"
            "<extra></extra>"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        xaxis=dict(
            type="category",
            title="Score range"
        ),
        yaxis=dict(
            title="Number of participants",
            tickformat=","
        ),
        legend_title="Gender",
        height=500,
        margin=dict(l=20, r=20, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# GENERAL OVERVIEW
# ============================================================

st.markdown(
    """
    <div class="section-header">
        General overview
    </div>

    <div class="section-description">
        A broader view of NMT 2026 across subjects, regions and participant groups.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUBJECT PERFORMANCE
# ============================================================

st.divider()

st.subheader("Subject performance")

subject_union = []

for subject_name, score_col in score_columns.items():

    subject_union.append(
        f"""
        SELECT
            '{subject_name}' AS Subject,
            "{score_col}" AS Score

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "{score_col}" IS NOT NULL
        """
    )

subject_stats_df = con.execute(
    f"""
    WITH scores AS (
        {" UNION ALL ".join(subject_union)}
    )

    SELECT
        Subject,
        AVG(Score) AS Average,
        MEDIAN(Score) AS Median,

        SUM(
            CASE
                WHEN Score >= 180
                THEN 1 ELSE 0
            END
        ) AS "180+",

        SUM(
            CASE
                WHEN Score >= 200
                THEN 1 ELSE 0
            END
        ) AS "200",

        COUNT(*) AS Participants

    FROM scores

    GROUP BY Subject
    ORDER BY Average
    """
).df()


if not subject_stats_df.empty:

    fig = px.scatter(
        subject_stats_df,
        x="Average",
        y="Subject",
        size="Participants",
        text="Average",
        color="Subject",
        color_discrete_sequence=SUBJECT_PALETTE,
        hover_data={
            "Average": ":.1f",
            "Median": ":.1f",
            "180+": True,
            "200": True,
            "Participants": ":,"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="middle right",
        marker=dict(
            line=dict(
                color="#FFFFFF",
                width=1.5
            ),
            opacity=0.88
        ),
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Average score: %{x:.1f}"
            "<br>Median score: %{customdata[0]:.1f}"
            "<br>180+ results: %{customdata[1]:,}"
            "<br>200-point results: %{customdata[2]:,}"
            "<br>Participants: %{customdata[3]:,}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Average score",
        yaxis_title="",
        height=550,
        margin=dict(l=20, r=50, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# SCORE × SUBJECT HEATMAP
# ============================================================

st.divider()

st.subheader("Score distribution by subject")

heatmap_union = []

for subject_name, score_col in score_columns.items():

    heatmap_union.append(
        f"""
        SELECT
            '{subject_name}' AS Subject,

            CASE
                WHEN "{score_col}" BETWEEN 100 AND 119
                    THEN '100–119'

                WHEN "{score_col}" BETWEEN 120 AND 139
                    THEN '120–139'

                WHEN "{score_col}" BETWEEN 140 AND 159
                    THEN '140–159'

                WHEN "{score_col}" BETWEEN 160 AND 179
                    THEN '160–179'

                WHEN "{score_col}" BETWEEN 180 AND 199
                    THEN '180–199'

                WHEN "{score_col}" = 200
                    THEN '200'

                ELSE NULL
            END AS "Score range",

            COUNT(*) AS Count

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "{score_col}" IS NOT NULL

        GROUP BY
            Subject,
            "Score range"

        HAVING "Score range" IS NOT NULL
        """
    )

heatmap_df = con.execute(
    " UNION ALL ".join(heatmap_union)
).df()

heatmap_pivot = heatmap_df.pivot(
    index="Subject",
    columns="Score range",
    values="Count"
).fillna(0)

heatmap_pivot = heatmap_pivot.reindex(
    columns=[
        "100–119",
        "120–139",
        "140–159",
        "160–179",
        "180–199",
        "200"
    ],
    fill_value=0
)

fig = px.imshow(
    heatmap_pivot,
    text_auto=".0f",
    aspect="auto",
    color_continuous_scale=HEATMAP_SCALE
)

fig.update_layout(
    xaxis_title="Score range",
    yaxis_title="",
    coloraxis_colorbar=dict(
        tickformat=","
    ),
    height=600,
    margin=dict(l=20, r=20, t=30, b=30)
)

st.plotly_chart(
    fig,
    width="stretch"
)


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

st.divider()

st.subheader("Regional performance")

regional_union = []

for subject_name, score_col in score_columns.items():

    regional_union.append(
        f"""
        SELECT
            "RegName" AS Region,
            "{score_col}" AS Score

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "RegName" IS NOT NULL
        AND "{score_col}" IS NOT NULL
        """
    )

regional_df = con.execute(
    f"""
    WITH regional_scores AS (
        {" UNION ALL ".join(regional_union)}
    )

    SELECT
        Region,
        AVG(Score) AS Average,
        COUNT(*) AS Participants

    FROM regional_scores

    GROUP BY Region

    ORDER BY Average DESC
    """
).df()


if not regional_df.empty:

    regional_df = regional_df.sort_values(
        "Average",
        ascending=False
    )

    fig = px.bar(
        regional_df.head(10),
        x="Average",
        y="Region",
        orientation="h",
        text="Average",
        color="Average",
        color_continuous_scale=[
            "#DBEAFE",
            "#60A5FA",
            "#2563EB",
            "#312E81"
        ],
        hover_data=["Participants"]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Average score: %{x:.1f}"
            "<br>Participants: %{customdata[0]:,}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        coloraxis_showscale=False,
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Average score",
        yaxis_title="",
        height=500,
        margin=dict(l=20, r=20, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# TOP REGIONS BY 180+
# ============================================================

st.divider()

st.subheader("Top regions by high scores")

regional_high_union = []

for subject_name, score_col in score_columns.items():

    regional_high_union.append(
        f"""
        SELECT
            TRIM(CAST("RegName" AS VARCHAR)) AS Region,
            "{score_col}" AS Score

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "RegName" IS NOT NULL
        AND "{score_col}" IS NOT NULL
        """
    )

regional_high_df = con.execute(
    f"""
    WITH regional_scores AS (
        {" UNION ALL ".join(regional_high_union)}
    )

    SELECT
        Region,
        SUM(
            CASE
                WHEN Score >= 180
                THEN 1 ELSE 0
            END
        ) AS "180+",
        COUNT(*) AS Participants

    FROM regional_scores

    GROUP BY Region

    ORDER BY "180+" DESC

    LIMIT 10
    """
).df()


if not regional_high_df.empty:

    regional_high_df = regional_high_df.sort_values(
        "180+",
        ascending=True
    )

    fig = px.bar(
        regional_high_df,
        x="180+",
        y="Region",
        orientation="h",
        text="180+",
        color="180+",
        color_continuous_scale=[
            "#D1FAE5",
            "#6EE7B7",
            "#10B981",
            "#047857"
        ],
        hover_data=["Participants"]
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>180+ results: %{x:,}"
            "<br>Total results: %{customdata[0]:,}"
            "<extra></extra>"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Number of 180+ results",
        yaxis_title="",
        height=500,
        margin=dict(l=20, r=20, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# REGIONAL PARTICIPANT SHARE
# ============================================================

st.divider()

st.subheader("Where did participants come from?")

region_counts = con.execute(f"""
    SELECT
        TRIM(CAST("RegName" AS VARCHAR)) AS RegName,
        COUNT(*) AS Participants

    FROM nmt_clean

    {where_clause}

    GROUP BY RegName

    ORDER BY Participants DESC
""").df()

if not region_counts.empty:

    fig = px.treemap(
        region_counts,
        path=["RegName"],
        values="Participants",
        color="Participants",
        color_continuous_scale=[
            "#EFF6FF",
            "#BFDBFE",
            "#60A5FA",
            "#2563EB",
            "#312E81"
        ]
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b>"
            "<br>Participants: %{value:,}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        coloraxis_showscale=False,
        height=600,
        margin=dict(l=10, r=10, t=20, b=20)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# PARTICIPANT TYPES
# ============================================================

st.divider()

st.subheader("Who took the NMT?")

participant_type = con.execute(f"""
    SELECT
        TRIM(CAST("RegTypeName" AS VARCHAR)) AS RegTypeName,
        COUNT(*) AS Participants

    FROM nmt_clean

    {where_clause}

    GROUP BY RegTypeName

    ORDER BY Participants DESC
""").df()

if not participant_type.empty:

    fig = px.treemap(
        participant_type,
        path=["RegTypeName"],
        values="Participants",
        color="Participants",
        color_continuous_scale=[
            "#F5F3FF",
            "#DDD6FE",
            "#A78BFA",
            "#7C3AED",
            "#4C1D95"
        ]
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b>"
            "<br>Participants: %{value:,}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        coloraxis_showscale=False,
        height=500,
        margin=dict(l=10, r=10, t=20, b=20)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# HIGH PERFORMERS
# ============================================================

st.divider()

st.subheader("High performers")

high_performer_union = []

for subject_name, score_col in score_columns.items():

    high_performer_union.append(
        f"""
        SELECT
            '{subject_name}' AS Subject,
            "{score_col}" AS Score

        FROM nmt_clean

        {where_clause}

        {"AND" if where_clause else "WHERE"}
        "{score_col}" IS NOT NULL
        """
    )


high_performers_df = con.execute(
    f"""
    WITH scores AS (
        {" UNION ALL ".join(high_performer_union)}
    )

    SELECT
        Subject,

        SUM(
            CASE
                WHEN Score >= 180
                THEN 1 ELSE 0
            END
        ) AS "180+",

        SUM(
            CASE
                WHEN Score >= 200
                THEN 1 ELSE 0
            END
        ) AS "200",

        COUNT(*) AS Participants,

        SUM(
            CASE
                WHEN Score >= 180
                THEN 1 ELSE 0
            END
        ) * 100.0 / COUNT(*) AS "180+ %"

    FROM scores

    GROUP BY Subject

    ORDER BY "180+ %"
    """
).df()


if not high_performers_df.empty:

    fig = px.bar(
        high_performers_df.sort_values(
            "180+ %",
            ascending=True
        ),
        x="180+ %",
        y="Subject",
        orientation="h",
        text="180+ %",
        color="180+ %",
        color_continuous_scale=[
            "#DBEAFE",
            "#93C5FD",
            "#6366F1",
            "#4338CA",
            "#312E81"
        ],
        hover_data=[
            "180+",
            "200",
            "Participants"
        ]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>180+ share: %{x:.1f}%"
            "<br>180+ results: %{customdata[0]:,}"
            "<br>200-point results: %{customdata[1]:,}"
            "<br>Participants: %{customdata[2]:,}"
            "<extra></extra>"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Share of participants with 180+",
        yaxis_title="",
        height=550,
        margin=dict(l=20, r=20, t=30, b=30)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# DATA PREVIEW
# ============================================================

st.divider()

with st.expander("View filtered data"):

    preview = con.execute(f"""
        SELECT *
        FROM nmt_clean

        {where_clause}

        LIMIT 1000
    """).df()

    st.dataframe(
        preview,
        width="stretch",
        height=400
    )