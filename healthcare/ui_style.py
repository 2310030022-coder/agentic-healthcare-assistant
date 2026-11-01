
import streamlit as st


def apply_custom_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"], [data-testid="stApp"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 95% 8%, #e9e4ff 0%, transparent 30%),
                radial-gradient(circle at 5% 85%, #d9f6ff 0%, transparent 35%),
                linear-gradient(145deg, #f7fbff 0%, #f7f5ff 55%, #f0fbfa 100%);
            color: #182642;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(
                175deg,
                #13275e 0%,
                #33328c 48%,
                #166e95 100%
            );
        }

        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stSelectbox label {
            font-weight: 600;
        }

        [data-testid="stSidebar"] [data-baseweb="select"] * {
            color: #182642 !important;
        }

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: #1a3060 !important;
            font-weight: 800 !important;
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

        .hero-banner {
            background: linear-gradient(
                115deg,
                #1964d9 0%,
                #6547cf 55%,
                #16a8b6 100%
            );
            border-radius: 24px;
            padding: 32px;
            color: white;
            margin: 12px 0 25px;
            box-shadow: 0 16px 36px rgba(69, 85, 177, 0.18);
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

        [data-testid="stMetric"] {
            background: linear-gradient(
                145deg,
                #ffffff 0%,
                #f3f7ff 100%
            );
            border: 1px solid #e2e9fb;
            border-radius: 20px;
            padding: 22px;
            box-shadow: 0 8px 24px rgba(30, 66, 127, 0.06);
            transition: transform 0.2s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-3px);
        }

        [data-testid="stMetricLabel"] {
            color: #5c6b86;
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: #2356bc;
            font-weight: 800;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(
                110deg,
                #1677e7,
                #6c4ce4
            );
            color: white;
            border: none;
            border-radius: 13px;
            font-weight: 700;
            padding: 0.65rem 1.4rem;
            box-shadow: 0 6px 18px rgba(73, 82, 204, 0.2);
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(
                110deg,
                #105ec1,
                #5335c6
            );
            color: white;
        }

        div.stButton > button[kind="secondary"] {
            border: 1px solid #cddcf7;
            border-radius: 12px;
            color: #2856a1;
            background: #ffffff;
            font-weight: 600;
        }

        div[data-testid="stForm"] {
            background: rgba(255,255,255,0.88);
            border: 1px solid #e0e8fa;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(40, 70, 130, 0.05);
        }

        div[data-testid="stExpander"] {
            background: rgba(255,255,255,0.9);
            border: 1px solid #e0e8f7;
            border-radius: 15px;
            overflow: hidden;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: #ffffff;
            border: 1px solid #d4dff1;
            border-radius: 12px;
            color: #182642;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #e0e8f7;
        }

        [data-testid="stAlert"] {
            border-radius: 14px;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 22px 0;
        }

        .feature-card {
            background: white;
            border: 1px solid #e3eaf9;
            border-radius: 19px;
            padding: 22px;
            box-shadow: 0 8px 25px rgba(37, 69, 131, 0.06);
        }

        .feature-icon {
            font-size: 1.8rem;
            margin-bottom: 12px;
        }

        .feature-card h3 {
            font-size: 1rem;
            margin-bottom: 7px;
        }

        .feature-card p {
            color: #65748d;
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .section-label {
            display: inline-block;
            background: #e8efff;
            color: #315bc0;
            padding: 7px 13px;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 12px;
        }

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


def render_hero():
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-badge">
                ✦ AI-POWERED HEALTHCARE PLATFORM
            </div>
            <h2>Smarter Care. Seamless Coordination.</h2>
            <p>
                Your intelligent workspace for patient records,
                appointment management, trusted medical research,
                and explainable AI workflows.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_feature_cards():
    st.markdown(
        """
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3>Intelligent AI Agent</h3>
                <p>Multi-step planning and medical task coordination.</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">📅</div>
                <h3>Smart Appointments</h3>
                <p>Browse doctors and manage simulated bookings.</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3>Semantic Memory</h3>
                <p>Find relevant patient context using FAISS.</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Agent Analytics</h3>
                <p>Explore execution traces and evaluation metrics.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
