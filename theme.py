import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>

        /* ================================
           MAIN APPLICATION
        ================================= */

        .stApp {
            background:
                radial-gradient(circle at 80% 10%,
                    rgba(0, 174, 239, 0.08),
                    transparent 30%),
                linear-gradient(
                    135deg,
                    #06101d 0%,
                    #091a2c 50%,
                    #071522 100%
                );

            color: #eaf3fc;
        }


        /* Main content container */

        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }


        /* ================================
           STREAMLIT HEADER
        ================================= */

        [data-testid="stHeader"] {
            background: rgba(6, 16, 29, 0.90);
            backdrop-filter: blur(10px);
        }


        /* ================================
           SIDEBAR
        ================================= */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #081827,
                    #06111e
                );

            border-right: 1px solid #18344b;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: #dbeaf7 !important;
        }


        /* ================================
           TYPOGRAPHY
        ================================= */

        h1 {
            color: #ffffff !important;
            font-weight: 800 !important;
            letter-spacing: -0.7px;
        }

        h2 {
            color: #f3f8ff !important;
            font-weight: 750 !important;
        }

        h3 {
            color: #dff5ff !important;
            font-weight: 700 !important;
        }

        p {
            color: #bfd0df;
        }

        label {
            color: #d7e6f3 !important;
        }

        [data-testid="stCaptionContainer"] {
            color: #8faabd !important;
        }


        /* ================================
           DASHBOARD CARDS
        ================================= */

        .metric-card {

            background:
                linear-gradient(
                    145deg,
                    rgba(15, 42, 67, 0.96),
                    rgba(7, 25, 42, 0.96)
                );

            border: 1px solid rgba(53, 155, 190, 0.30);

            border-radius: 16px;

            padding: 20px;

            min-height: 125px;

            margin-bottom: 15px;

            box-shadow:
                0 8px 30px rgba(0,0,0,0.25),
                inset 0 1px 0 rgba(255,255,255,0.04);
        }


        .metric-label {

            color: #89a9bf;

            font-size: 12px;

            font-weight: 600;

            text-transform: uppercase;

            letter-spacing: 1px;
        }


        .metric-value {

            color: #ffffff;

            font-size: 28px;

            font-weight: 800;

            margin-top: 8px;
        }


        .metric-note {

            color: #45e0bf;

            font-size: 12px;

            margin-top: 5px;
        }


        /* ================================
           FEATURE CARDS
        ================================= */

        .feature-card {

            background:
                linear-gradient(
                    145deg,
                    rgba(14, 39, 63, 0.95),
                    rgba(7, 23, 39, 0.95)
                );

            border: 1px solid #24465f;

            border-radius: 16px;

            padding: 20px;

            margin-bottom: 15px;

            box-shadow: 0 8px 25px rgba(0,0,0,0.20);
        }


        .feature-card p {
            color: #bcd0df;
            line-height: 1.6;
        }


        /* ================================
           BUTTONS
        ================================= */

        .stButton > button {

            background:
                linear-gradient(
                    135deg,
                    #0786b6,
                    #056c99
                );

            color: white !important;

            border: 1px solid #27b5d5;

            border-radius: 9px;

            font-weight: 650;

            min-height: 42px;

            transition: all 0.2s ease;
        }


        .stButton > button:hover {

            background:
                linear-gradient(
                    135deg,
                    #08a1d7,
                    #087ba7
                );

            border-color: #64e4f5;

            box-shadow:
                0 0 15px rgba(39,181,213,0.25);

            color: white !important;
        }


        /* ================================
           TEXT INPUTS
        ================================= */

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {

            background-color: #0d2237 !important;

            color: #ffffff !important;

            border: 1px solid #294b65 !important;

            border-radius: 8px !important;
        }


        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {

            border-color: #28b8d8 !important;

            box-shadow:
                0 0 0 1px #28b8d8 !important;
        }


        /* ================================
           SELECT BOX
        ================================= */

        .stSelectbox > div > div {

            background-color: #0d2237;

            color: white;

            border-radius: 8px;
        }


        /* ================================
           TABS
        ================================= */

        .stTabs [data-baseweb="tab-list"] {

            gap: 8px;

            background: rgba(8, 26, 43, 0.70);

            padding: 6px;

            border-radius: 12px;
        }


        .stTabs [data-baseweb="tab"] {

            border-radius: 8px;

            padding-left: 18px;

            padding-right: 18px;

            color: #9fb9cc;
        }


        .stTabs [aria-selected="true"] {

            background: #0b779f !important;

            color: white !important;
        }


        /* ================================
           EXPANDERS
        ================================= */

        [data-testid="stExpander"] {

            background:
                rgba(9, 29, 47, 0.75);

            border: 1px solid #24445d;

            border-radius: 12px;
        }


        /* ================================
           ALERTS
        ================================= */

        [data-testid="stAlert"] {

            border-radius: 10px;

            background:
                rgba(13, 35, 54, 0.90);
        }


        /* ================================
           DATAFRAMES
        ================================= */

        [data-testid="stDataFrame"] {

            border: 1px solid #294760;

            border-radius: 12px;

            overflow: hidden;
        }


        /* ================================
           DIVIDERS
        ================================= */

        hr {

            border: none;

            height: 1px;

            background: #203d54;

            margin-top: 25px;

            margin-bottom: 25px;
        }


        /* ================================
           SCROLLBAR
        ================================= */

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #06101d;
        }

        ::-webkit-scrollbar-thumb {

            background: #244c68;

            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #327096;
        }


        /* ================================
           HIDE STREAMLIT FOOTER
        ================================= */

        footer {
            visibility: hidden;
        }


        /* ================================
           MOBILE
        ================================= */

        @media (max-width: 768px) {

            .block-container {

                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }

            .metric-card,
            .feature-card {

                padding: 14px;

            }

            .metric-value {

                font-size: 23px;

            }

        }

        </style>
        """,

        unsafe_allow_html=True
    )