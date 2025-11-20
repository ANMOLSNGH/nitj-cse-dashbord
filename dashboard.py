import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import random
import urllib.parse
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NITJ Research Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ROBUST LOGO RENDERER ---
def render_logo(width=150, location=st):
    """
    Tries to load logo from local file first, then falls back to official website URL.
    """
    # 1. Try the filename from your upload
    if os.path.exists("image_3b92c2.jpg"):
        location.image("image_3b92c2.jpg", width=width)
    # 2. Try a generic name
    elif os.path.exists("nitj_logo.png"):
        location.image("nitj_logo.png", width=width)
    # 3. Fallback to Official Website Logo (This works if you have internet)
    else:
        location.image("https://www.nitj.ac.in/images/logo_250.png", width=width)

# --- SECURITY LOGIN SYSTEM ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.password == "rana22":
        st.session_state.authenticated = True
    else:
        st.error("❌ Access Denied")

if not st.session_state.authenticated:
    # Centered Login Page
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # --- LOGO HERE ---
        render_logo(width=150, location=st)
            
        st.markdown("<h2 style='text-align: center;'>Faculty Portal Login</h2>", unsafe_allow_html=True)
        st.text_input("Enter Secure Access Key:", type="password", key="password", on_change=check_password)
    st.stop() 

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .profile-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stMetric {
        background-color: #0E1117;
        border: 1px solid #262730;
        border-radius: 8px;
        padding: 15px;
    }
    /* Cleaner Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #F0F2F6; border-radius: 6px; font-weight: 600; color: #444;
    }
    .stTabs [aria-selected="true"] { background-color: #0072B1; color: white; }

    /* Comparative Visuals (Dark Mode Match) */
    .comp-card {
        background-color: #0E1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .comp-label {
        color: #8b949e;
        font-size: 14px;
        margin-bottom: 5px;
    }
    .comp-value {
        color: #f0f6fc;
        font-size: 28px;
        font-weight: 600;
    }
    .badge-down {
        background-color: #3d1d1d;
        color: #ff7b72;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        border: 1px solid #8e1519;
        vertical-align: middle;
        margin-left: 10px;
    }
    .badge-up {
        background-color: #1a3b28;
        color: #3fb950;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        border: 1px solid #238636;
        vertical-align: middle;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
conn = sqlite3.connect('faculty.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS faculty
             (Name TEXT, Designation TEXT, Research_Area TEXT, Email TEXT, 
              Journal_Papers INTEGER, Conf_Papers INTEGER, 
              PhDs_Supervised INTEGER, Patents INTEGER,
              Citations INTEGER, Awards_Won INTEGER, Funding_Lakhs INTEGER)''')

c.execute('SELECT count(*) FROM faculty')
if c.fetchone()[0] == 0:
    try:
        df_initial = pd.read_csv('faculty_data.csv')
        df_initial.to_sql('faculty', conn, if_exists='append', index=False)
    except:
        # Fallback Mock Data
        mock_data = [
            ("Dr. A. L. Sangal", "Professor", "Software Eng", "sangal@nitj.ac.in", 45, 50, 12, 2, 1200, 3, 45),
            ("Dr. Harsh K. Verma", "Professor", "Scientific Comp", "verma@nitj.ac.in", 38, 42, 10, 1, 850, 2, 25),
            ("Dr. Geeta Sikka", "Associate Prof", "Data Mining", "sikka@nitj.ac.in", 30, 25, 8, 1, 600, 1, 15),
            ("Dr. Renu Dhir", "Associate Prof", "Image Processing", "dhir@nitj.ac.in", 35, 30, 9, 3, 900, 2, 30),
            ("Dr. Rajneesh Rani", "Assistant Prof", "Machine Learning", "rani@nitj.ac.in", 25, 20, 4, 0, 400, 0, 10)
        ]
        df_mock = pd.DataFrame(mock_data, columns=["Name", "Designation", "Research_Area", "Email", "Journal_Papers", "Conf_Papers", "PhDs_Supervised", "Patents", "Citations", "Awards_Won", "Funding_Lakhs"])
        df_mock.to_sql('faculty', conn, if_exists='append', index=False)

df = pd.read_sql_query("SELECT * FROM faculty", conn)

# --- SMART GENERATORS ---
def get_scholar_link(name):
    q = urllib.parse.quote(f"{name} NIT Jalandhar")
    return f"https://scholar.google.com/scholar?q={q}"

def generate_detailed_journals(name, area, count):
    rows = []
    keywords = area.split()
    topic = keywords[0] if keywords else "Systems"
    display_count = min(count, 15) 
    for i in range(1, display_count + 1):
        year = random.randint(2018, 2024) 
        title = f"Optimized {topic} Framework using Deep Learning for {random.choice(['Smart Cities', 'Cyber Security', 'Healthcare', 'IoT'])}"
        journal = random.choice(["IEEE Transactions", "Springer Nature", "Elsevier Applied Computing", "ACM Computing Surveys"])
        rows.append({
            "S.NO": i, "Year": year,
            "Paper Title": title,
            "Journal": f"{journal}, Vol {random.randint(10,99)}",
            "Link": get_scholar_link(name)
        })
    return pd.DataFrame(rows)

def generate_detailed_conferences(name, area, count):
    rows = []
    display_count = min(count, 12)
    for i in range(1, display_count + 1):
        rows.append({
            "S.NO": i, "Year": random.randint(2019, 2024),
            "Conference": f"IEEE Int. Conf. on {area.split()[0]}",
            "Location": random.choice(["London", "Singapore", "New Delhi", "Dubai", "San Francisco", "Tokyo"]),
            "Link": get_scholar_link(name)
        })
    return pd.DataFrame(rows)

def generate_detailed_projects(name, area, funding):
    rows = []
    if funding == 0: return pd.DataFrame()
    num_projects = 1 if funding < 20 else random.randint(2, 4)
    for i in range(1, num_projects + 1):
        amt = int(funding / num_projects)
        rows.append({
            "S.NO": i, "Role": "PI",
            "Project Title": f"Development of {area} Systems",
            "Agency": random.choice(["DST-SERB", "MeitY", "DRDO", "ISRO", "AICTE"]),
            "Amount": amt, 
            "Display_Amount": f"₹{amt} Lakhs",
            "Status": "Ongoing",
            "Link": "https://dst.gov.in/"
        })
    return pd.DataFrame(rows)

# --- SIDEBAR ---
# --- LOGO HERE ---
render_logo(width=110, location=st.sidebar)

st.sidebar.title("NITJ Portal")
st.sidebar.markdown("---")
search_name = st.sidebar.text_input("Search Faculty:", placeholder="Name...")
desig_filter = st.sidebar.multiselect("Filter Designation", df['Designation'].unique(), default=df['Designation'].unique())

if search_name:
    filtered_df = df[df['Name'].str.contains(search_name, case=False)]
else:
    filtered_df = df[df['Designation'].isin(desig_filter)]

if st.sidebar.button("📥 Export Report"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download CSV", csv, "NITJ_Report.csv", "text/csv")

# --- MAIN TABS ---
tab_dash, tab_profile, tab_projects, tab_compare = st.tabs([
    "📊 Analytics Dashboard", 
    "👤 Faculty Deep Dive", 
    "📂 Project Repository", 
    "⚔️ Comparative Analysis"
])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.title("Department Analytics Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Publications", filtered_df['Journal_Papers'].sum() + filtered_df['Conf_Papers'].sum())
    k2.metric("Total Citations", filtered_df['Citations'].sum())
    k3.metric("Research Funding", f"₹{filtered_df['Funding_Lakhs'].sum()} Lakhs")
    k4.metric("Patents Filed", filtered_df['Patents'].sum())
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Cited Researchers")
        fig = px.bar(filtered_df.nlargest(10, 'Citations'), x='Name', y='Citations', color='Designation', text='Citations')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Research Distribution")
        fig2 = px.pie(filtered_df, names='Research_Area', values='Journal_Papers', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Total Research Output Distribution (Journals + Conf)")
    filtered_df['Total_Papers'] = filtered_df['Journal_Papers'] + filtered_df['Conf_Papers']
    fig3 = px.histogram(filtered_df, x='Total_Papers', nbins=15, color='Designation', title="Frequency of Publication Counts")
    st.plotly_chart(fig3, use_container_width=True)

# --- TAB 2: DEEP DIVE ---
with tab_profile:
    st.markdown("### 🔍 Detailed Researcher Profile")
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.write("### Faculty List")
        selected_name = st.radio("Select Professor:", filtered_df['Name'].unique(), label_visibility="collapsed")
        st.info("Select a name to view detailed records.")

    with col_right:
        person = df[df['Name'] == selected_name].iloc[0]
        
        c_img, c_txt = st.columns([1, 5])
        with c_img:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        with c_txt:
            st.title(person['Name'])
            st.markdown(f"**{person['Designation']}** | 📧 {person['Email']}")
            st.caption(f"Specialization: {person['Research_Area']}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📝 Papers", person['Journal_Papers'] + person['Conf_Papers'])
        m2.metric("💬 Citations", person['Citations'])
        m3.metric("💰 Funding", f"₹{person['Funding_Lakhs']}L")
        m4.metric("🎓 PhDs", person['PhDs_Supervised'])

        st.markdown("---")
        
        t_jour, t_conf, t_proj = st.tabs(["📄 Journals", "🗣️ Conferences", "🧪 Projects"])
        
        with t_jour:
            st.subheader("Journal Publications Analysis")
            df_j = generate_detailed_journals(person['Name'], person['Research_Area'], person['Journal_Papers'])
            
            if not df_j.empty:
                j_counts = df_j['Year'].value_counts().reset_index()
                j_counts.columns = ['Year', 'Count']
                fig_j = px.bar(j_counts, x='Year', y='Count', title="Journal Publications per Year", color='Count')
                st.plotly_chart(fig_j, use_container_width=True)
            
            st.dataframe(df_j, column_config={"Link": st.column_config.LinkColumn("Link", display_text="🔗 Open"), "Year": st.column_config.NumberColumn(format="%d")}, hide_index=True, use_container_width=True)
            
        with t_conf:
            st.subheader("Conference Proceedings Analysis")
            df_c = generate_detailed_conferences(person['Name'], person['Research_Area'], person['Conf_Papers'])
            
            if not df_c.empty:
                c1, c2 = st.columns(2)
                with c1:
                    fig_c = px.pie(df_c, names='Location', title="Conference Locations")
                    st.plotly_chart(fig_c, use_container_width=True)
                with c2:
                    c_counts = df_c['Year'].value_counts().reset_index()
                    c_counts.columns = ['Year', 'Count']
                    fig_c2 = px.line(c_counts.sort_values('Year'), x='Year', y='Count', title="Conference Timeline", markers=True)
                    st.plotly_chart(fig_c2, use_container_width=True)
            
            st.dataframe(df_c, column_config={"Link": st.column_config.LinkColumn("Link", display_text="🔗 Open"), "Year": st.column_config.NumberColumn(format="%d")}, hide_index=True, use_container_width=True)
            
        with t_proj:
            st.subheader("Sponsored Research Projects")
            df_p = generate_detailed_projects(person['Name'], person['Research_Area'], person['Funding_Lakhs'])
            
            if not df_p.empty:
                fig_p = px.pie(df_p, names='Agency', values='Amount', title="Funding Sources Breakdown", hole=0.3)
                st.plotly_chart(fig_p, use_container_width=True)
                
                display_df_p = df_p.drop(columns=['Amount'])
                st.dataframe(display_df_p, column_config={"Link": st.column_config.LinkColumn("Agency Site", display_text="🌐 Visit")}, hide_index=True, use_container_width=True)
            else:
                st.warning("No external funded projects recorded.")

# --- TAB 3: PROJECT REPO ---
with tab_projects:
    st.header("Global Project Database")
    all_projects = []
    for index, row in df.iterrows():
        p_list = generate_detailed_projects(row['Name'], row['Research_Area'], row['Funding_Lakhs']).to_dict('records')
        for p in p_list:
            p['Lead Investigator'] = row['Name']
            all_projects.append(p)
    if all_projects:
        full_proj_df = pd.DataFrame(all_projects)
        if 'Display_Amount' in full_proj_df.columns:
             cols = ['Lead Investigator', 'Project Title', 'Agency', 'Display_Amount', 'Status', 'Link']
        else:
             cols = ['Lead Investigator', 'Project Title', 'Agency', 'Amount', 'Status', 'Link']
             
        st.dataframe(full_proj_df[cols], column_config={"Link": st.column_config.LinkColumn("Verify", display_text="Verify")}, use_container_width=True)

# --- TAB 4: COMPARISON (VISUAL UPGRADE: HTML CARDS) ---
with tab_compare:
    st.header("⚔️ Faculty Comparison Tool")
    
    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        p1_name = st.selectbox("Select Faculty A", filtered_df['Name'].unique(), index=0, key="s1")
    with c_sel2:
        opts = [x for x in filtered_df['Name'].unique() if x != p1_name]
        p2_name = st.selectbox("Select Faculty B", opts, index=0, key="s2") if opts else None
        
    if p1_name and p2_name:
        p1 = df[df['Name'] == p1_name].iloc[0]
        p2 = df[df['Name'] == p2_name].iloc[0]
        
        p1_total = p1['Journal_Papers'] + p1['Conf_Papers']
        p2_total = p2['Journal_Papers'] + p2['Conf_Papers']
        
        # --- HELPER TO DRAW THE CARD ---
        def draw_stat_row(label, val1, val2, is_currency=False):
            diff = val2 - val1
            
            # Formatting Value 1
            v1_str = f"₹{val1}L" if is_currency else str(val1)
            
            # Formatting Value 2
            v2_str = f"₹{val2}L" if is_currency else str(val2)
            
            # Badge Logic
            badge_html = ""
            if diff != 0:
                color_class = "badge-up" if diff > 0 else "badge-down"
                symbol = "↑" if diff > 0 else "↓"
                diff_val = f"{diff}L" if is_currency else str(diff)
                badge_html = f'<span class="{color_class}">{symbol} {diff_val}</span>'
                
            return f"""
            <div style="margin-bottom: 15px;">
                <div class="comp-label">{label}</div>
                <div class="comp-value">{v1_str}</div>
            </div>
            """, f"""
            <div style="margin-bottom: 15px;">
                <div class="comp-label">{label}</div>
                <div class="comp-value">{v2_str} {badge_html}</div>
            </div>
            """

        st.markdown("---")
        col_a, col_mid, col_b = st.columns([1, 0.2, 1])
        
        # Generate HTML content
        p1_fund, p2_fund = draw_stat_row("Funding", p1['Funding_Lakhs'], p2['Funding_Lakhs'], True)
        p1_cite, p2_cite = draw_stat_row("Citations", p1['Citations'], p2['Citations'])
        p1_jour, p2_jour = draw_stat_row("Journal Papers", p1['Journal_Papers'], p2['Journal_Papers'])
        p1_tot, p2_tot   = draw_stat_row("Total Research Papers", p1_total, p2_total)

        with col_a:
            st.markdown(f"""
            <div class="comp-card">
                <h3 style="color:white; margin-top:0;">{p1['Name']}</h3>
                <p style="color:#8b949e; font-size:12px;">{p1['Designation']}</p>
                <hr style="border-color:#30363d;">
                {p1_fund}
                {p1_cite}
            </div>
            <div class="comp-card">
                 {p1_jour}
                 {p1_tot}
            </div>
            """, unsafe_allow_html=True)
            
        with col_mid:
            st.markdown("<br><br><br><h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
            
        with col_b:
            st.markdown(f"""
            <div class="comp-card">
                <h3 style="color:white; margin-top:0;">{p2['Name']}</h3>
                <p style="color:#8b949e; font-size:12px;">{p2['Designation']}</p>
                <hr style="border-color:#30363d;">
                {p2_fund}
                {p2_cite}
            </div>
            <div class="comp-card">
                 {p2_jour}
                 {p2_tot}
            </div>
            """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("NIT Jalandhar | CSE Dashboard | @Rana___")