from sqlalchemy import create_engine
import streamlit as st

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(DATABASE_URL)