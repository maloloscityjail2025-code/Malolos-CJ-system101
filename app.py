import base64
from datetime import datetime

# 1. Ideklara muna ang variable na ito bago mo gamitin:
current_date = datetime.now().strftime("%B %d, %Y")

# 2. Pagkatapos ay saka mo i-display sa st.markdown:
st.markdown(f"PDL DETAINED AS OF **{current_date}**")
import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Malolos City Jail Virtual Dashboard", layout="wide")

EXCEL_FILE = "pdl_database.xlsx"
SETTINGS_FILE = "jail_settings.xlsx"

# ---------- SETTINGS PERSISTENCE ----------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return pd.read_excel(SETTINGS_FILE).iloc[0].to_dict()
    return {
        "Alert Status": "WHITE ALERT (Normal)",
        "Duty Male": 5,
        "Duty Female": 3,
        "Duty Escort": 2,
        "Duty Admin": 2,
        "Duty Nurse": 1,
        "Jail Capacity": 19
    }

def update_settings_file():
    save_settings(
        st.session_state.widget_alert,
        st.session_state.widget_male,
        st.session_state.widget_female,
        st.session_state.widget_escort,
        st.session_state.widget_admin,
        st.session_state.widget_nurse,
        st.session_state.widget_capacity
    )

def save_settings(alert, male, female, escort, admin, nurse, capacity):
    df_set = pd.DataFrame([{
        "Alert Status": alert,
        "Duty Male": male,
        "Duty Female": female,
        "Duty Escort": escort,
        "Duty Admin": admin,
        "Duty Nurse": nurse,
        "Jail Capacity": capacity
    }])
    df_set.to_excel(SETTINGS_FILE, index=False)

saved_set = load_settings()

# ---------- THEME ----------
BG, PANEL, EDGE = "#07142E", "#0D2147", "#1B4F9C"
CYAN, GOLD, RED, TEXT = "#1FD6E6", "#F5C518", "#E53935", "#E8EEF9"
PALETTE = [RED, CYAN, GOLD, "#7E57C2", "#FB8C00", "#43A047", "#1E88E5", "#EC407A", "#8D6E63"]

CSS = """
<style>
.stApp { background: __BG__; color: __TEXT__; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1rem 1.2rem 0.5rem 1.2rem; max-width: 100%; }
section[data-testid="stSidebar"] { background: #050E22; border-right: 1px solid __EDGE__; }
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p { color: __TEXT__ !important; }

.hdr { display:flex; justify-content:space-between; align-items:center;
       background: __PANEL__; border:1px solid __EDGE__; padding:10px 18px; margin-bottom:10px; }
.hdr-title { color: __GOLD__; font-size:1.7rem; font-weight:800; letter-spacing:.04em; }
.hdr-sub { color: __CYAN__; font-size:.85rem; }
.hdr-date { text-align:right; color: __TEXT__; font-size:.75rem; }
.hdr-date b { color: __GOLD__; font-size:1rem; }

.kpi { background: __PANEL__; border:1px solid __EDGE__; padding:8px 12px; margin-bottom:8px; }
.kpi .lbl { color: __GOLD__; font-weight:700; font-size:.85rem; }
.kpi .val { color: __TEXT__; font-size:2.3rem; font-weight:800; line-height:1.15; }
.kpi .sub { color: __TEXT__; font-size:.75rem; opacity:.85; }
.kpi.alert { background: __RED__; border-color: __RED__; }
.kpi.alert .lbl { color:#fff; }
.kpi.ok .val { color: __CYAN__; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: __PANEL__; border:1px solid __EDGE__ !important; border-radius:3px; }
.panel-title { color: __GOLD__; font-weight:700; font-size:.95rem;
               border-bottom:1px solid __EDGE__; padding-bottom:4px; margin-bottom:2px; }
</style>
"""
for key, val in {"__BG__": BG, "__PANEL__": PANEL, "__EDGE__": EDGE, "__CYAN__": CYAN,
                 "__GOLD__": GOLD, "__RED__": RED, "__TEXT__": TEXT}.items():
    CSS = CSS.replace(key, val)
st.markdown(CSS, unsafe_allow_html=True)

