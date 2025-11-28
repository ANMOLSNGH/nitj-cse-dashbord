# dashboard.py  (FULL FILE)
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import urllib.parse
import os

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="NITJ Research Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# LOGO RENDERER
# ======================
def render_logo(width=150, location=st):
    if os.path.exists("image_3b92c2.jpg"):
        location.image("image_3b92c2.jpg", width=width)
    elif os.path.exists("nitj_logo.png"):
        location.image("nitj_logo.png", width=width)
    else:
        location.image("https://www.nitj.ac.in/images/logo_250.png", width=width)

# ======================
# AUTHENTICATION (simple)
# ======================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.password == "rana22":
        st.session_state.authenticated = True
    else:
        st.error("❌ Access Denied")

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        render_logo(width=150, location=st)
        st.markdown("<h2 style='text-align: center;'>Faculty Portal Login</h2>", unsafe_allow_html=True)
        st.text_input("Enter Secure Access Key:", type="password", key="password", on_change=check_password)
    st.stop()

# ======================
# MINIMAL CSS
# ======================
st.markdown("""
<style>
    .profile-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border:1px solid #e0e0e0; margin-bottom:18px;}
    .comp-card { background-color: #0E1117; border:1px solid #30363d; border-radius:8px; padding:18px; margin-bottom:12px; }
    .comp-label { color:#8b949e; font-size:14px; margin-bottom:5px; }
    .comp-value { color:#f0f6fc; font-size:26px; font-weight:600; }
    .badge-down { background-color:#3d1d1d; color:#ff7b72; padding:2px 8px; border-radius:12px; font-size:12px; border:1px solid #8e1519; margin-left:10px; }
    .badge-up { background-color:#1a3b28; color:#3fb950; padding:2px 8px; border-radius:12px; font-size:12px; border:1px solid #238636; margin-left:10px; }
    a { color: #1a73e8; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ======================
# FILE NAMES (adjust here if you renamed files)
# ======================
MAIN_XL = "final data.xlsx"
IDS_XL_CANDIDATES = [
    "nit j....xlsx", "nit j...xlsx", "nit j.. (1).xlsx",
    "nit j..xlsx", "nit j.xlsx", "nit j.. (1).xlsx", "nit j.. (1).xls"
]

# ======================
# LOAD MAIN EXCEL
# ======================
if not os.path.exists(MAIN_XL):
    st.error(f"Missing file: {MAIN_XL}. Place final data.xlsx in the same folder as this script and re-run.")
    st.stop()

df_main = pd.read_excel(MAIN_XL)
# normalize column names to strings
df_main.columns = df_main.columns.astype(str)
# sanity: strip names
if "Name" in df_main.columns:
    df_main["Name"] = df_main["Name"].astype(str).str.strip()
else:
    st.error("final data.xlsx must contain a 'Name' column in the header row.")
    st.stop()

# ======================
# FIND & LOAD IDS FILE (only Research_ID is used)
# ======================
ids_path = None
for candidate in IDS_XL_CANDIDATES:
    if os.path.exists(candidate):
        ids_path = candidate
        break

if ids_path:
    df_ids = pd.read_excel(ids_path)
    df_ids.columns = df_ids.columns.astype(str)
    if "Name" in df_ids.columns:
        df_ids["Name"] = df_ids["Name"].astype(str).str.strip()
    # find research id-like column (name begins with 'research id' ignoring case)
    rid_col = next((c for c in df_ids.columns if c.strip().lower().startswith("research id")), None)
    # also accept 'profile link' present but we will ignore other columns per your instruction
    if rid_col:
        df_ids_small = df_ids[["Name", rid_col]].rename(columns={rid_col: "Research_ID"})
    else:
        # nothing found -> create empty Research_ID column
        df_ids_small = pd.DataFrame({"Name": df_ids["Name"], "Research_ID": pd.NA})
else:
    df_ids_small = pd.DataFrame(columns=["Name", "Research_ID"])

# ======================
# MERGE MAIN + RESEARCH_ID (only)
# ======================
df_full = df_main.merge(df_ids_small, on="Name", how="left")

# drop any Unnamed: columns
to_drop = [c for c in df_full.columns if c.lower().startswith("unnamed")]
if to_drop:
    df_full = df_full.drop(columns=to_drop)

# Save to SQLite (no funding columns kept)
conn = sqlite3.connect("faculty_genuine.db")
df_full.to_sql("faculty", conn, index=False, if_exists="replace")
df = df_full.copy()

# ======================
# HELPER FUNCTIONS FOR LINKS & FALLBACKS
# ======================
def get_scholar_link(name):
    return f"https://scholar.google.com/scholar?q={urllib.parse.quote(name + ' NIT Jalandhar')}"

def mk_clickable(link_text):
    """Return markdown hyperlink or raw text fallback."""
    if pd.isna(link_text) or str(link_text).strip() == "":
        return "-"
    s = str(link_text).strip()
    if s.lower().startswith("http"):
        # safe markdown link
        return f"[Open]({s})"
    # if text contains 'http' somewhere, still attempt to show it
    if "http" in s.lower():
        return f"[Open]({s})"
    return s

def mk_researchid_link(reid):
    if pd.isna(reid) or str(reid).strip() == "":
        return "-"
    s = str(reid).strip()
    # if it's a URL, open directly
    if s.lower().startswith("http"):
        return f"[Open]({s})"
    # else search google for that id + NIT Jalandhar
    q = urllib.parse.quote(s + " NIT Jalandhar")
    return f"[Search]({ 'https://www.google.com/search?q=' + q })"

# ======================
# SIDEBAR
# ======================
render_logo(width=110, location=st.sidebar)
st.sidebar.title("NITJ Portal")
st.sidebar.markdown("---")
search_name = st.sidebar.text_input("Search Faculty:", placeholder="Name...")
desig_choices = df["Designation"].dropna().unique().tolist() if "Designation" in df.columns else []
desig_filter = st.sidebar.multiselect("Filter Designation", desig_choices, default=desig_choices)

filtered_df = df.copy()
if search_name:
    filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
else:
    if desig_choices:
        filtered_df = filtered_df[filtered_df['Designation'].isin(desig_filter)]

if st.sidebar.button("📥 Export Report"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download CSV", csv, "NITJ_Report.csv", "text/csv")

# ======================
# TABS
# ======================
tab_dash, tab_profile, tab_projects, tab_compare = st.tabs([
    "📊 Analytics Dashboard",
    "👤 Faculty Deep Dive",
    "📂 Project Repository",
    "⚔️ Comparative Analysis"
])

# ======================
# TAB 1: DASHBOARD
# ======================
with tab_dash:
    st.title("Department Analytics Overview")
    # three metrics (funding removed)
    k1, k2, k3 = st.columns(3)
    total_pubs = int(filtered_df.get('Journal_Papers', 0).fillna(0).sum() + filtered_df.get('Conf_Papers', 0).fillna(0).sum())
    k1.metric("Total Publications", total_pubs)
    total_citations = int(filtered_df.get('Citations', 0).fillna(0).sum())
    k2.metric("Total Citations", total_citations)
    k3.metric("Patents Filed", int(filtered_df.get('Patents', 0).fillna(0).sum()))
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Cited Researchers")
        if 'Citations' in filtered_df.columns:
            top = filtered_df.nlargest(10, 'Citations').fillna(0)
            fig = px.bar(top, x='Name', y='Citations', color='Designation' if 'Designation' in top.columns else None, text='Citations')
            fig.update_layout(xaxis_tickangle=-45, height=480)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No citation data available.")
    with c2:
        st.subheader("Research Distribution")
        if 'Research_Area' in filtered_df.columns and 'Journal_Papers' in filtered_df.columns:
            fig2 = px.pie(filtered_df, names='Research_Area', values=filtered_df['Journal_Papers'].fillna(0), hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Not enough publication breakdown to render distribution.")

    st.subheader("Total Research Output Distribution (Journals + Conf)")
    filtered_df['Total_Papers'] = filtered_df.get('Journal_Papers', 0).fillna(0) + filtered_df.get('Conf_Papers', 0).fillna(0)
    fig3 = px.histogram(filtered_df, x='Total_Papers', nbins=15, color='Designation' if 'Designation' in filtered_df.columns else None)
    st.plotly_chart(fig3, use_container_width=True)

# ======================
# TAB 2: DEEP DIVE
# ======================
with tab_profile:
    st.markdown("### 🔍 Detailed Researcher Profile")
    col_left, col_right = st.columns([1, 3])
    with col_left:
        sorted_names = sorted(filtered_df['Name'].unique())
        selected_name = st.radio("Select Professor:", sorted_names, label_visibility="collapsed")
        st.info("Select a name to view detailed records.")
    with col_right:
        if selected_name:
            # pick row (safe)
            person = df[df['Name'] == selected_name].iloc[0]

            # header + contact + specialization
            st.title(person['Name'])
            email = person.get('Email', '-')
            # profile link might be in different column names depending on source
            profile_link_candidates = [c for c in person.index if "profile" in c.lower() and str(person.get(c)).strip() != ""]
            profile_raw = person.get(profile_link_candidates[0]) if profile_link_candidates else None
            st.markdown(f"**{person.get('Designation','')}** | 📧 {email}")
            st.caption(f"Specialization: {person.get('Research_Area','-')}")

            # Research ID: clickable
            st.markdown(f"**Research ID:** {mk_researchid_link(person.get('Research_ID', None))}", unsafe_allow_html=True)

            # Metrics (no funding)
            m1, m2, m3 = st.columns(3)
            m1.metric("📝 Papers", int((person.get('Journal_Papers', 0) or 0) + (person.get('Conf_Papers', 0) or 0)))
            m2.metric("💬 Citations", int(person.get('Citations', 0) or 0))
            m3.metric("🎓 PhDs", int(person.get('PhDs_Supervised', 0) or 0))

            st.markdown("---")

            # Tabs for publications and projects
            t_jour, t_conf, t_proj = st.tabs(["📄 Journals", "🗣️ Conferences", "🧪 Projects"])

            # Journals tab: show total bar + pie + summary row clickable
            with t_jour:
                st.subheader("Journal Publications Analysis")
                jp = int(person.get('Journal_Papers', 0) or 0)
                cp = int(person.get('Conf_Papers', 0) or 0)
                colv1, colv2 = st.columns(2)
                with colv1:
                    fig_jbar = px.bar(x=["Journal Papers"], y=[jp], text=[jp], labels={"x": "", "y": "Count"}, title="Total Journal Papers")
                    fig_jbar.update_traces(textposition="outside")
                    st.plotly_chart(fig_jbar, use_container_width=True)
                with colv2:
                    fig_pie = px.pie(names=["Journals", "Conferences"], values=[jp, cp], title="Publications Breakdown")
                    st.plotly_chart(fig_pie, use_container_width=True)
                # summary table (single row because no per-year data)
                if jp > 0:
                    df_j = pd.DataFrame([{
                        "Year": "-",
                        "Paper Title": f"{jp} total journal papers",
                        "Journal": "See profile",
                        "Profile": mk_clickable(profile_raw) if profile_raw else mk_clickable(get_scholar_link(person['Name']))
                    }])
                    st.dataframe(df_j, use_container_width=True)
                else:
                    st.info("No journal entries recorded.")

            # Conferences tab
            with t_conf:
                st.subheader("Conference Publications Analysis")
                cp = int(person.get('Conf_Papers', 0) or 0)
                colv1, colv2 = st.columns(2)
                with colv1:
                    fig_cbar = px.bar(x=["Conference Papers"], y=[cp], text=[cp], labels={"x": "", "y": "Count"}, title="Total Conference Papers")
                    fig_cbar.update_traces(textposition="outside")
                    st.plotly_chart(fig_cbar, use_container_width=True)
                with colv2:
                    fig_line = px.line(x=[1], y=[cp], markers=True, title="Conference Timeline (No year data)")
                    st.plotly_chart(fig_line, use_container_width=True)
                if cp > 0:
                    df_c = pd.DataFrame([{
                        "Year": "-",
                        "Conference": f"{cp} total conference papers",
                        "Paper Title": "Summary",
                        "Profile": mk_clickable(profile_raw) if profile_raw else mk_clickable(get_scholar_link(person['Name']))
                    }])
                    st.dataframe(df_c, use_container_width=True)
                else:
                    st.info("No conference entries recorded.")

            # Projects tab: disabled (no funding data / no project details expected)
            with t_proj:
                st.warning("Projects data not provided. This section is disabled.")

# ======================
# TAB 3: PROJECT REPO
# ======================
with tab_projects:
    st.header("Global Project Database")
    st.info("Projects data not provided in uploaded Excel.")

# ======================
# TAB 4: COMPARISON
# ======================
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

        p1_total = (p1.get('Journal_Papers', 0) or 0) + (p1.get('Conf_Papers', 0) or 0)
        p2_total = (p2.get('Journal_Papers', 0) or 0) + (p2.get('Conf_Papers', 0) or 0)

        def row(label, v1, v2):
            diff = (v2 or 0) - (v1 or 0)
            badge = ""
            if diff > 0:
                badge = f'<span class="badge-up">↑ {int(diff)}</span>'
            elif diff < 0:
                badge = f'<span class="badge-down">↓ {int(abs(diff))}</span>'
            return (
                f"<div class='comp-label'>{label}</div><div class='comp-value'>{int(v1 or 0)}</div>",
                f"<div class='comp-label'>{label}</div><div class='comp-value'>{int(v2 or 0)} {badge}</div>"
            )

        f1_cit, f2_cit = row("Citations", p1.get('Citations', 0), p2.get('Citations', 0))
        f1_jour, f2_jour = row("Journal Papers", p1.get('Journal_Papers', 0), p2.get('Journal_Papers', 0))
        f1_tot, f2_tot = row("Total Research Papers", p1_total, p2_total)

        col_a, col_mid, col_b = st.columns([1, 0.2, 1])
        with col_a:
            st.markdown(f"""
                <div class="comp-card">
                    <h3 style='color:white'>{p1['Name']}</h3>
                    <p style='color:#8b949e'>{p1.get('Designation','')}</p>
                    <hr style="border-color:#30363d;">
                    {f1_cit}
                </div>
                <div class="comp-card">
                    {f1_jour}<br>{f1_tot}
                </div>
            """, unsafe_allow_html=True)
        with col_mid:
            st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
                <div class="comp-card">
                    <h3 style='color:white'>{p2['Name']}</h3>
                    <p style='color:#8b949e'>{p2.get('Designation','')}</p>
                    <hr style="border-color:#30363d;">
                    {f2_cit}
                </div>
                <div class="comp-card">
                    {f2_jour}<br>{f2_tot}
                </div>
            """, unsafe_allow_html=True)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("NIT Jalandhar | CSE Dashboard | @Rana___")
