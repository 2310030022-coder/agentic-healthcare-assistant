import streamlit as st


def apply_custom_style():
    st.markdown('''
    <style>
    .stApp {background:linear-gradient(125deg,#f3f9ff,#f8f4ff 65%,#eafbf8);color:#162b50}
    .block-container {max-width:1450px;padding-top:1.5rem}
    [data-testid="stSidebar"] {background:linear-gradient(165deg,#142b68,#45339b 58%,#137e9a)}
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {color:#fff!important}
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="select"] input {
      color:#142a4e!important;-webkit-text-fill-color:#142a4e!important}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {background:#fff!important}
    [data-baseweb="popover"] [role="option"] * {color:#142a4e!important}
    h1,h2,h3 {color:#163268}
    [data-testid="stMetric"] {background:#fff;border:1px solid #dfe9fa;
      border-radius:16px;padding:15px}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px}
    div.stButton>button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"] {
      background:linear-gradient(95deg,#1779e8,#7046e6);color:white!important;
      border:0;border-radius:12px}
    div.stButton>button {border-radius:12px}
    .hero {background:linear-gradient(105deg,#1968d7,#6b4bdb,#0fa4aa);
      padding:28px;border-radius:22px;color:white;margin-bottom:22px}
    .hero h2,.hero p {color:white!important}
    .tile {padding:18px;border-radius:14px;text-align:center;font-size:32px}
    .footer {text-align:center;color:#71809b;font-size:12px;padding:24px}
    </style>
    ''', unsafe_allow_html=True)


def render_hero():
    st.markdown('''<div class="hero"><h2>🏥 MediFlow AI — Smart Healthcare Workspace</h2>
    <p>Patient registration • Simulated appointments • Medical records • AI history summaries • Trusted research</p>
    </div>''', unsafe_allow_html=True)


def render_feature_cards():
    features = [
        ('📅','Smart Booking','Find a department, doctor and available time.','📅 Appointments','#e9e7ff'),
        ('📋','Medical Records','Add or update fictional patient history.','📋 Medical Records','#e5f8f2'),
        ('🩺','History Summary','Generate an AI summary of past records.','🩺 History Summary','#e8f1ff'),
        ('🔎','Medical Research','Search trusted health information.','🔎 Medical Research','#fff1df'),
    ]
    for col, (emoji,title,description,page,color) in zip(st.columns(4),features):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="tile" style="background:{color}">{emoji}</div>',unsafe_allow_html=True)
                st.markdown(f'#### {title}')
                st.caption(description)
                if st.button('Open Module →',key=f'card_{page}',use_container_width=True):
                    st.session_state['_next_page']=page
                    st.rerun()
