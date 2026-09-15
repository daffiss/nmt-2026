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
    "#0F766E", "#457B9D", "#E76F51", "#E9C46A",
    "#6D597A", "#84A98C", "#C97C5D", "#2A9D8F",
    "#7A8C99", "#9A6A7B", "#6B705C", "#526777"
]

MAIN_RED = "#0F766E"
DARK_BURGUNDY = "#1F2937"
RED = "#E76F51"
ROSE = "#2A9D8F"
WINE = "#457B9D"

HEATMAP_SCALE = [
    [0, "#F1F5F4"], [0.2, "#CDE7E2"], [0.4, "#8BCBC1"],
    [0.6, "#4FA79C"], [0.8, "#247F78"], [1, "#174C4A"]
]

dashboard_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            color="#3F2930",
            family="Arial"
        ),
        colorway=SUBJECT_PALETTE,
        xaxis=dict(
            gridcolor="#E8ECE9",
            zerolinecolor="#CDD8D5",
            linecolor="#B8C9C5"
        ),
        yaxis=dict(
            gridcolor="#E8ECE9",
            zerolinecolor="#CDD8D5",
            linecolor="#B8C9C5"
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#B8C9C5",
            font_color="#1F2937"
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
                rgba(166, 27, 50, 0.09),
                transparent 28%
            ),
            radial-gradient(
                circle at 0% 25%,
                rgba(194, 65, 79, 0.06),
                transparent 25%
            ),
            #F6F5F2;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 1500px;
    }

    h1 {
        color: #1F2937 !important;
        font-weight: 850 !important;
        letter-spacing: -1.5px;
        font-size: 2.7rem !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        color: #1F2937 !important;
        font-weight: 750 !important;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #667085;
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
            #EEF7F5,
            #FAFBFA
        );
        border-left: 4px solid #0F766E;
        color: #1F2937;
        font-size: 1.18rem;
        font-weight: 800;
    }

    .section-description {
        color: #667085;
        margin-top: 0.3rem;
        margin-bottom: 1rem;
        font-size: 0.91rem;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #E4E7E2;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 6px 22px rgba(15, 23, 42, 0.05);
        min-height: 120px;
    }

    div[data-testid="stMetricLabel"] {
        color: #667085 !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #1F2937 !important;
        font-weight: 850 !important;
        font-size: 1.8rem !important;
    }

    div[data-baseweb="select"] > div {
        border: 1px solid #B8C9C5 !important;
        border-radius: 11px !important;
        background-color: #FFFFFF !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #0F766E !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #E4E7E2;
        border-radius: 14px;
        background: #FFFFFF;
    }

    div[data-testid="stExpander"] summary {
        color: #1F2937;
        font-weight: 650;
    }

    hr {
        border-color: #E4E7E2 !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
    }

    .filter-label {
        color: #475467;
        font-size: 0.85rem;
        font-weight: 650;
        margin-bottom: 0.4rem;
    }


    .active-filter-note { color:#667085; font-size:0.78rem; margin:0.25rem 0 1.35rem 0.15rem; }
    div[data-testid="stExpander"] { border:1px solid #D7E2DF; border-radius:16px; background:rgba(255,255,255,0.94); box-shadow:0 8px 26px rgba(31,41,55,0.06); }
    div[data-testid="stExpander"] summary { padding:0.9rem 1rem; font-size:0.95rem; }
    .chart-note { color:#667085; font-size:0.82rem; line-height:1.45; margin:-0.25rem 0 0.65rem 0; }
    div[data-testid="stPlotlyChart"] { background:#FFFFFF; border:1px solid #E4E7E2; border-radius:16px; padding:0.15rem; box-shadow:0 7px 22px rgba(31,41,55,0.045); }

    /* Premium dashboard accents */
    h1 {
        position: relative;
        padding-bottom: 0.7rem;
    }

    h1::after {
        content: "";
        display: block;
        width: 64px;
        height: 4px;
        margin-top: 0.55rem;
        border-radius: 999px;
        background: linear-gradient(90deg, #0F766E, #457B9D, #E9C46A);
    }

    div[data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
    }

    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1F2937, #E76F51);
    }

    div[data-testid="stMetricValue"] {
        letter-spacing: -0.7px;
    }

    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #E4E7E2;
        border-radius: 18px;
        padding: 0.25rem;
        box-shadow: 0 8px 28px rgba(74, 17, 27, 0.06);
    }

    div[data-baseweb="select"] > div:focus-within {
        border-color: #0F766E !important;
        box-shadow: 0 0 0 2px rgba(166, 27, 50, 0.10) !important;
    }

    div[data-testid="stExpander"] {
        box-shadow: 0 6px 20px rgba(74, 17, 27, 0.04);
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
        A clean, interactive view of NMT 2026 results — explore patterns by subject, region and participant group.
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
# FILTER DRAWER
# ============================================================

with st.expander("Filters  ·  refine the view", expanded=False):
    st.markdown("Choose a subset of participants and the visualizations below will update automatically.")
    f1, f2, f3, f4 = st.columns([1.35, 1, 1, 1.2])
    with f1:
        selected_region = st.selectbox("Region", region_options)
    with f2:
        selected_gender = st.selectbox("Gender", gender_options)
    with f3:
        selected_reg_type = st.selectbox("Participant type", reg_type_options)
    with f4:
        subject_options = ["All"] + list(subjects.keys())
        selected_subject = st.selectbox("Subject", subject_options)

st.markdown("<div class=\"active-filter-note\">Filters are optional — the default view shows the full dataset.</div>", unsafe_allow_html=True)

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

st.subheader("Score distribution")

st.markdown("<div class=\"chart-note\">How results are distributed across the 100–200 scale.</div>", unsafe_allow_html=True)


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
            color_discrete_sequence=[MAIN_RED]
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

st.subheader("Score ranges overview")

st.markdown("<div class=\"chart-note\">A compact view of how results are concentrated across broad score bands.</div>", unsafe_allow_html=True)

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
            "#E8D7DA",
            "#F6BFC6",
            "#E98E98",
            "#2A9D8F",
            "#247F78",
            "#0F766E",
            "#174C4A"
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

left_col, right_col = st.columns(2)

with left_col:
    # ============================================================
    # AGE ANALYSIS
    # ============================================================

    st.subheader("Age and performance")

    st.markdown("<div class=\"chart-note\">Participant age groups shown as a population profile.</div>", unsafe_allow_html=True)

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
                "#0F766E",
                "#0F766E",
                "#247F78",
                "#E76F51",
                "#2A9D8F"
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



with right_col:
    # ============================================================
    # GENDER COMPARISON
    # ============================================================

    st.subheader("NMT results by gender")

    st.markdown("<div class=\"chart-note\">Compare score distributions across the available gender groups.</div>", unsafe_allow_html=True)


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

        gender_colors = ["#0F766E", "#E76F51", "#E9C46A", "#6D597A"]

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

left_col, right_col = st.columns(2)

with left_col:
    # ============================================================
    # SUBJECT PERFORMANCE
    # ============================================================

    st.subheader("Subject performance")

    st.markdown("<div class=\"chart-note\">Average score and participant volume across all NMT subjects.</div>", unsafe_allow_html=True)

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



with right_col:
    # ============================================================
    # SCORE × SUBJECT HEATMAP
    # ============================================================

    st.subheader("Score distribution by subject")

    st.markdown("<div class=\"chart-note\">A matrix view for scanning score ranges across subjects.</div>", unsafe_allow_html=True)

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

left_col, right_col = st.columns(2)

with left_col:
    # ============================================================
    # REGIONAL PERFORMANCE
    # ============================================================

    st.subheader("Regional performance")

    st.markdown("<div class=\"chart-note\">Average score by region for the selected participant set.</div>", unsafe_allow_html=True)

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
                "#FDE8EA",
                "#F5A6AE",
                "#E76F51",
                "#526777"
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



with right_col:
    # ============================================================
    # TOP REGIONS BY 180+
    # ============================================================

    st.subheader("Top regions by high scores")

    st.markdown("<div class=\"chart-note\">Regions with the largest number of 180+ results.</div>", unsafe_allow_html=True)

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
                "#EAF4F2",
                "#9BCBC3",
                "#E76F51",
                "#1F2937"
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

left_col, right_col = st.columns(2)

with left_col:
    # ============================================================
    # REGIONAL PARTICIPANT SHARE
    # ============================================================

    st.subheader("Where did participants come from?")

    st.markdown("<div class=\"chart-note\">The relative size of the participant population across regions.</div>", unsafe_allow_html=True)

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
                "#EEF7F5",
                "#BFDBFE",
                "#60A5FA",
                "#0F766E",
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



with right_col:
    # ============================================================
    # PARTICIPANT TYPES
    # ============================================================

    st.subheader("Who took the NMT?")

    st.markdown("<div class=\"chart-note\">Participant composition by registration type.</div>", unsafe_allow_html=True)

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
            color_continuous_scale=["#F5F2F7", "#DDD4E4", "#B5A3C0", "#806A8F", "#4C3D55"]
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

st.subheader("High performers")

st.markdown("<div class=\"chart-note\">The share of results reaching 180+ for each subject.</div>", unsafe_allow_html=True)

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
            "#EEF7F5",
            "#F5B0B8",
            "#2A9D8F",
            "#0F766E",
            "#174C4A"
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