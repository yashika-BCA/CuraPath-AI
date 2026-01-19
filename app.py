"""
CuraPath AI - Comprehensive Career Guidance Platform
Main Application File
"""
import streamlit as st
import random
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_calendar import calendar
from utils.auth import register_user, authenticate_user, get_user_data, save_user_data
from utils.storage import (
    save_profile, load_profile, save_progress, load_progress,
    save_journal_entry, load_journal, save_task, load_tasks, update_task,
    save_alarm, load_alarms, update_alarm, delete_alarm,
    update_journal_entry, delete_journal_entry,
    save_event, load_events, delete_event,
)
from utils.career_engine import (
    get_career_suggestions,
    get_career_paths,
    get_career_milestones,
    build_prioritized_roadmap,
    compute_completion_date,
)
from utils.ui_components import apply_glassmorphism_css, render_header, render_progress_bar, render_career_card
from utils.gsheets import append_row as gsheets_append_row

# Page configuration
st.set_page_config(
    page_title="CuraPath AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False
if "current_section" not in st.session_state:
    st.session_state.current_section = "oracle"
if "selected_career" not in st.session_state:
    st.session_state.selected_career = None
if "selected_path" not in st.session_state:
    st.session_state.selected_path = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "mood" not in st.session_state:
    st.session_state.mood = None
if "burnout_detected" not in st.session_state:
    st.session_state.burnout_detected = False

# Apply custom CSS (after theme is available)
apply_glassmorphism_css(theme=st.session_state.theme)

# ==================== PHASE 1: AUTHENTICATION ====================
def show_auth_page():
    """Display login/signup page"""
    st.title("🧠 AI Career Coach")
    st.markdown("### Your professional, personalized career planning platform")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        username = st.text_input("Username or Email", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            ok, uname_key = authenticate_user(username, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.username = uname_key
                user_data = get_user_data(uname_key)
                st.session_state.onboarding_complete = user_data.get("onboarding_complete", False)
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.markdown("### Create Your Account")
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        
        if st.button("Sign Up", use_container_width=True):
            ok, msg = register_user(new_username, new_password, name=name, email=email)
            if ok:
                # Optional Google Sheets logging
                try:
                    gsheets_append_row("Signup", [datetime.now().isoformat(), new_username, name, email])
                except Exception:
                    pass
                st.success("Account created successfully! Please login.")
            else:
                st.error(msg)

# ==================== PHASE 1: ONBOARDING ====================
def show_onboarding():
    """Multi-step onboarding questionnaire"""
    st.title("👋 Welcome!")
    st.markdown("Let’s build your career profile — this powers every recommendation inside **AI Career Coach**.")
    
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 1
    
    steps = ["Personal Info", "Education", "Skills", "Interests", "Goals & Pace"]
    current_step = st.session_state.onboarding_step
    
    # Progress indicator
    progress = current_step / len(steps)
    st.progress(progress)
    st.caption(f"Step {current_step} of {len(steps)}: {steps[current_step-1]}")
    
    if current_step == 1:
        st.markdown("### Step 1: Personal Information")
        name = st.text_input("What's your name?")
        age = st.number_input("How old are you?", min_value=13, max_value=100, value=20)
        
        if st.button("Next", use_container_width=True):
            if name:
                st.session_state.onboarding_data = {"name": name, "age": age}
                st.session_state.onboarding_step = 2
                st.rerun()
    
    elif current_step == 2:
        st.markdown("### Step 2: Education")
        school = st.text_input("School / College Name")
        education_level = st.selectbox("Education Level", ["High School", "College", "Other"], key="onb_edu_level")

        detail = None
        if education_level == "High School":
            detail = st.selectbox("Grade", ["9", "10", "11", "12"], key="onb_grade")
        elif education_level == "College":
            detail = st.selectbox(
                "Degree",
                ["B.Tech", "BCA", "BSc", "BCom", "BA", "BE", "BBA", "M.Tech", "MCA", "MSc", "MBA", "Other"],
                key="onb_degree",
            )
        else:
            detail = st.text_input("Education Detail", placeholder="e.g., Diploma, Bootcamp, Self-taught", key="onb_other_edu")
        
        if st.button("Next", use_container_width=True):
            st.session_state.onboarding_data["school"] = school
            st.session_state.onboarding_data["education_level"] = education_level
            st.session_state.onboarding_data["education_detail"] = detail
            st.session_state.onboarding_step = 3
            st.rerun()
    
    elif current_step == 3:
        st.markdown("### Step 3: Skills")
        st.caption("Select what you already know — this directly updates career suggestions + roadmaps.")

        st.markdown("**Technical Skills**")
        tech_skills = st.multiselect(
            "Pick technical skills",
            [
                "Frontend (HTML/CSS/JS)",
                "React",
                "Backend (Node/Django/Flask)",
                "Databases (SQL/NoSQL)",
                "DSA",
                "System Design",
                "Python",
                "Java",
                "Cloud (AWS/Azure/GCP)",
                "DevOps (CI/CD)",
                "AI/ML",
                "Cybersecurity",
            ],
            key="onb_tech",
            label_visibility="collapsed",
        )

        st.markdown("**Soft Skills**")
        soft_skills = st.multiselect(
            "Pick soft skills",
            ["Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", "Public Speaking", "Creativity"],
            key="onb_soft",
            label_visibility="collapsed",
        )
        
        if st.button("Next", use_container_width=True):
            st.session_state.onboarding_data["skills_technical"] = tech_skills
            st.session_state.onboarding_data["skills_soft"] = soft_skills
            st.session_state.onboarding_step = 4
            st.rerun()
    
    elif current_step == 4:
        st.markdown("### Step 4: Hobbies & Interests")
        st.markdown("**Creative Hobbies**")
        creative_hobbies = st.multiselect(
            "Pick creative hobbies",
            ["Design", "Digital Art", "Content Creation", "Writing", "Music", "Photography", "Video Editing", "Gaming", "Public Speaking"],
            key="onb_hobbies",
            label_visibility="collapsed",
        )
        hobbies_other = st.text_area("Anything else?", placeholder="Optional: add more hobbies/interests…", key="onb_hobbies_other")
        
        if st.button("Next", use_container_width=True):
            st.session_state.onboarding_data["hobbies_creative"] = creative_hobbies
            st.session_state.onboarding_data["hobbies_other"] = hobbies_other
            st.session_state.onboarding_step = 5
            st.rerun()
    
    elif current_step == 5:
        st.markdown("### Step 5: Career Goals & Learning Pace")
        goals = st.text_area("Career Goals", placeholder="e.g., Get an internship, become a full-stack dev, crack placements, build a startup…")

        colp1, colp2 = st.columns(2)
        with colp1:
            daily_hours = st.slider("Daily Study Hours", min_value=1, max_value=8, value=2, step=1)
        with colp2:
            pace = st.select_slider("Learning Pace", options=["Slow", "Normal", "Fast"], value="Normal")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.onboarding_step = 4
                st.rerun()
        with col2:
            if st.button("Complete Onboarding", use_container_width=True):
                if goals:
                    st.session_state.onboarding_data["goals"] = goals
                    st.session_state.onboarding_data["daily_hours"] = daily_hours
                    st.session_state.onboarding_data["learning_pace"] = pace
                    
                    # Save profile
                    profile = st.session_state.onboarding_data.copy()
                    save_profile(st.session_state.username, profile)
                    save_user_data(st.session_state.username, {"onboarding_complete": True, "profile": profile})
                    
                    st.session_state.onboarding_complete = True
                    st.session_state.onboarding_step = 1
                    st.rerun()

# ==================== PHASE 2: CAREER ORACLE ====================
def show_career_oracle():
    """Career suggestion hub"""
    st.title("🔮 Career Oracle")
    st.markdown("### Discover Your Personalized Career Paths")
    
    profile = load_profile(st.session_state.username)
    if not profile:
        st.error("Profile not found. Please complete onboarding.")
        return
    
    suggestions = get_career_suggestions(profile)
    
    st.markdown("---")
    st.markdown("### 🎯 Your Personalized Career Suggestions")
    
    for idx, career_data in enumerate(suggestions):
        selected = render_career_card(career_data, idx)
        if selected:
            st.session_state.selected_career = selected
            st.session_state.current_section = "roadmap"
            st.rerun()
        st.markdown("---")

# ==================== PHASE 2: STRATEGIC ROADMAP ====================
def show_roadmap():
    """Strategic roadmap with 4 paths"""
    if not st.session_state.selected_career:
        st.warning("Please select a career path first.")
        if st.button("Back to Career Oracle"):
            st.session_state.current_section = "oracle"
            st.rerun()
        return
    
    st.title(f"🗺️ Strategic Roadmap: {st.session_state.selected_career}")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Oracle"):
            st.session_state.current_section = "oracle"
            st.session_state.selected_career = None
            st.rerun()
    
    profile = load_profile(st.session_state.username) or {}
    target_focus = st.selectbox("Target Focus (Logic Switch)", ["MNC", "Startup"], index=0, help="MNC prioritizes DSA/System Design. Startup prioritizes stacks & projects.")

    # Smart timeline (completion date)
    daily_hours = int(profile.get("daily_hours", 2))
    learning_pace = profile.get("learning_pace", "Normal")
    roadmap_struct = build_prioritized_roadmap(st.session_state.selected_career, target_focus)
    completion_dt = compute_completion_date(roadmap_struct, daily_hours=daily_hours, learning_pace=learning_pace)
    st.caption(f"📅 Estimated Completion Date: **{completion_dt.strftime('%b %d, %Y')}** (based on {daily_hours}h/day, pace: {learning_pace})")

    st.markdown("---")
    st.markdown("### 🧭 Roadmap Structure (Industry Standard Levels)")
    for level, topics in roadmap_struct.items():
        with st.expander(level, expanded=False):
            for t in topics:
                st.markdown(f"- {t['topic']}")

    st.markdown("---")
    paths = get_career_paths(st.session_state.selected_career)
    path_names = ["Startup", "MNC", "Product-based", "FAANG"]
    
    st.markdown("### Choose Your Path")
    
    cols = st.columns(4)
    for idx, path_name in enumerate(path_names):
        with cols[idx]:
            if path_name in paths:
                path_data = paths[path_name]
                st.markdown(f"""
                <div class="path-card">
                    <h3 style="color: white;">{path_name}</h3>
                    <p style="color: rgba(255,255,255,0.7);">⏱️ {path_data['time_estimate']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select {path_name}", key=f"path_{path_name}", use_container_width=True):
                    st.session_state.selected_path = path_name
                    st.session_state.current_section = "progress"
                    st.rerun()
    
    st.markdown("---")
    
    # Show detailed resources for selected path (if any)
    if st.session_state.selected_path and st.session_state.selected_path in paths:
        path_data = paths[st.session_state.selected_path]
        st.markdown(f"### 📚 Resources for {st.session_state.selected_path} Path")

        tabs = st.tabs(["🆓 Free Sites", "🏆 Certifications", "💰 Paid", "📺 YouTube Lists"])
        with tabs[0]:
            for resource in path_data["resources"]["free"]:
                st.markdown(f"- {resource}")
        with tabs[1]:
            for resource in path_data["resources"]["certification"]:
                st.markdown(f"- {resource}")
        with tabs[2]:
            for resource in path_data["resources"]["paid"]:
                st.markdown(f"- {resource}")
            st.markdown("---")
            st.markdown("**Non-certification (projects/tasks)**")
            for resource in path_data["resources"]["non_certification"]:
                st.markdown(f"- {resource}")
        with tabs[3]:
            st.info("YouTube curation placeholder (AI-ready). Add channels/playlists per your target.")
            st.markdown("- Roadmap walkthrough playlist (placeholder)")
            st.markdown("- Interview prep playlist (placeholder)")

        st.markdown("### 🎯 Required Skills (Vertical Cards)")
        for skill in path_data["skills"]:
            st.markdown(f"<div class='milestone-card'><strong style='color:white;'>{skill}</strong></div>", unsafe_allow_html=True)

# ==================== PHASE 2: INTERACTIVE PROGRESS TRACKER ====================
def show_progress_tracker():
    """IBM-style progress tracker"""
    if not st.session_state.selected_career or not st.session_state.selected_path:
        st.warning("Please select a career and path first.")
        if st.button("Back to Roadmap"):
            st.session_state.current_section = "roadmap"
            st.rerun()
        return
    
    st.title(f"📊 Progress Tracker: {st.session_state.selected_career} - {st.session_state.selected_path}")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Roadmap"):
            st.session_state.current_section = "roadmap"
            st.rerun()
    
    # Load or initialize progress
    progress_key = f"{st.session_state.selected_career}_{st.session_state.selected_path}"
    progress_data = load_progress(st.session_state.username, progress_key)
    
    if not progress_data:
        milestones = get_career_milestones(st.session_state.selected_career)
        progress_data = {
            "basics": {m: False for m in milestones.get("Basics", [])},
            "intermediate": {m: False for m in milestones.get("Intermediate", [])},
            "advanced": {m: False for m in milestones.get("Advanced", [])}
        }
    else:
        milestones = {
            "Basics": list(progress_data.get("basics", {}).keys()),
            "Intermediate": list(progress_data.get("intermediate", {}).keys()),
            "Advanced": list(progress_data.get("advanced", {}).keys())
        }
    
    # Calculate progress percentage
    all_milestones = []
    completed = 0
    for level in ["basics", "intermediate", "advanced"]:
        level_data = progress_data.get(level, {})
        all_milestones.extend(level_data.items())
        completed += sum(1 for v in level_data.values() if v)
    
    total = len(all_milestones)
    progress_percentage = (completed / total * 100) if total > 0 else 0
    
    # Render progress bar
    render_progress_bar(progress_percentage)
    
    st.markdown(f"### Overall Progress: {progress_percentage:.1f}% ({completed}/{total} completed)")
    st.progress(progress_percentage / 100)

    # Success celebration
    if total > 0 and completed == total:
        st.balloons()
        st.markdown("### 🏅 Congratulations — you completed the full roadmap!")
        try:
            st.image("assets/career_badge.svg", use_container_width=True)
        except Exception:
            st.info("Career Badge: assets/career_badge.svg (image load placeholder)")
    
    # Display milestones by level
    levels = ["Basics", "Intermediate", "Advanced"]
    level_keys = ["basics", "intermediate", "advanced"]
    
    for level, level_key in zip(levels, level_keys):
        st.markdown(f"### 🎯 {level} Level")
        level_milestones = progress_data.get(level_key, {})
        
        for milestone, completed_status in level_milestones.items():
            checkbox_key = f"{level_key}_{milestone}"
            new_status = st.checkbox(
                milestone,
                value=completed_status,
                key=checkbox_key
            )
            
            if new_status != completed_status:
                progress_data[level_key][milestone] = new_status
                save_progress(st.session_state.username, progress_key, progress_data)
                st.rerun()

# ==================== PLACEMENT READINESS ====================
def show_placement_readiness():
    """Placement Readiness hub (AI-ready placeholders)."""
    st.title("🎯 Placement Readiness")
    st.caption("AI-ready review hub for LinkedIn, GitHub, and Resume — personalized using your profile.")

    profile = load_profile(st.session_state.username) or {}

    top = st.container()
    with top:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Quick Snapshot")
        cols = st.columns(3)
        cols[0].metric("Daily Hours", str(profile.get("daily_hours", 2)))
        cols[1].metric("Learning Pace", str(profile.get("learning_pace", "Normal")))
        cols[2].metric("Target Career", str(st.session_state.selected_career or "Not selected"))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ✅ What you want reviewed")
    linkedin = st.text_input("LinkedIn Profile URL", placeholder="https://www.linkedin.com/in/yourname")
    github = st.text_input("GitHub Profile / Repo URL", placeholder="https://github.com/yourname")
    resume_text = st.text_area("Resume (paste text) / Key sections", height=200, placeholder="Paste resume content or sections here...")

    st.markdown("---")
    st.markdown("### 🤖 AI Guidance (Placeholders)")
    st.info("Gemini integration will generate detailed feedback here (LinkedIn headline/about, GitHub repo quality, ATS resume structure).")

    if st.button("Generate Feedback (AI Placeholder)", use_container_width=True):
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### LinkedIn Feedback (placeholder)")
        st.write("- Optimize headline to include role + niche + proof (projects/impact).")
        st.write("- Strengthen About section: problem → skills → proof → goals.")
        st.markdown("#### GitHub Feedback (placeholder)")
        st.write("- Pin 3–5 best repos; add crisp READMEs with screenshots + setup + architecture.")
        st.write("- Add CI + tests + issues; show consistent commits.")
        st.markdown("#### Resume Feedback (placeholder)")
        st.write("- Use impact bullets: Action + Tech + Metric.")
        st.write("- Keep 1 page; projects first if fresher; add keywords for ATS.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧩 Skills you should highlight (vertical cards)")
    highlight_skills = (profile.get("skills_technical", []) + profile.get("skills_soft", []))[:10]
    if not highlight_skills:
        st.caption("Add skills in Account Settings to see recommendations here.")
    for s in highlight_skills:
        st.markdown(f"<div class='milestone-card'><strong style='color:white;'>{s}</strong></div>", unsafe_allow_html=True)

# ==================== PHASE 3: MIND-CARE SUITE ====================
def show_mindcare():
    """Mind-Care Suite: Vent Box, Empathetic AI, Success Stories, Mood Tracker"""
    st.title("💚 Mind-Care Suite")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Vent Box", "🤖 Empathy Chat", "🌟 Success Stories", "😊 Mood Tracker"])
    
    with tab1:
        st.markdown("### Vent Box - Your Safe Space")
        st.caption("Write down your thoughts, feelings, or anything on your mind...")
        
        journal_entry = st.text_area("What's on your mind?", height=200, key="vent_box")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Entry", use_container_width=True):
                if journal_entry:
                    # Check for burnout/self-doubt keywords
                    burnout_keywords = ["burnout", "tired", "exhausted", "overwhelmed", "can't", "give up"]
                    doubt_keywords = ["doubt", "not good enough", "failure", "impossible", "can't do"]
                    
                    entry_lower = journal_entry.lower()
                    if any(keyword in entry_lower for keyword in burnout_keywords):
                        st.session_state.burnout_detected = True
                    if any(keyword in entry_lower for keyword in doubt_keywords):
                        st.session_state.burnout_detected = True
                    
                    save_journal_entry(st.session_state.username, {
                        "entry": journal_entry,
                        "type": "vent"
                    })
                    # Optional Google Sheets logging
                    try:
                        gsheets_append_row("Journal", [datetime.now().isoformat(), st.session_state.username, "vent", journal_entry[:500]])
                    except Exception:
                        pass
                    st.success("Entry saved! 💚")
                    st.rerun()
        
        with col2:
            if st.button("Past Reflections", use_container_width=True):
                st.session_state.show_reflections = True

        # Past Reflections dashboard (Edit/Delete)
        if st.session_state.get("show_reflections", False):
            st.markdown("---")
            st.markdown("### 🗂️ Past Reflections")
            entries = [e for e in load_journal(st.session_state.username) if e.get("type") == "vent"]
            if not entries:
                st.info("No reflections yet. Write one above.")
            for entry in reversed(entries[-20:]):
                entry_id = entry.get("id")
                with st.container():
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    ts = entry.get("timestamp", "")[:19].replace("T", " ")
                    st.markdown(f"**{ts}**")
                    st.write(entry.get("entry", ""))
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button("✏️ Edit", key=f"edit_j_{entry_id}"):
                            st.session_state.editing_journal_id = entry_id
                            st.session_state.editing_journal_text = entry.get("entry", "")
                            st.rerun()
                    with c2:
                        if st.button("🗑️ Delete", key=f"del_j_{entry_id}"):
                            delete_journal_entry(st.session_state.username, entry_id)
                            st.success("Deleted.")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # Edit dialog-ish area
            if st.session_state.get("editing_journal_id"):
                st.markdown("#### Edit Reflection")
                edited = st.text_area(
                    "Update your entry",
                    value=st.session_state.get("editing_journal_text", ""),
                    height=150,
                    key="editing_journal_text_area",
                )
                colx1, colx2 = st.columns(2)
                with colx1:
                    if st.button("Save Edit", use_container_width=True):
                        update_journal_entry(st.session_state.username, st.session_state.editing_journal_id, {"entry": edited})
                        st.session_state.editing_journal_id = None
                        st.session_state.editing_journal_text = ""
                        st.success("Updated.")
                        st.rerun()
                with colx2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.editing_journal_id = None
                        st.session_state.editing_journal_text = ""
                        st.rerun()
    
    with tab2:
        st.markdown("### Empathy Chat (Persistent)")
        st.caption("This chat will become Gemini-powered. For now it uses profile-aware templates.")

        profile = load_profile(st.session_state.username) or {}
        if "mindcare_chat" not in st.session_state:
            st.session_state.mindcare_chat = [
                {
                    "role": "assistant",
                    "content": f"Hey {profile.get('name','there')} — I’m here. What’s on your mind today?",
                }
            ]

        if st.session_state.burnout_detected:
            st.warning("⚠️ Burnout/self-doubt signals detected in your reflections. Let’s slow down and reset.")

        # Scrollable chat window (bubbles are styled via CSS)
        st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
        for m in st.session_state.mindcare_chat[-20:]:
            if m["role"] == "user":
                st.markdown(f"<div class='chat-bubble user-bubble'>{m['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble ai-bubble'>{m['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        user_message = st.text_input("Message", key="mindcare_input", placeholder="Type here...")
        if st.button("Send", use_container_width=True) and user_message:
            st.session_state.mindcare_chat.append({"role": "user", "content": user_message})

            # Profile-aware motivational story placeholder
            career = st.session_state.selected_career or "your chosen career"
            daily_hours = profile.get("daily_hours", 2)
            pace = profile.get("learning_pace", "Normal")
            assistant_msg = (
                f"I hear you. Since you’re aiming for **{career}**, let’s focus on one small win today.\n\n"
                f"Mini-plan: **{daily_hours}h/day** at **{pace}** pace. Do 1 focused block, then stop — consistency beats intensity.\n\n"
                f"Story: A student like you felt stuck, but they shipped one small project weekly. In 8–12 weeks, their confidence (and clarity) exploded."
            )
            st.session_state.mindcare_chat.append({"role": "assistant", "content": assistant_msg})
            st.rerun()
    
    with tab3:
        st.markdown("### 🌟 Success Stories")
        st.caption("Real stories from people who achieved their career goals")
        
        success_stories = [
            {
                "name": "Alex",
                "career": "Web Developer",
                "path": "Startup",
                "story": "Started with zero coding knowledge at 22. Spent 8 months learning through free resources, built 5 projects, and landed a job at a startup. Now a senior developer!"
            },
            {
                "name": "Sam",
                "career": "Data Scientist",
                "path": "MNC",
                "story": "Transitioned from marketing to data science at 28. Completed online courses, solved 200+ Kaggle problems, and got hired by a Fortune 500 company in 18 months."
            },
            {
                "name": "Jordan",
                "career": "Software Engineer",
                "path": "FAANG",
                "story": "Worked through 500+ LeetCode problems, built scalable systems, contributed to open source. After 2 years of dedicated effort, got an offer from Google!"
            }
        ]
        
        for story in success_stories:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: white;">{story['name']} - {story['career']} ({story['path']})</h4>
                <p style="color: rgba(255,255,255,0.8);">{story['story']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 😊 Mood Tracker")
        st.caption("Track your mood and emotional well-being")
        
        mood_options = ["😊 Great", "🙂 Good", "😐 Okay", "😔 Low", "😢 Struggling"]
        selected_mood = st.radio("How are you feeling today?", mood_options, key="mood_select")
        
        if st.button("Save Mood", use_container_width=True):
            mood_data = {
                "mood": selected_mood,
                "date": datetime.now().isoformat()
            }
            save_journal_entry(st.session_state.username, {
                "entry": f"Mood: {selected_mood}",
                "type": "mood",
                "mood_data": mood_data
            })
            st.session_state.mood = selected_mood
            st.success("Mood saved! 💚")
            
            # Show mood-based encouragement
            if "Struggling" in selected_mood or "Low" in selected_mood:
                st.info("💚 Remember: It's okay to have difficult days. You're doing your best, and that's enough.")

# ==================== PHASE 3: LIFE-TRACKER ====================
def show_lifetracker():
    """Life-Tracker: Alarms, Math Challenges, Task Checklist, Calendar"""
    st.title("⏰ Life-Tracker")
    
    tab1, tab2, tab3 = st.tabs(["🔔 Alarms", "✅ Task Checklist", "📅 Calendar"])
    
    with tab1:
        st.markdown("### Set Study Alarms & Reminders")
        
        alarm_name = st.text_input("Alarm Name", placeholder="e.g., Study Python")
        alarm_date = st.date_input("Date")

        # AM/PM time picker (Streamlit's time_input is 24h-only)
        col_t1, col_t2, col_t3 = st.columns([1, 1, 1])
        with col_t1:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=8)
        with col_t2:
            minute = st.selectbox("Minute", [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55], index=6)
        with col_t3:
            ampm = st.selectbox("AM/PM", ["AM", "PM"], index=0)

        hour_24 = hour_12 % 12
        if ampm == "PM":
            hour_24 += 12
        alarm_time_str = f"{hour_24:02d}:{minute:02d}:00"
        
        if st.button("Set Alarm", use_container_width=True):
            if alarm_name:
                alarm_data = {
                    "name": alarm_name,
                    "time": alarm_time_str,
                    "date": str(alarm_date),
                    "type": "study"
                }
                save_alarm(st.session_state.username, alarm_data)
                st.success(f"Alarm set for {alarm_date} at {alarm_time_str} 🔔")
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Active Alarms")
        alarms = load_alarms(st.session_state.username)
        active_alarms = [a for a in alarms if a.get("active", True)]

        # "Strict firing" in Streamlit can only happen while the app page is open.
        # We approximate it by auto-refreshing and triggering when current time >= alarm time.
        if active_alarms:
            st_autorefresh(interval=30_000, key="alarm_autorefresh")  # 30s
        
        if active_alarms:
            for alarm in active_alarms[-5:]:  # Show last 5
                # Trigger check
                try:
                    alarm_dt = datetime.fromisoformat(f"{alarm.get('date')}T{alarm.get('time')}")
                except Exception:
                    alarm_dt = None
                now = datetime.now()
                is_due = bool(alarm_dt and now >= alarm_dt)

                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    due_tag = " 🔥 DUE" if is_due else ""
                    st.markdown(f"**{alarm.get('name', 'Alarm')}** - {alarm.get('date')} at {alarm.get('time')}{due_tag}")
                with col2:
                    if st.button("Dismiss", key=f"dismiss_{alarm.get('id')}"):
                        # Math challenge to dismiss
                        st.session_state[f"math_challenge_{alarm.get('id')}"] = True
                        st.rerun()
                with col3:
                    if st.button("Delete", key=f"delete_{alarm.get('id')}"):
                        delete_alarm(st.session_state.username, alarm.get('id'))
                        st.success("Alarm deleted!")
                        st.rerun()

                # Auto-open dismiss challenge when due
                if is_due and not st.session_state.get(f"math_challenge_{alarm.get('id')}", False):
                    st.session_state[f"math_challenge_{alarm.get('id')}"] = True
                
                # Math challenge (sum and difference)
                if st.session_state.get(f"math_challenge_{alarm.get('id')}", False):
                    if f"math_num1_{alarm.get('id')}" not in st.session_state:
                        st.session_state[f"math_num1_{alarm.get('id')}"] = random.randint(10, 99)
                        st.session_state[f"math_num2_{alarm.get('id')}"] = random.randint(10, 99)
                        num1 = st.session_state[f"math_num1_{alarm.get('id')}"]
                        num2 = st.session_state[f"math_num2_{alarm.get('id')}"]
                        st.session_state[f"math_sum_{alarm.get('id')}"] = num1 + num2
                        st.session_state[f"math_diff_{alarm.get('id')}"] = abs(num1 - num2)
                        st.session_state[f"math_type_{alarm.get('id')}"] = random.choice(["sum", "diff"])
                    
                    num1 = st.session_state[f"math_num1_{alarm.get('id')}"]
                    num2 = st.session_state[f"math_num2_{alarm.get('id')}"]
                    math_type = st.session_state[f"math_type_{alarm.get('id')}"]
                    
                    if math_type == "sum":
                        question = f"Solve: {num1} + {num2} = ?"
                        correct_answer = st.session_state[f"math_sum_{alarm.get('id')}"]
                    else:
                        question = f"Solve: {max(num1, num2)} - {min(num1, num2)} = ?"
                        correct_answer = st.session_state[f"math_diff_{alarm.get('id')}"]
                    
                    answer = st.number_input(
                        question,
                        key=f"math_input_{alarm.get('id')}",
                        min_value=0
                    )
                    if st.button("Submit", key=f"submit_{alarm.get('id')}"):
                        if answer == correct_answer:
                            st.success("Correct! Alarm dismissed. ✅")
                            update_alarm(st.session_state.username, alarm.get('id'), {"active": False})
                            st.session_state[f"math_challenge_{alarm.get('id')}"] = False
                            # Clear math challenge state
                            for key in list(st.session_state.keys()):
                                if f"math_{alarm.get('id')}" in key:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error("Incorrect. Try again!")
        else:
            st.info("No active alarms. Set one to stay on track! 🎯")
    
    with tab2:
        st.markdown("### Daily Task Checklist")
        
        new_task = st.text_input("Add New Task", placeholder="e.g., Complete Python basics module")
        if st.button("Add Task", use_container_width=True):
            if new_task:
                save_task(st.session_state.username, {"task": new_task})
                st.success("Task added! ✅")
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Your Tasks")
        tasks = load_tasks(st.session_state.username)
        active_tasks = [t for t in tasks if not t.get("completed", False)]
        
        if active_tasks:
            for task in active_tasks:
                task_id = task.get("id")
                completed = st.checkbox(
                    task.get("task", ""),
                    value=False,
                    key=f"task_{task_id}"
                )
                if completed:
                    update_task(st.session_state.username, task_id, {"completed": True})
                    st.rerun()
        else:
            st.info("No active tasks. Great job! 🎉")
        
        completed_tasks = [t for t in tasks if t.get("completed", False)]
        if completed_tasks:
            st.markdown("---")
            st.markdown("### Completed Tasks")
            for task in completed_tasks[-5:]:
                st.markdown(f"✅ ~~{task.get('task', '')}~~")
    
    with tab3:
        st.markdown("### 📅 Interactive Calendar")
        st.caption("Click a date to add an event (saved locally). Google Sheets sync comes next.")

        events = load_events(st.session_state.username)
        cal_events = []
        for e in events:
            cal_events.append(
                {
                    "title": e.get("title", "Event"),
                    "start": f"{e.get('date')}T{e.get('time','09:00:00')}",
                    "end": f"{e.get('date')}T{e.get('time','09:30:00')}",
                }
            )

        calendar_state = calendar(
            events=cal_events,
            options={
                "initialView": "dayGridMonth",
                "height": 560,
            },
            key="cp_calendar",
        )

        clicked_date = None
        if isinstance(calendar_state, dict):
            if calendar_state.get("dateClick"):
                clicked_date = calendar_state["dateClick"].get("date")

        if clicked_date:
            st.session_state.calendar_clicked_date = clicked_date[:10]

        if st.session_state.get("calendar_clicked_date"):
            with st.container():
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown(f"### Add Event — {st.session_state.calendar_clicked_date}")
                title = st.text_input("Event Title", key="evt_title")
                time_str = st.text_input("Time (HH:MM:SS)", value="09:00:00", key="evt_time")
                if st.button("Save Event", use_container_width=True):
                    if title:
                        save_event(
                            st.session_state.username,
                            {"title": title, "date": st.session_state.calendar_clicked_date, "time": time_str},
                        )
                        # Optional Google Sheets logging
                        try:
                            gsheets_append_row("Calendar", [datetime.now().isoformat(), st.session_state.username, st.session_state.calendar_clicked_date, time_str, title])
                        except Exception:
                            pass
                        st.session_state.calendar_clicked_date = None
                        st.success("Event saved.")
                        st.rerun()
                if st.button("Cancel", use_container_width=True, key="evt_cancel"):
                    st.session_state.calendar_clicked_date = None
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Upcoming Events")
        if not events:
            st.info("No events yet. Click a date on the calendar to add one.")
        else:
            for e in sorted(events, key=lambda x: (x.get("date", ""), x.get("time", "")))[:15]:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{e.get('title','Event')}** — {e.get('date')} {e.get('time','')}")
                with c2:
                    if st.button("Delete", key=f"del_evt_{e.get('id')}"):
                        delete_event(st.session_state.username, e.get("id"))
                        st.rerun()

# ==================== PHASE 3: ASSISTANT AI ====================
def show_assistant_ai():
    """Assistant AI sidebar chat"""
    st.sidebar.title("🤖 Assistant AI")
    st.sidebar.caption("Ask me anything about your career journey!")
    
    # Initialize chat history
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = [
            {"role": "assistant", "content": "Hello! I'm your CuraPath AI assistant. How can I help you today? 🎯"}
        ]
    
    # Display chat history
    for message in st.session_state.assistant_messages:
        if message["role"] == "user":
            st.sidebar.markdown(f"**You:** {message['content']}")
        else:
            st.sidebar.markdown(f"**AI:** {message['content']}")
    
    # User input
    user_query = st.sidebar.text_input("Ask a question...", key="ai_query")
    
    if st.sidebar.button("Send", use_container_width=True) and user_query:
        st.session_state.assistant_messages.append({"role": "user", "content": user_query})
        
        # Simple rule-based responses (can be enhanced with OpenAI API)
        query_lower = user_query.lower()
        
        if "roadmap" in query_lower or "path" in query_lower:
            response = "To view your roadmap, go to the Career Oracle section, select a career, and then choose your preferred path (Startup, MNC, Product-based, or FAANG). Each path has specific resources and time estimates! 🗺️"
        elif "progress" in query_lower or "track" in query_lower:
            response = "Track your progress in the Progress Tracker section. You'll see milestones organized by Basics, Intermediate, and Advanced levels. Check off completed tasks to see your progress bar update! 📊"
        elif "career" in query_lower or "suggestion" in query_lower:
            response = "The Career Oracle analyzes your profile (skills, goals, age) to suggest personalized career paths with success probabilities. Check it out in the main navigation! 🔮"
        elif "alarm" in query_lower or "reminder" in query_lower:
            response = "Set alarms in the Life-Tracker section. When an alarm goes off, you'll need to solve a math problem to dismiss it - this helps ensure you're alert and ready! 🔔"
        elif "help" in query_lower:
            response = "I can help you with: navigating the app, understanding career paths, tracking progress, setting alarms, and general career guidance. What would you like to know? 💚"
        else:
            response = "That's a great question! For detailed career guidance, check out the Career Oracle section. For app-specific help, feel free to ask me more specific questions! 🎯"
        
        st.session_state.assistant_messages.append({"role": "assistant", "content": response})
        st.rerun()

# ==================== ACCOUNT SETTINGS ====================
def show_account_settings():
    """Editable Profile Hub / Account Settings"""
    st.title("⚙️ Account Settings")
    st.caption("Update your profile — changes instantly improve your career oracle, roadmaps, and motivation prompts.")

    user_data = get_user_data(st.session_state.username) or {}
    profile = load_profile(st.session_state.username) or user_data.get("profile") or {}

    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 👤 Profile")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=profile.get("name", user_data.get("name", "")), disabled=True)
            age = st.number_input("Age", min_value=13, max_value=100, value=int(profile.get("age", 20)))
        with col2:
            email = st.text_input("Email", value=user_data.get("email", ""), disabled=True)
            school = st.text_input("School / College Name", value=profile.get("school", ""))

        education_level = st.selectbox(
            "Education Level",
            ["High School", "College", "Other"],
            index=["High School", "College", "Other"].index(profile.get("education_level", "College"))
            if profile.get("education_level", "College") in ["High School", "College", "Other"]
            else 1,
        )

        detail = None
        if education_level == "High School":
            detail = st.selectbox(
                "Grade",
                ["9", "10", "11", "12"],
                index=["9", "10", "11", "12"].index(str(profile.get("education_detail", "11")))
                if str(profile.get("education_detail", "11")) in ["9", "10", "11", "12"]
                else 2,
            )
        elif education_level == "College":
            degrees = ["B.Tech", "BCA", "BSc", "BCom", "BA", "BE", "BBA", "M.Tech", "MCA", "MSc", "MBA", "Other"]
            current_degree = profile.get("education_detail", "B.Tech")
            detail = st.selectbox("Degree", degrees, index=degrees.index(current_degree) if current_degree in degrees else 0)
        else:
            detail = st.text_input("Education Detail", value=profile.get("education_detail", ""))

        st.markdown("---")
        st.markdown("### 🧩 Skills & Hobbies")

        tech_skills = st.multiselect(
            "Technical Skills",
            [
                "Frontend (HTML/CSS/JS)",
                "React",
                "Backend (Node/Django/Flask)",
                "Databases (SQL/NoSQL)",
                "DSA",
                "System Design",
                "Python",
                "Java",
                "Cloud (AWS/Azure/GCP)",
                "DevOps (CI/CD)",
                "AI/ML",
                "Cybersecurity",
            ],
            default=profile.get("skills_technical", []),
        )
        soft_skills = st.multiselect(
            "Soft Skills",
            ["Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", "Public Speaking", "Creativity"],
            default=profile.get("skills_soft", []),
        )
        creative_hobbies = st.multiselect(
            "Creative Hobbies",
            ["Design", "Digital Art", "Content Creation", "Writing", "Music", "Photography", "Video Editing", "Gaming", "Public Speaking"],
            default=profile.get("hobbies_creative", []),
        )
        hobbies_other = st.text_area("Other hobbies/interests (optional)", value=profile.get("hobbies_other", ""))

        st.markdown("---")
        st.markdown("### 🎯 Goals & Learning Pace")
        goals = st.text_area("Career Goals", value=profile.get("goals", ""))

        colp1, colp2 = st.columns(2)
        with colp1:
            daily_hours = st.slider("Daily Study Hours", min_value=1, max_value=8, value=int(profile.get("daily_hours", 2)), step=1)
        with colp2:
            pace = st.select_slider("Learning Pace", options=["Slow", "Normal", "Fast"], value=profile.get("learning_pace", "Normal"))

        save = st.button("💾 Save Changes", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if save:
        new_profile = {
            **profile,
            "name": profile.get("name", user_data.get("name", "")),
            "age": int(age),
            "school": school,
            "education_level": education_level,
            "education_detail": detail,
            "skills_technical": tech_skills,
            "skills_soft": soft_skills,
            "hobbies_creative": creative_hobbies,
            "hobbies_other": hobbies_other,
            "goals": goals,
            "daily_hours": int(daily_hours),
            "learning_pace": pace,
        }
        save_profile(st.session_state.username, new_profile)
        save_user_data(st.session_state.username, {"profile": new_profile})
        st.success("Profile updated. Your recommendations will refresh across the app.")
        st.rerun()

# ==================== MAIN NAVIGATION ====================
def show_main_app():
    """Main application interface"""
    # Render header
    render_header()
    
    # Sidebar navigation
    st.sidebar.title("🎯 CuraPath AI")
    st.sidebar.markdown(f"**Welcome, {st.session_state.username}!**")
    st.sidebar.markdown("---")
    
    # Navigation menu
    nav_options = {
        "🔮 Career Oracle": "oracle",
        "🗺️ Strategic Roadmap": "roadmap",
        "📊 Progress Tracker": "progress",
        "🎯 Placement Readiness": "placement",
        "💚 Mind-Care Suite": "mindcare",
        "⏰ Life-Tracker": "lifetracker",
        "⚙️ Account Settings": "settings",
    }
    
    for label, section in nav_options.items():
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{section}"):
            st.session_state.current_section = section
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Assistant AI (always visible)
    show_assistant_ai()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.onboarding_complete = False
        st.session_state.current_section = "oracle"
        st.rerun()
    
    # Main content area
    if st.session_state.current_section == "oracle":
        show_career_oracle()
    elif st.session_state.current_section == "roadmap":
        show_roadmap()
    elif st.session_state.current_section == "progress":
        show_progress_tracker()
    elif st.session_state.current_section == "placement":
        show_placement_readiness()
    elif st.session_state.current_section == "mindcare":
        show_mindcare()
    elif st.session_state.current_section == "lifetracker":
        show_lifetracker()
    elif st.session_state.current_section == "settings":
        show_account_settings()

# ==================== MAIN APP FLOW ====================
def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        show_auth_page()
    elif not st.session_state.onboarding_complete:
        show_onboarding()
    else:
        show_main_app()

if __name__ == "__main__":
    main()

