import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.config import APP_NAME, SKILL_CATEGORIES, THEME_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from src.database import init_db, save_session, get_all_sessions, clear_history
from src.vector_store import VectorStore
from src.llm_engine import LLMEngine
from src.resource_validator import validate_url

# Page Config
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(f"""
    <style>
    .main {{
        background-color: #fcfbf9;
    }}
    .stApp {{
        color: {SECONDARY_COLOR};
    }}
    .stButton>button {{
        background-color: {ACCENT_COLOR};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
    }}
    .stButton>button:hover {{
        background-color: {SECONDARY_COLOR};
        color: white;
    }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        border-color: {THEME_COLOR};
    }}
    h1, h2, h3 {{
        color: {ACCENT_COLOR};
        font-family: 'Inter', sans-serif;
    }}
    .sidebar .sidebar-content {{
        background-color: {THEME_COLOR};
    }}
    </style>
    """, unsafe_allow_html=True)

# Initialize Components
@st.cache_resource
def load_components():
    init_db()
    vector_store = VectorStore()
    llm_engine = LLMEngine()
    return vector_store, llm_engine

vector_store, llm_engine = load_components()

# Sidebar
with st.sidebar:
    st.title("User Profile")
    user_name = st.text_input("Designer Name", value="Design Professional")
    st.info(f"Welcome back, {user_name}!")
    
    st.divider()
    st.subheader("System Connectivity")
    if llm_engine.use_groq:
        st.success("✅ Primary Engine: Groq (Connected)")
    elif HF_TOKEN:
        st.warning("⚠️ Using Fallback: Hugging Face")
    else:
        st.error("❌ No AI Engine Connected")
    
    st.divider()
    st.subheader("Session Controls")
    if st.button("Clear Session History"):
        clear_history()
        st.success("History cleared!")
        st.rerun()

# Main Title
st.title(f"🎨 {APP_NAME}")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Skill Gap Analyzer", "📊 My Skill Profile", "💼 JD Gap Matcher"])

# Tab 1: Skill Gap Analyzer
with tab1:
    st.header("Analyze Your Design Challenges")
    col1, col2 = st.columns(2)
    
    with col1:
        task_desc = st.text_area("Describe your design task", placeholder="e.g., Creating a high-end residential lighting plan...")
    with col2:
        struggle_desc = st.text_area("What are you struggling with?", placeholder="e.g., Calculating beam angles and avoiding glare on art pieces...")
    
    if st.button("Analyze Skill Gap"):
        if task_desc and struggle_desc:
            with st.spinner("Analyzing skill gaps using AI knowledge base..."):
                # RAG retrieval
                context = vector_store.search(f"{task_desc} {struggle_desc}")
                
                # LLM Analysis
                result = llm_engine.analyze_gap(task_desc, struggle_desc, context)
                
                if result:
                    # Save to DB
                    save_session(
                        task_desc, 
                        result['skill_gap'], 
                        result['domain'], 
                        result['severity'], 
                        result['confidence'], 
                        result['resource_link']
                    )
                    
                    st.success("Analysis Complete!")
                    
                    # Display Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Detected Gap", result['skill_gap'])
                    m2.metric("Domain", result['domain'])
                    m3.metric("Confidence", f"{result['confidence']*100:.1f}%")
                    
                    # Details
                    with st.expander("📖 Tutorial & Explanation", expanded=True):
                        st.write(result['explanation'])
                    
                    with st.expander("🛠️ Recommended Workflow"):
                        st.code(result['workflow_example'], language='markdown')
                    
                    # Resource Link
                    is_valid = validate_url(result['resource_link'])
                    if is_valid:
                        st.link_button("View Official Resource", result['resource_link'])
                    else:
                        st.warning("Resource link validation failed. Please search for the official documentation manually.")
                else:
                    st.error("Failed to analyze skill gap. Please try again.")
        else:
            st.warning("Please fill in both fields.")

# Tab 2: My Skill Profile
with tab2:
    st.header("Your Professional Growth")
    
    sessions = get_all_sessions()
    if sessions:
        df = pd.DataFrame(sessions, columns=['ID', 'Timestamp', 'Task', 'Skill Gap', 'Domain', 'Severity', 'Confidence', 'Link'])
        
        # Calculate Skill Levels for Radar Chart
        # Base levels = 1, increment by 0.5 per session in that domain, max 5
        skill_data = {cat: 1.0 for cat in SKILL_CATEGORIES}
        domain_counts = df['Domain'].value_counts().to_dict()
        for domain, count in domain_counts.items():
            if domain in skill_data:
                skill_data[domain] = min(5.0, 1.0 + (count * 0.8))
        
        # Radar Chart
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(skill_data.values()),
            theta=list(skill_data.keys()),
            fill='toself',
            marker=dict(color=ACCENT_COLOR),
            name='Skill Level'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5])
            ),
            showlegend=False,
            title="Competency Overview"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Session History
        st.subheader("Session History")
        st.dataframe(df.drop(columns=['ID']), use_container_width=True)
    else:
        st.info("No session history found. Start analyzing gaps to build your profile!")

# Tab 3: JD Gap Matcher
with tab3:
    st.header("Match Your Skills to Job Descriptions")
    
    jd_input = st.text_area("Paste Job Description", height=200, placeholder="Paste the text from an interior design job posting here...")
    user_skills_input = st.text_area("List Your Current Skills", placeholder="e.g., AutoCAD, Revit, Mood Boarding, Vendor Management...")
    
    if st.button("Calculate Match"):
        if jd_input and user_skills_input:
            with st.spinner("Comparing skills against job requirements..."):
                matches = llm_engine.match_jd(jd_input, user_skills_input)
                
                if matches:
                    st.subheader("Prioritized Learning Path")
                    
                    severity_map = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
                    
                    for match in matches:
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.write(f"**{match['skill']}**")
                            sev = match.get('severity', 'Medium')
                            progress_val = severity_map.get(sev, 0.5)
                            st.progress(progress_val, text=f"Severity: {sev}")
                        with col_b:
                            st.info(match['recommendation'])
                else:
                    st.error("Failed to parse JD matching results.")
        else:
            st.warning("Please provide both the JD and your current skills.")

# Footer
st.markdown("---")
st.caption("© 2026 Interior Design Skill Gap Analyzer | Powered by Mistral-7B & FAISS")