# ---------- DATA CONSTANTS ----------
COLUMNS = ['PDL ID', 'Pangalan', 'Edad', 'Branch', 'Uri ng Kaso', 'Civil Status', 'Status', 'Room / Cell']
CRIMES = ['Drugs', 'Crime Vs Property', 'Crime Vs Person', 'Non-Index Crime', 'Others']
CIVIL = ['Single', 'Married', 'Broken']
STATUSES = ['Ongoing Trial', 'Serving Sentence', 'PDL Due for in Patient Rehabilitation']
ROOMS = ['Dorm 1', 'Dorm 2', 'Dorm 3', 'ISOLATION']
BRACKETS = ['Under 18', 'Age 18-24', 'Age 25-30', 'Age 31-35', 'Age 36-41',
            'Age 42-47', 'Age 48-53', 'Age 54-59', 'Age 60-69', 'Above 70']

def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    
    df_default = pd.DataFrame({
        'PDL ID': [101, 102, 103, 104, 105],
        'Pangalan': ['John Jaybee Macapagal', 'Joel Sarmiento', 'Michael Angelo Calayag',
                     'MacLhouie Honra', 'Mark Anthony Catacutan'],
        'Edad': [22, 28, 42, 33, 62],
        'Branch': ['RTC Branch 10', 'RTC Branch 14', 'RTC Branch 10', 'MTC Branch 1', 'RTC Branch 81'],
        'Uri ng Kaso': ['Drugs', 'Crime Vs Property', 'Crime Vs Person', 'Non-Index Crime', 'Others'],
        'Civil Status': ['Single', 'Married', 'Single', 'Broken', 'Single'],
        'Status': ['Serving Sentence', 'Ongoing Trial', 'Serving Sentence', 'Ongoing Trial', 'Serving Sentence'],
        'Room / Cell': ['Dorm 1', 'Dorm 2', 'Dorm 3', 'ISOLATION', 'Dorm 1'],
    })
    df_default.to_excel(EXCEL_FILE, index=False)
    return df_default

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

def get_age_bracket(age):
    if age < 18:
        return 'Under 18'
    for lo, hi, label in [(18, 24, 'Age 18-24'), (25, 30, 'Age 25-30'), (31, 35, 'Age 31-35'),
                          (36, 41, 'Age 36-41'), (42, 47, 'Age 42-47'), (48, 53, 'Age 48-53'),
                          (54, 59, 'Age 54-59'), (60, 69, 'Age 60-69')]:
        if lo <= age <= hi:
            return label
    return 'Above 70'

if 'pdl_data' not in st.session_state:
    st.session_state.pdl_data = load_data()

data = st.session_state.pdl_data

def idx_of(items, value):
    str_items = [str(x).strip().lower() for x in items]
    target = str(value).strip().lower()
    return str_items.index(target) if target in str_items else 0

# ---------- SIDEBAR LOGO ----------
LOGO_NAME = "logo2.png" 
if os.path.exists(LOGO_NAME):
    st.sidebar.image(LOGO_NAME, use_container_width=True)
    st.sidebar.markdown("---")
else:
    st.sidebar.warning(f"⚠️ Walang nakitang {LOGO_NAME} sa folder.")

# ---------- SIDEBAR (AUTOMATIC SAVING) ----------
st.sidebar.header("⚙️ Jail Management")

jail_capacity = st.sidebar.number_input(
    "Itakda ang Jail Capacity", 
    min_value=1, 
    value=int(saved_set.get("Jail Capacity", 19)),
    key="widget_capacity",
    on_change=update_settings_file
)

st.sidebar.markdown("---")
st.sidebar.header("🚨 Operational Status & Duty")

alert_options = ["WHITE ALERT (Normal)", "BLUE ALERT (Heightened)", "RED ALERT (Full Alert)"]
curr_alert = saved_set.get("Alert Status", "WHITE ALERT (Normal)")
alert_idx = alert_options.index(curr_alert) if curr_alert in alert_options else 0

ALERT_STATUS = st.sidebar.selectbox(
    "Alert Status", 
    alert_options, 
    index=alert_idx,
    key="widget_alert",
    on_change=update_settings_file
)

duty_male = st.sidebar.number_input(
    "Duty Personnel (Male)", 
    min_value=0, 
    value=int(saved_set.get("Duty Male", 5)),
    key="widget_male",
    on_change=update_settings_file
)

