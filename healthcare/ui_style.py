
import streamlit as st


def apply_custom_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(
            125deg,
            #f4faff 0%,
            #f8f5ff 55%,
            #eefaf8 100%
        );
        color: #142c4d;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #173d76;
        font-weight: 800;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            170deg,
            #102c67 0%,
            #2546a2 48%,
            #087b9b 100%
        );
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 7px 6px;
        border-radius: 9px;
    }

    [data-testid="stSidebar"] [role="radiogroup"] p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        line-height: 1.45 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.14);
    }

    [data-testid="stSidebar"] [data-baseweb="radio"] {
        accent-color: #55f2d5;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.25);
    }

    /* PATIENT DROPDOWN */

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 2px solid #bce9ff !important;
        border-radius: 12px !important;
        min-height: 48px;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #173456 !important;
        -webkit-text-fill-color: #173456 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: #173456 !important;
    }

    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] [role="option"] * {
        color: #173456 !important;
        -webkit-text-fill-color: #173456 !important;
    }

    /* ALL BUTTONS */

    div.stButton > button {
        min-height: 46px;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 750 !important;
        transition: all 0.15s ease;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(
            100deg,
            #146ce4,
            #6744dc
        ) !important;
        color: #ffffff !important;
        border: none !important;
    }

    div.stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #194c9b !important;
        border: 2px solid #a9c7f5 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: #eaf2ff !important;
        color: #143d80 !important;
        border-color: #3478e0 !important;
    }

    div.stButton > button:disabled {
        opacity: 0.65;
    }

    /* SIDEBAR REGISTRATION BUTTON */

    [data-testid="stSidebar"] div.stButton > button {
        background: #ffffff !important;
        color: #123f85 !important;
        border: 2px solid #c1e9ff !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        min-height: 50px;
    }

    [data-testid="stSidebar"] div.stButton > button p {
        color: #123f85 !important;
        font-weight: 800 !important;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background: #dff7ff !important;
    }

    /* METRICS */

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dbe7f8;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(20,60,130,0.06);
    }

    [data-testid="stMetricValue"] {
        color: #185bc4;
        font-weight: 800;
    }

    /* INPUTS */

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        background: #ffffff !important;
        color: #183656 !important;
        border-radius: 10px !important;
        border: 1px solid #b9cce8 !important;
    }

    /* FORMS */

    [data-testid="stForm"] {
        background: rgba(255,255,255,0.95);
        border: 1px solid #d7e5f8;
        border-radius: 18px;
        padding: 20px;
    }

    /* ALERTS */

    [data-testid="stAlert"] {
        border-radius: 14px;
        font-weight: 500;
    }

    /* DATA TABLES */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* FEATURE CARDS */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero():
    # Native Streamlit components prevent raw HTML display.

    with st.container(border=True):
        st.caption("✨ INTELLIGENT HEALTHCARE WORKSPACE")

        st.title("Smarter Care. Seamless Coordination.")

        st.write(
            "An interactive healthcare workflow demonstration "
            "for managing fictional patients, exploring medical "
            "departments, scheduling simulated appointments, "
            "reviewing medical histories, and researching "
            "trusted health information."
        )

        st.markdown(
            "**Gemini AI  •  LangGraph  •  FAISS  •  Streamlit**"
        )

        st.info(
            "Clinical-style educational prototype. "
            "Not approved for real patient care."
        )


def render_feature_cards():

    features = [
        {
            "icon": "📅",
            "title": "Smart Appointments",
            "description": (
                "Select a department, choose a doctor "
                "and confirm a simulated booking."
            ),
            "page": "📅 Appointments"
        },
        {
            "icon": "📋",
            "title": "Medical Records",
            "description": (
                "Add or update patient history, "
                "diagnoses, treatments and notes."
            ),
            "page": "📋 Medical Records"
        },
        {
            "icon": "🩺",
            "title": "History Summary",
            "description": (
                "Retrieve existing records and "
                "generate an AI history summary."
            ),
            "page": "🩺 History Summary"
        },
        {
            "icon": "🔎",
            "title": "Medical Research",
            "description": (
                "Explore trusted educational "
                "medical information."
            ),
            "page": "🔎 Medical Research"
        }
    ]

    columns = st.columns(4, gap="medium")

    for index, feature in enumerate(features):
        with columns[index]:
            with st.container(border=True):

                st.markdown(
                    f"## {feature['icon']}"
                )

                st.markdown(
                    f"#### {feature['title']}"
                )

                st.write(feature["description"])

                if st.button(
                    "Open Module →",
                    key=f"feature_card_{index}",
                    use_container_width=True
                ):
                    # Defer sidebar navigation until next run.
                    st.session_state["_next_page"] = (
                        feature["page"]
                    )
                    st.rerun()
