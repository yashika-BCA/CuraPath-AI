# 🎯 CuraPath AI - Your Personalized Career Journey Companion

A comprehensive career guidance platform built with Streamlit that provides personalized career paths, progress tracking, and mental wellness support.

## ✨ Features

### Phase 1: Entry & Profile
- **Secure Authentication**: Login/Signup with bcrypt password hashing
- **Multi-step Onboarding**: Comprehensive questionnaire covering Name, Age, School, Skills, Hobbies, and Goals
- **Persistent User Profiles**: All data saved locally in JSON format

### Phase 2: Career Journey Flow
- **🔮 Career Oracle**: AI-powered career suggestions with:
  - Success Probability %
  - Time Estimates
  - Personalized Reasoning
  - Required Skills Analysis
  
- **🗺️ Strategic Roadmap**: Four distinct career paths:
  - Startup Path
  - MNC Path
  - Product-based Path
  - FAANG Path
  
  Each path includes:
  - Free Resources
  - Paid Resources
  - Certification Courses
  - Non-Certification Projects
  
- **📊 Interactive Progress Tracker**: IBM-style visual interface
  - Three levels: Basics → Intermediate → Advanced
  - Checkbox milestones
  - Real-time progress bar (top of screen)
  - Seamless flow from Career → Roadmap → Progress

### Phase 3: Daily Utility & Support
- **💚 Mind-Care Suite**:
  - Vent Box: Private journaling space
  - Empathetic AI: Burnout detection and motivational support
  - Success Stories: Inspiring real-world examples
  - Mood Tracker: Daily emotional well-being tracking

- **⏰ Life-Tracker**:
  - Study Alarms & Reminders
  - Math Challenge: Solve problems to dismiss alarms (Alarmy-style)
  - Task Checklist: Daily roadmap goal tracking
  - Calendar: Event and reminder management

- **🤖 Assistant AI**: Sidebar chat for app help and career queries

## 🎨 UI/UX Features
- **Glassmorphism Design**: Modern, professional glass-effect styling
- **Dark Theme**: Beautiful dark-themed GUI
- **Real-time Clock & Date**: Displayed in header
- **Theme Toggle**: Switch between light/dark modes
- **Smooth Animations**: Professional transitions and hover effects
- **Rounded UI**: Modern, friendly interface design

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

## 📁 Project Structure

```
CuraPath AI/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── utils/
│   ├── __init__.py
│   ├── auth.py           # Authentication utilities
│   ├── storage.py        # Data persistence utilities
│   ├── career_engine.py  # Career suggestion engine
│   └── ui_components.py  # UI components and styling
└── data/                 # User data storage (created automatically)
    ├── users.json
    ├── profiles/
    ├── progress/
    ├── journals/
    ├── tasks/
    └── alarms/
```

## 🔐 Security

- Passwords are hashed using bcrypt
- User data stored locally in JSON files
- Session-based authentication
- Secure user profile management

## 🎯 Usage Flow

1. **Sign Up/Login**: Create an account or login
2. **Complete Onboarding**: Fill out the multi-step questionnaire
3. **Explore Career Oracle**: View personalized career suggestions
4. **Select a Career**: Click on a suggested career path
5. **Choose Your Path**: Select Startup, MNC, Product-based, or FAANG
6. **Track Progress**: Mark milestones as complete and watch your progress bar
7. **Use Daily Tools**: Set alarms, track tasks, journal, and get support

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **bcrypt**: Password hashing
- **Pandas**: Data manipulation
- **JSON**: Data storage
- **Python**: Core programming language

## 📝 Notes

- All data is stored locally in the `data/` directory
- The application uses session state for seamless navigation
- Career suggestions are based on user profile analysis
- Progress tracking is persistent across sessions

## 🎨 Customization

You can customize:
- Career database in `utils/career_engine.py`
- UI styling in `utils/ui_components.py`
- Theme colors in `.streamlit/config.toml`

## 📧 Support

For issues or questions, please refer to the Assistant AI within the application or check the documentation.

---

**Built with ❤️ for students and career changers**