duty_female = st.sidebar.number_input(
    "Duty Personnel (Female)", 
    min_value=0, 
    value=int(saved_set.get("Duty Female", 3)),
    key="widget_female",
    on_change=update_settings_file
)

duty_escort = st.sidebar.number_input(
    "Duty Escort", 
    min_value=0, 
    value=int(saved_set.get("Duty Escort", 2)),
    key="widget_escort",
    on_change=update_settings_file
)

duty_admin = st.sidebar.number_input(
    "Duty Admin", 
    min_value=0, 
    value=int(saved_set.get("Duty Admin", 2)),
    key="widget_admin",
    on_change=update_settings_file
)

duty_nurse = st.sidebar.number_input(
    "Duty Nurse", 
    min_value=0, 
    value=int(saved_set.get("Duty Nurse", 1)),
    key="widget_nurse",
    on_change=update_settings_file
)

total_duty = duty_male + duty_female + duty_escort + duty_admin + duty_nurse

# Alert Status Color Mapping
alert_bg = "#43A047" 
if "BLUE" in ALERT_STATUS:
    alert_bg = "#1E88E5" 
elif "RED" in ALERT_STATUS:
    alert_bg = "#E53935" 

st.sidebar.markdown("---")
st.sidebar.header("➕ Magdagdag ng PDL")

# Form para sa pagdadagdag kasama ang Duplicate Validation
with st.sidebar.form("pdl_form"):
    new_id = int(data['PDL ID'].max() + 1) if not data.empty else 101
    new_name = st.text_input("Pangalan ng PDL")
    new_age = st.number_input("Edad", min_value=18, max_value=100, value=30)
    new_branch = st.text_input("Branch (Manual Input)", value="RTC Branch ")
    new_crime = st.selectbox("Uri ng Kaso", CRIMES)
    new_civil = st.selectbox("Civil Status", CIVIL)
    new_status = st.selectbox("Status", STATUSES)
    new_room = st.selectbox("Room / Cell", ROOMS)
    submit_button = st.form_submit_button("I-save ang PDL")

    if submit_button:
        if not new_name.strip():
            st.sidebar.error("⚠️ Mangyaring ilagay ang pangalan ng PDL.")
        else:
            existing_names = data['Pangalan'].str.strip().str.lower() if not data.empty else pd.Series()
            input_name_cleaned = new_name.strip().lower()
            
            if input_name_cleaned in existing_names.values:
                st.sidebar.error(f"❌ Ang pangalang '{new_name}' ay nakarehistro na sa sistema!")
            else:
                new_row = pd.DataFrame([[new_id, new_name, new_age, new_branch, new_crime,
                                         new_civil, new_status, new_room]], columns=COLUMNS)
                st.session_state.pdl_data = pd.concat([data, new_row], ignore_index=True)
                save_data(st.session_state.pdl_data)
                st.sidebar.success(f"Tagumpay na naidagdag si {new_name}!")
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("✏️ I-edit / 🗑️ Delete PDL")
if not data.empty:
    action_type = st.sidebar.radio("Piliin ang Gawin", ["I-edit", "Mag-delete"])
    labels = {int(r['PDL ID']): f"{int(r['PDL ID'])} - {r['Pangalan']}" for _, r in data.iterrows()}
    selected_id = st.sidebar.selectbox("Piliin ang PDL", list(labels.keys()),
                                       format_func=lambda i: labels[i])

    if action_type == "I-edit":
        cur = data[data['PDL ID'] == selected_id].iloc[0]
        with st.sidebar.form("edit_form"):
            u_name = st.text_input("Bagong Pangalan", value=str(cur['Pangalan']), key=f"n{selected_id}")
            u_age = st.number_input("Bagong Edad", min_value=18, max_value=100,
                                    value=int(cur['Edad']), key=f"a{selected_id}")
            u_branch = st.text_input("Bagong Branch", value=str(cur['Branch']), key=f"b{selected_id}")
            u_crime = st.selectbox("Bagong Uri ng Kaso", CRIMES,
                                    index=idx_of(CRIMES, cur['Uri ng Kaso']), key=f"c{selected_id}")
            u_civil = st.selectbox("Bagong Civil Status", CIVIL,
                                    index=idx_of(CIVIL, cur['Civil Status']), key=f"cs{selected_id}")
            u_status = st.selectbox("Bagong Status", STATUSES,
                                     index=idx_of(STATUSES, cur['Status']), key=f"s{selected_id}")
            u_room = st.selectbox("Bagong Room / Cell", ROOMS,
                                   index=idx_of(ROOMS, cur['Room / Cell']), key=f"r{selected_id}")
            if st.form_submit_button("I-update"):
                mask = st.session_state.pdl_data['PDL ID'] == selected_id
                st.session_state.pdl_data.loc[mask, COLUMNS[1:]] = [
                    u_name, u_age, u_branch, u_crime, u_civil, u_status, u_room]
                save_data(st.session_state.pdl_data)
                st.rerun()
    else:
        if st.sidebar.button("Kumpirmahin ang Pag-delete"):
            st.session_state.pdl_data = data[data['PDL ID'] != selected_id].reset_index(drop=True)
            save_data(st.session_state.pdl_data)
            st.rerun()

