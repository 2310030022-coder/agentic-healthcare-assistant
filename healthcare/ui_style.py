
import streamlit as st


# =====================================================
# PREMIUM MEDIFLOW AI STYLING
# =====================================================

def apply_custom_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 95% 8%,
                    #e9e4ff 0%, transparent 30%),
                radial-gradient(circle at 5% 85%,
                    #d9f6ff 0%, transparent 35%),
                linear-gradient(
                    145deg,
                    #f7fbff 0%,
                    #f7f5ff 55%,
                    #f0fbfa 100%
                );
            color: #182642;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }

        /* SIDEBAR */

        [data-testid="stSidebar"] {
            background: linear-gradient(
                175deg,
                #13275e 0%,
                #33328c 48%,
                #166e95 100%
            );
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] [role="radiogroup"] p {
            color: white !important;
        }

        /* PATIENT SELECTOR */

        [data-testid="stSidebar"] [data-baseweb="select"],
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #ffffff !important;
            border-radius: 12px !important;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] *,
        [data-testid="stSidebar"] [data-baseweb="select"] input {
            color: #17324d !important;
            -webkit-text-fill-color: #17324d !important;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] svg {
            color: #17324d !important;
            fill: #17324d !important;
        }

        [data-baseweb="popover"] [role="listbox"] {
            background: white !important;
        }

        [data-baseweb="popover"] [role="option"],
        [data-baseweb="popover"] [role="option"] * {
            color: #17324d !important;
            -webkit-text-fill-color: #17324d !important;
        }

        [data-baseweb="popover"] [aria-selected="true"] {
            background: #e7f1ff !important;
        }

        /* HEADINGS */

        h1, h2, h3 {
            color: #1a3060;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .main-title {
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 800;
            line-height: 1.2;
            background: linear-gradient(
                100deg,
                #1169c6,
                #6544cc,
                #009eaf
            );
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #63718c;
            font-size: 1.05rem;
            margin-bottom: 22px;
        }

        /* HERO */

        .hero-banner {
            background: linear-gradient(
                115deg,
                #1964d9,
                #6547cf 55%,
                #16a8b6
            );
            border-radius: 24px;
            padding: 32px;
            color: white;
            margin: 12px 0 25px;
            box-shadow: 0 16px 36px
                rgba(69, 85, 177, 0.18);
        }

        .hero-banner h2 {
            color: white !important;
            font-size: 1.8rem;
            margin-bottom: 8px;
        }

        .hero-banner p {
            color: #f0f4ff;
            font-size: 1rem;
            margin-bottom: 0;
        }

        .hero-badge {
            display: inline-block;
            padding: 7px 13px;
            border-radius: 100px;
            background: rgba(255,255,255,0.19);
            border: 1px solid rgba(255,255,255,0.25);
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 16px;
            color: white;
        }

        /* SECTION HEADERS */

        .section-header {
            background: linear-gradient(
                110deg,
                #eaf3ff,
                #f1edff
            );
            border: 1px solid #dce7fb;
            border-radius: 18px;
            padding: 20px 24px;
            margin: 12px 0 24px;
        }

        .section-header h2 {
            margin: 0;
            color: #244b9b;
        }

        .section-header p {
            color: #60728f;
            margin: 8px 0 0;
            font-size: 15px;
        }

        /* METRIC CARDS */

        [data-testid="stMetric"] {
            background: linear-gradient(
                145deg,
                #ffffff,
                #f3f7ff
            );
            border: 1px solid #e2e9fb;
            border-radius: 20px;
            padding: 22px;
            box-shadow: 0 8px 24px
                rgba(30, 66, 127, 0.06);
        }

        [data-testid="stMetricLabel"] {
            color: #5c6b86;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: #2356bc;
            font-weight: 800;
        }

        /* BUTTONS */

        div.stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"]
        button[kind="primary"] {
            background: linear-gradient(
                110deg,
                #1677e7,
                #6c4ce4
            );
            color: white !important;
            border: none;
            border-radius: 13px;
            font-weight: 700;
            padding: 0.65rem 1.4rem;
            box-shadow: 0 6px 18px
                rgba(73, 82, 204, 0.2);
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(
                110deg,
                #105ec1,
                #5335c6
            );
            color: white !important;
        }

        div.stButton > button[kind="secondary"] {
            border: 1px solid #cddcf7;
            border-radius: 12px;
            color: #2856a1;
            background: #ffffff;
            font-weight: 600;
        }

        /* FORMS */

        div[data-testid="stForm"] {
            background: rgba(255,255,255,0.88);
            border: 1px solid #e0e8fa;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 24px
                rgba(40, 70, 130, 0.05);
        }

        /* EXPANDERS */

        div[data-testid="stExpander"] {
            background: rgba(255,255,255,0.9);
            border: 1px solid #e0e8f7;
            border-radius: 15px;
            overflow: hidden;
        }

        /* INPUTS */

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: #ffffff;
            border: 1px solid #d4dff1;
            border-radius: 12px;
            color: #182642;
            -webkit-text-fill-color: #182642;
        }

        /* TABLES */

        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #e0e8f7;
        }

        [data-testid="stAlert"] {
            border-radius: 14px;
        }

        /* FOOTER */

        .footer-text {
            text-align: center;
            padding: 22px 10px;
            color: #64748b;
            font-size: 13px;
            line-height: 1.8;
        }

        /* MOBILE */

        @media (max-width: 700px) {
            .block-container {
                padding: 1rem;
            }

            .hero-banner {
                padding: 22px;
                border-radius: 18px;
            }

            .hero-banner h2 {
                font-size: 1.4rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# HERO BANNER
# =====================================================

def render_hero():
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-badge">
                ✦ AI-POWERED HEALTHCARE PLATFORM
            </div>
            <h2>Smarter Care. Seamless Coordination.</h2>
            <p>
                Your intelligent workspace for patient
                records, appointment management,
                trusted medical research, and
                explainable AI workflows.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# INTERACTIVE FEATURE CARDS
# =====================================================

def render_feature_cards():

    features = [
        {
            "icon": "🤖",
            "title": "Intelligent AI Agent",
            "description": (
                "Plan multi-step healthcare tasks "
                "using Gemini AI and LangGraph."
            ),
            "page": "🤖 AI Healthcare Assistant",
            "color": "#eaf2ff"
        },
        {
            "icon": "📅",
            "title": "Smart Appointments",
            "description": (
                "Choose a medical department and "
                "book simulated appointments."
            ),
            "page": "📅 Appointments",
            "color": "#f1eaff"
        },
        {
            "icon": "🧠",
            "title": "Semantic Memory",
            "description": (
                "Search fictional patient records "
                "with FAISS vector retrieval."
            ),
            "page": "🧠 FAISS Memory",
            "color": "#e4fbf7"
        },
        {
            "icon": "📊",
            "title": "Agent Analytics",
            "description": (
                "Explore agent logs, execution "
                "traces, and evaluation metrics."
            ),
            "page": "📊 Evaluation & Monitoring",
            "color": "#fff2e5"
        }
    ]

    columns = st.columns(4, gap="medium")

    for index, (column, feature) in enumerate(
        zip(columns, features)
    ):
        with column:
            with st.container(border=True):

                st.markdown(
                    f"""
                    <div style="
                        background:{feature['color']};
                        padding:16px;
                        border-radius:12px;
                        text-align:center;
                        font-size:32px;
                        margin-bottom:12px;
                    ">
                        {feature['icon']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"#### {feature['title']}"
                )

                st.caption(feature["description"])

                if st.button(
                    "Open Module →",
                    key=f"feature_open_{index}",
                    use_container_width=True
                ):
                    st.session_state.current_page = feature["page"]
                    st.rerun()
