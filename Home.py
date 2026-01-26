import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json

# 1. SETUP HALAMAN (Wajib Paling Atas)
st.set_page_config(
    page_title="Sains Data Crisis Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 MASTER DESIGN SYSTEM (CORPORATE STYLE)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONT PREMIUM (Source Sans 3 - Standar Adobe/Professional) */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800&display=swap');

    /* RESET & BASE STYLE */
    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
        color: #111827; /* Gray-900: Hampir hitam, sangat tegas */
    }

    /* BACKGROUND BERSIH (Tanpa Motif Mainan) */
    .stApp {
        background-color: #f3f4f6; /* Gray-100: Abu-abu sangat muda, elegan */
    }

    /* SIDEBAR (Warna Kampus/Solid) */
    [data-testid="stSidebar"] {
        background-color: #0f172a; /* Slate-900: Deep Navy */
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #f8fafc !important;
    }

    /* KARTU PROFESIONAL (Shadow Lebih Halus & Border Tipis) */
    .pro-card {
        background: #ffffff;
        padding: 24px;
        border-radius: 8px; /* Sudut tidak terlalu bulat (lebih kotak/serius) */
        border: 1px solid #e5e7eb; /* Border abu tipis */
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); /* Shadow tipis standar korporat */
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .pro-card:hover {
        border-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* TYPOGRAPHY YANG LEBIH TEGAS */
    h1 {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 800; 
        letter-spacing: -0.5px;
        color: #111827; /* Hitam tegas */
    }
    h2, h3 {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 700;
        color: #1f2937; /* Gray-800 */
    }
    p, div {
        color: #374151; /* Gray-700: Teks isi lebih gelap biar terbaca jelas */
        line-height: 1.6;
    }
    
    /* TOMBOL PRIMARY (Solid Blue - No Gradient) */
    .stButton > button {
        background-color: #1d4ed8; /* Biru BUMN/Korporat */
        color: white;
        border: none;
        border-radius: 6px; /* Sudut tajam dikit */
        font-weight: 600;
        padding: 0.6rem 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        width: 100%;
        font-family: 'Source Sans 3', sans-serif;