# ---------- COMPUTE ----------
df = st.session_state.pdl_data.copy()
if not df.empty:
    df['Age Group'] = df['Edad'].apply(get_age_bracket)

population = len(df)
congestion = (population / jail_capacity) * 100
over = population - jail_capacity

def count_by(series, order=None):
    vc = series.value_counts()
    if order:
        vc = vc.reindex(order, fill_value=0)
    vc = vc[vc > 0]
    return vc.rename_axis("label").reset_index(name="count")

def style_fig(fig, height):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=TEXT, size=11), height=height)
    return fig

def pie_panel(col, title, counts):
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="panel-title">{title}</div>', unsafe_allow_html=True)
            if counts.empty:
                st.caption("Walang data.")
                return
            fig = px.pie(counts, names="label", values="count", hole=0.55,
                         color_discrete_sequence=PALETTE)
            fig.update_traces(textinfo="percent", textfont_size=11,
                              marker=dict(line=dict(color=PANEL, width=2)))
            style_fig(fig, 300)
            fig.update_layout(margin=dict(t=8, b=70, l=8, r=8),
                              legend=dict(orientation="h", y=-0.02, yanchor="top",
                                          font=dict(size=10)))
            fig.add_annotation(text=f"<b>{int(counts['count'].sum())}</b>", showarrow=False,
                               x=0.5, y=0.5, font=dict(size=22, color=GOLD))
            st.plotly_chart(fig, use_container_width=True)

def bar_panel(col, title, counts):
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="panel-title">{title}</div>', unsafe_allow_html=True)
            if counts.empty:
                st.caption("Walang data.")
                return
            fig = px.bar(counts, x="count", y="label", orientation='h', text="count",
                         color_discrete_sequence=[CYAN])
            fig.update_traces(textposition="outside", cliponaxis=False)
            style_fig(fig, 300)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=25),
                              xaxis_title=None, yaxis_title=None,
                              yaxis=dict(autorange="reversed"))
            fig.update_xaxes(showgrid=True, gridcolor=EDGE)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)

def highlight_duplicates(s):
    is_dup = s.duplicated(keep=False)
    return ['background-color: #E53935; color: white;' if v else '' for v in is_dup]

def kpi(label, value, sub="", cls=""):
    st.markdown(f'<div class="kpi {cls}"><div class="lbl">{label}</div>'
                f'<div class="val">{value}</div><div class="sub">{sub or "&nbsp;"}</div></div>',
                unsafe_allow_html=True)

# ---------- HEADER WITH 3 LOGOS ----------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo1_b64 = get_base64_image("logo1.jpg") 
logo2_b64 = get_base64_image("logo2.png") 
logo3_b64 = get_base64_image("logo3.png") 

logos_html = '<div style="display: flex; align-items: center; gap: 10px; margin-right: 15px;">'
if logo1_b64:
    logos_html += f'<img src="data:image/png;base64,{logo1_b64}" style="height: 50px; border-radius: 4px;">'
if logo2_b64:
    logos_html += f'<img src="data:image/png;base64,{logo2_b64}" style="height: 50px; border-radius: 4px;">'
if logo3_b64:
    logos_html += f'<img src="data:image/png;base64,{logo3_b64}" style="height: 50px; border-radius: 4px;">'
