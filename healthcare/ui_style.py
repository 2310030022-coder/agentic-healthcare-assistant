
import streamlit as st
from html import escape


# =====================================================
# GLOBAL WEBSITE STYLING
# =====================================================

def apply_custom_style():

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 95% 5%,
                    #e7e1ff 0%,
                    transparent 35%
                ),
                radial-gradient(
                    circle at 5% 90%,
                    #dff6ff 0%,
                    transparent 40%
                ),
                linear-gradient(
                    135deg,
                    #f8fbff,
                    #f6f4ff
                );

            color: #172b4d;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* HEADINGS */

        h1, h2, h3 {
            color: #17356c;
            font-weight: 800;
        }

        h1 {
            letter-spacing: -1px;
        }

        /* SIDEBAR */

        [data-testid="stSidebar"] {
            background: linear-gradient(
                175deg,
                #14275f 0%,
                #32318b 50%,
                #146c94 100%
            );
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] [role="radiogroup"] p {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.2);
        }

        /* SIDEBAR PATIENT DROPDOWN */

        [data-testid="stSidebar"] [data-baseweb="select"],
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: white !important;
            border-radius: 12px !important;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] *,
        [data-testid="stSidebar"] [data-baseweb="select"] input {
            color: #163253 !important;
            -webkit-text-fill-color: #163253 !important;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] svg {
            color: #163253 !important;
            fill: #163253 !important;
        }

        [data-baseweb="popover"] [role="listbox"] {
            background: #ffffff !important;
        }

        [data-baseweb="popover"] [role="option"],
        [data-baseweb="popover"] [role="option"] * {
            color: #163253 !important;
            -webkit-text-fill-color: #163253 !important;
        }

        [data-baseweb="popover"] [aria-selected="true"] {
            background: #e8f1ff !important;
        }

        /* HERO BANNER */

        .hero-banner {
            background: linear-gradient(
                115deg,
                #1769dd,
                #6549d8 55%,
                #10a7b8
            );

            padding: 35px;
            border-radius: 24px;
            color: white;

            box-shadow:
                0 15px 35px rgba(55,80,170,0.2);

            margin-bottom: 30px;
        }

        .hero-banner h2 {
            color: white !important;
            font-size: 2rem;
            margin-bottom: 12px;
        }

        .hero-banner p {
            color: #f0f5ff !important;
            font-size: 1.05rem;
            line-height: 1.7;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 18px;
        }

        /* METRIC CARDS */

        [data-testid="stMetric"] {
            background: linear-gradient(
                145deg,
                #ffffff,
                #f1f6ff
            );

            border: 1px solid #e0e8fa;
            border-radius: 18px;
            padding: 22px;

            box-shadow:
                0 8px 25px rgba(35,65,125,0.07);
        }

        [data-testid="stMetricValue"] {
            color: #2559c2;
            font-weight: 800;
        }

        /* BUTTONS */

        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            transition: all 0.2s ease;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(
                110deg,
                #1675e8,
                #7146e3
            );

            color: white !important;
            border: none;

            box-shadow:
                0 7px 20px rgba(75,70,200,0.2);
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(
                110deg,
                #105ec2,
                #5c35c5
            );
        }

        div.stButton > button[kind="secondary"] {
            background: #ffffff;
            color: #2454a3;
            border: 1px solid #cddcf7;
        }

        div.stButton > button[kind="secondary"]:hover {
            background: #edf4ff;
            border-color: #83a6ed;
        }

        /* FEATURE CARD CONTAINERS */

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 18px;
        }

        /* INPUT FIELDS */

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 12px;
            background: #ffffff;
            color: #172b4d;
            border: 1px solid #d3dff3;
        }

        /* FORMS */

        [data-testid="stForm"] {
            background: rgba(255,255,255,0.9);
            border: 1px solid #e0e8f8;
            border-radius: 20px;
            padding: 20px;
        }

        /* DATAFRAMES */

        [data-testid="stDataFrame"] {
            border-radius: 15px;
            overflow: hidden;
        }

        /* ALERTS */

        [data-testid="stAlert"] {
            border-radius: 14px;
        }

        /* FOOTER */

        .footer {
            text-align: center;
            padding: 25px;
            color: #70809b;
            font-size: 13px;
            line-height: 1.9;
        }

        /* RESPONSIVE */

        @media (max-width: 768px) {

            .block-container {
                padding: 1rem;
            }

            .hero-banner {
                padding: 22px;
            }

            .hero-banner h2 {
                font-size: 1.5rem;
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
                ✨ AI-POWERED HEALTHCARE PLATFORM
            </div>

            <h2>
                Smarter Care. Seamless Coordination.
            </h2>

            <p>
                Manage fictional patient records,
                explore medical departments,
                discover available appointments,
                summarize medical histories,
                and search trusted healthcare information.
            </p>

            <p>
                Powered by Gemini AI, LangGraph,
                FAISS and Streamlit.
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
            "icon": "📅",
            "title": "Smart Appointments",
            "description": (
                "Choose a department, select a doctor, "
                "and confirm a simulated appointment."
            ),
            "page": "📅 Appointments",
            "color": "#e9f1ff"
        },
        {
            "icon": "📋",
            "title": "Medical Records",
            "description": (
                "Add and update fictional patient "
                "diagnoses, treatments and notes."
            ),
            "page": "📋 Medical Records",
            "color": "#f1eaff"
        },
        {
            "icon": "🩺",
            "title": "History Summary",
            "description": (
                "Retrieve patient medical history "
                "and generate an AI summary."
            ),
            "page": "🩺 History Summary",
            "color": "#e2faf3"
        },
        {
            "icon": "🔎",
            "title": "Medical Research",
            "description": (
                "Search trusted educational "
                "medical information sources."
            ),
            "page": "🔎 Medical Research",
            "color": "#fff2e2"
        }
    ]

    columns = st.columns(
        4,
        gap="medium"
    )

    for index, feature in enumerate(features):

        with columns[index]:

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div style="
                        background:{feature['color']};
                        border-radius:14px;
                        padding:20px;
                        text-align:center;
                        font-size:36px;
                        margin-bottom:15px;
                    ">
                        {feature['icon']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"#### {escape(feature['title'])}"
                )

                st.caption(
                    feature["description"]
                )

                if st.button(
                    "Open Module →",
                    key=f"feature_card_{index}",
                    use_container_width=True
                ):

                    # Do not directly modify the sidebar
                    # radio widget after it has been created.
                    # app.py reads this on the next rerun.

                    st.session_state["_next_page"] = (
                        feature["page"]
                    )

                    st.rerun()