logos_html += '</div>'

st.markdown(
    f'<div class="hdr" style="display: flex; align-items: center;">'
    f'{logos_html}'
    f'<div style="flex-grow: 1;">'
    f'<div class="hdr-title">MALOLOS CITY JAIL VIRTUAL DASHBOARD</div>'
    f'<div class="hdr-sub">Congestion Rate and PDL Management System ni Calayag</div>'
    f'</div>'
    f'<div style="text-align: right; margin-right: 15px;">'
    f'<div style="background: {alert_bg}; color: #ffffff; padding: 4px 12px; border-radius: 5px; font-weight: 800; font-size: 0.85rem; display: inline-block;">'
    f'{ALERT_STATUS}'
    f'</div>'
    f'</div>'
    f'<div class="hdr-date">PDL DETAINED AS OF<br><b>{datetime.now():%B %d, %Y}</b></div>'
    f'</div>',
    unsafe_allow_html=True
)

# ---------- ROW 1: HORIZONTAL KPI CARDS SA ITAAS ----------
st.markdown("### 📊 Operational Overview")
kpi_cols = st.columns(5) 

with kpi_cols[0]:
    kpi("Jail Population", population)
with kpi_cols[1]:
    kpi("Jail Capacity", jail_capacity)
with kpi_cols[2]:
    kpi("Congestion Rate", f"{congestion:.2f}%",
        f"{over} labis" if over > 0 else "Normal", "alert" if over > 0 else "ok")
with kpi_cols[3]:
    kpi("On-Duty Personnel", f"{total_duty}", f"👨 M:{duty_male} | 👩 F:{duty_female} | 🛡️ Esc:{duty_escort} | 📋 Adm:{duty_admin} | 💉 Nur:{duty_nurse}")
with kpi_cols[4]:
    kpi("Alert Status", ALERT_STATUS.split(" ")[0], "Current Level", "alert" if "RED" in ALERT_STATUS else "ok")

st.markdown("---")

# ---------- ROW 2: CHARTS SA IBABA NG KPIS ----------
st.markdown("### 📈 PDL Demographics & Case Analytics")
c1, c2, c3, c4, c5 = st.columns(5)

if df.empty:
    empty = pd.DataFrame(columns=["label", "count"])
    bar_panel(c1, "Branch", empty)
    for col, title in zip([c2, c3, c4, c5], ["Crime Category", "Civil Status", "Age Bracket", "Case Status"]):
        pie_panel(col, title, empty)
else:
    bar_panel(c1, "Branch Distribution", count_by(df['Branch']))
    pie_panel(c2, "Crime Category", count_by(df['Uri ng Kaso']))
    pie_panel(c3, "Civil Status", count_by(df['Civil Status']))
    pie_panel(c4, "Age Bracket", count_by(df['Age Group'], BRACKETS))
    pie_panel(c5, "PDL Case Status", count_by(df['Status']))

# ---------- ROW 3: ROOM DISTRIBUTION + MASTERLIST ----------
r1, r2 = st.columns([1.6, 3.4])

with r1:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Room Distribution</div>', unsafe_allow_html=True)
        if df.empty:
            st.caption("Walang data.")
        else:
            rooms = count_by(df['Room / Cell'], ROOMS)
            fig_room = px.bar(rooms, x="label", y="count", text="count",
                              color_discrete_sequence=[RED])
            fig_room.update_traces(textposition="outside", cliponaxis=False)
            style_fig(fig_room, 250)
            fig_room.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                                    xaxis_title=None, yaxis_title=None)
            fig_room.update_yaxes(gridcolor=EDGE)
            st.plotly_chart(fig_room, use_container_width=True)

with r2:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Masterlist ng mga PDL (Awtomatikong nakapula ang Duplicate)</div>', unsafe_allow_html=True)
        display_df = df.drop(columns=['Age Group']) if 'Age Group' in df.columns else df
        
        if not display_df.empty:
            styled_df = display_df.style.apply(highlight_duplicates, subset=['Pangalan'])
            st.dataframe(styled_df, use_container_width=True, height=250, hide_index=False)
        else:
            st.dataframe(display_df, use_container_width=True, height=250, hide_index=True)
