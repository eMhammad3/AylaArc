import streamlit as st
import core_logic  # العقل المدبر
import time
import db_handler

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="AylaArc | المعمارية آيلا",
    page_icon="👷‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تهيئة الذاكرة والمراحل (النسخة الذكية مع الاستعادة 🧠)
if 'app_stage' not in st.session_state:
    
    # --- 1. محاولة الاستعادة من الرابط (Auto-Login Logic) ---
    # نفحص إذا كان هناك توكن في الرابط
    token_in_url = st.query_params.get("auth_token")
    
    if token_in_url and 'user' not in st.session_state:
        with st.spinner("جاري استعادة جلستك..."):
            # نحاول الدخول باستخدام التوكن
            res = db_handler.login_with_token(token_in_url)
            if res.get("success"):
                st.session_state.user = res["user"]
            else:
                # إذا التوكن خربان، نمسحه من الرابط
                st.query_params.clear()
    
    # --- 2. المنطق المعتاد ---
    active_user = None 
    if 'user' in st.session_state:
        active_user = st.session_state.user

    if active_user:
        # نتأكد أن التوكن موجود في الرابط دائماً للحفاظ على الجلسة عند الريلود
        try:
            # نجلب التوكن الحالي
            current_token = active_user.session.access_token if hasattr(active_user, 'session') else None
            # ملاحظة: أحياناً object user لا يحتوي session مباشرة، لذا نعتمد على auth response
            # للتبسيط، سنعتمد على أن الدخول يضع التوكن، لكن هنا سنثبت الوجود
            pass 
        except: pass

        st.session_state.user = active_user
        
        query_params = st.query_params
        pid = query_params.get("pid")
        
        if pid:
            with st.spinner("جاري استعادة جلسة العمل..."):
                p = db_handler.get_project_by_id(pid)
                if p:
                    st.session_state.project_data = {
                        "id": p['id'],
                        "name": p['name'],
                        "type": p['project_type'],
                        "site": p['site_context'],
                        "requirements": p['requirements']
                    }
                    st.session_state.messages = db_handler.get_project_messages(pid)
                    st.session_state.app_stage = 'main_chat'
                else:
                    st.session_state.app_stage = 'project_landing'
        else:
            st.session_state.app_stage = 'project_landing'
            
        try:
            profile_res = db_handler.supabase.table("profiles").select("*").eq("id", active_user.id).execute()
            if profile_res.data:
                prof = profile_res.data[0]
                st.session_state.project_data["user_real_name"] = prof.get("real_name", "Architect")
                st.session_state.project_data["user_nickname"] = prof.get("nickname", "Arch")
        except: pass
    else:
        st.session_state.app_stage = 'profile'

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'project_data' not in st.session_state:
    st.session_state.project_data = {}
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
# متغير لتخزين حالة فتح القفل للمرحلة الثانية
if 'phase2_unlocked' not in st.session_state:
    st.session_state.phase2_unlocked = False
if 'active_phase_idx' not in st.session_state:
    st.session_state.active_phase_idx = 0

# تعريف المراحل (نسخة مختصرة وأنيقة للواجهة)
phases = {
    "0️⃣ المحادثة والإعداد | SETUP": "0️⃣ General Chat & Setup",
    "1️⃣ تحليل الموقع | SITE ANALYSIS": "1️⃣ Site & Research (Active)",
    "2️⃣ الفكرة والتوزيع | CON&ZONINIG": "2️⃣ Concept & Zoning",
    "3️⃣ السكيتشات | SKETCHES": "3️⃣ Sketches & Freehand",
    "4️⃣ المخططات | 2D PLANS": "4️⃣ 2D Drafting / Plans",
    "5️⃣ المودل | 3D MODELING": "5️⃣ 3D Modeling",
    "6️⃣ الإظهار المعماري | VIZ": "6️⃣ Visualization",
    "7️⃣ الماكيت | PHYSICAL MODEL": "7️⃣ Physical Model",
    "8️⃣ التسليم النهائي | SUBMISSION": "8️⃣ Jury & Marketing"
}

# 3. الستايل (CSS) - النسخة الذهبية (Clean Cut) ✨
st.markdown("""
    <style>
        /* =========================================
           1. الأساسيات والخطوط
           ========================================= */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans Arabic', sans-serif;
            scroll-behavior: smooth;
        }

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, #000000 100%);
        }

        h1, h2, h3, h4, .stCaption, p, div, label, .stTextInput, .stTextArea {
            direction: rtl;
            text-align: right;
        }

        /* =========================================
           2. السهم الذكي (Smart Toggle)
           ========================================= */
        header[data-testid="stHeader"] {
            background: transparent !important;
            z-index: 1 !important;
            height: 0px !important;
        }
        [data-testid="stDecoration"] { display: none; }

        /* الزر عندما تكون القائمة مغلقة */
        [data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            color: #fca311 !important;
            background-color: rgba(26, 26, 26, 0.9) !important;
            border: 1px solid #fca311 !important;
            border-radius: 8px !important;
            top: 20px !important;
            left: 20px !important;
            z-index: 1000002 !important;
            transition: all 0.3s ease;
        }
        [data-testid="stSidebarCollapsedControl"]:hover {
            transform: scale(1.1);
            background-color: #fca311 !important;
            color: black !important;
        }

        /* الزر عندما تكون القائمة مفتوحة */
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapsedControl"] {
            position: absolute !important;
            left: auto !important;
            right: 10px !important;
            top: 10px !important;
            background-color: transparent !important;
            border: none !important;
            color: #666 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapsedControl"]:hover {
            color: #fca311 !important;
            background-color: transparent !important;
            transform: scale(1.1);
        }

        /* =========================================
           3. القائمة الجانبية (The Clean Logic) 🧠🩸
           ========================================= */
        
        /* 1. الإطار الخارجي (الأب): يعمل فقط كـ "مقص" */
        section[data-testid="stSidebar"] {
            background-color: transparent !important; /* لا لون */
            border: none !important; /* لا حدود */
            box-shadow: none !important; /* لا ظل */
            overflow: hidden !important; /* قص أي شيء يخرج عنه */
        }

        /* 2. المحتوى الداخلي (الابن): هو من يحمل اللون والحدود */
        section[data-testid="stSidebar"] > div {
            background-color: #0c0c0c !important;
            border-right: 1px solid #222 !important; /* الحد هنا */
            box-shadow: 5px 0 20px rgba(0,0,0,0.7); /* الظل هنا */
            padding-top: 40px !important;
            height: 100vh !important; /* ارتفاع كامل */
            width: 100% !important;
        }

        /* منع النصوص من التكسر */
        section[data-testid="stSidebar"] * {
            white-space: nowrap !important;
        }

        /* =========================================
           4. كاردات المشاريع
           ========================================= */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
        }
        div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
            border-color: #fca311 !important;
            transform: translateY(-2px);
        }

        /* =========================================
           5. الشات والرسائل (تعديل: إخفاء بوكس الآيلا)
           ========================================= */
        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
        }
        
        /* 1. رسالة الطالب (تبقى بستايل وصندوق) */
        div[data-testid="stChatMessage"]:has(.user-marker) {
            flex-direction: row-reverse !important;
        }
        div[data-testid="stChatMessage"]:has(.user-marker) div[data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            border: 1px solid rgba(255,255,255,0.1);
            color: white;
            border-radius: 20px 5px 20px 20px !important;
            padding: 15px !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            text-align: right;
            direction: rtl;
        }

        /* 2. رسالة آيلا (بدون صندوق - نص فقط) */
        div[data-testid="stChatMessage"]:has(.assistant-marker) div[data-testid="stChatMessageContent"] {
            background: transparent !important; /* خلفية شفافة */
            border: none !important;            /* بدون حدود */
            box-shadow: none !important;        /* بدون ظل */
            color: #e0e0e0;                     /* لون النص */
            padding: 15px 0px !important;       /* تقليل الحواف الجانبية */
            text-align: right;
            direction: rtl;
        }
        
        /* إخفاء الأيقونات الصغيرة إن أردت، أو ابقائها */
        .user-marker, .assistant-marker { display: none; }
            
        /* =========================================
           6. تحسينات عامة
           ========================================= */
        .stTextInput input, .stTextArea textarea {
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: white !important;
            border-radius: 8px !important;
            direction: rtl;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #fca311 !important;
        }
        /* الأزرار الأساسية (ابدأي مشروعك / دخول المرسم) */
        div.stButton > button[kind="primary"] {
            background-color: #fca311 !important; /* ذهبي خالص */
            color: #000000 !important;           /* نص أسود فخم */
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 15px rgba(252, 163, 17, 0.3) !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #ffb742 !important; /* تفتيح عند اللمس */
            transform: translateY(-2px) !important;
        }

        /* أزرار تسجيل الخروج (إطار ذهبي فقط) */
        div.stButton > button[kind="secondary"] {
            background-color: transparent !important;
            color: #fca311 !important;
            border: 1px solid rgba(252, 163, 17, 0.5) !important;
            border-radius: 10px !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            border-color: #fca311 !important;
            background-color: rgba(252, 163, 17, 0.05) !important;
        }
        .lock-overlay {
            background: rgba(0,0,0,0.5);
            border: 1px dashed #555;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
        }
            
        /* =========================================
               7. تنسيقات خاصة لتاب التسجيل الفخم
               ========================================= */
            /* صندوق الرسالة الخاصة */
            .exclusive-msg-box {
                background: rgba(252, 163, 17, 0.08);
                border-right: 4px solid #fca311;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
            }
            
            /* كلاس لجعل حقول المعلومات الثابتة شفافة وذهبية */
            .static-info-field .stTextInput input:disabled {
                background-color: transparent !important; /* شفاف */
                border: none !important; /* بدون حدود */
                border-bottom: 1px dashed rgba(252, 163, 17, 0.3) !important; /* خط سفلي خفيف */
                color: #fca311 !important; /* لون ذهبي للنص */
                font-weight: 600 !important;
                font-size: 1rem !important;
                padding-right: 0 !important; /* إلغاء الحشو الجانبي */
                cursor: default !important; /* الماوس العادي */
                opacity: 1 !important; /* وضوح كامل */
            }
            /* تصغير لون العنوان للحقول الثابتة */
            .static-info-field label {
                 color: #888 !important;
                 font-size: 0.8rem !important;
            }

            /* =========================================
           8. بوابة المشروع الملكية (The Royal Gateway)
           ========================================= */
        .royal-project-gateway {
            position: relative;
            margin-top: 60px;
            padding: 60px 40px;
            text-align: center;
            /* خلفية متدرجة ذهبية داكنة مع شفافية */
            background: linear-gradient(135deg, rgba(252, 163, 17, 0.15) 0%, rgba(0,0,0,0.5) 100%);
            backdrop-filter: blur(25px); /* تمويه زجاجي قوي */
            border: 2px solid rgba(252, 163, 17, 0.5); /* إطار ذهبي لامع */
            border-radius: 30px;
            /* ظل عميق يعطي إحساساً بالطفو */
            box-shadow: 0 30px 70px rgba(0,0,0,0.6), inset 0 0 40px rgba(252, 163, 17, 0.1);
            overflow: hidden;
            /* أنيميشن دخول فخم */
            animation: gatewayEntrance 1.2s cubic-bezier(0.22, 1, 0.36, 1);
        }

        @keyframes gatewayEntrance {
            from { opacity: 0; transform: translateY(40px) scale(0.92); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        .gateway-content { position: relative; z-index: 2; }

        .royal-icon {
            font-size: 8rem; /* أيقونة عملاقة */
            margin-bottom: 30px;
            color: #fca311;
            /* توهج ذهبي نابض */
            text-shadow: 0 0 40px rgba(252, 163, 17, 0.7), 0 0 20px rgba(252, 163, 17, 0.9);
            animation: pulseGold 4s infinite alternate ease-in-out;
        }

        @keyframes pulseGold {
            from { text-shadow: 0 0 40px rgba(252, 163, 17, 0.7), 0 0 20px rgba(252, 163, 17, 0.9); transform: scale(1); }
            to { text-shadow: 0 0 70px rgba(252, 163, 17, 0.9), 0 0 35px rgba(252, 163, 17, 1); transform: scale(1.05); }
        }

        .royal-title {
            color: #ffffff;
            font-size: 3.8rem;
            font-weight: 800;
            margin: 0;
            /* تدرج لوني للنص نفسه */
            background: linear-gradient(to right, #fca311, #ffd700, #fca311);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
            filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.5));
        }

        .royal-meta {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            margin-top: 35px;
            font-size: 1.2rem;
        }

        .meta-item {
            background: rgba(252, 163, 17, 0.15);
            padding: 8px 20px;
            border-radius: 25px;
            border: 1px solid rgba(252, 163, 17, 0.3);
            color: #e0e0e0;
            font-weight: 500;
        }

        .golden-sep { color: #fca311; font-size: 1.8rem; opacity: 0.8; }

        /* زخارف الزوايا الذهبية */
        .corner {
            position: absolute;
            width: 40px;
            height: 40px;
            border: 3px solid #fca311;
            z-index: 1;
            opacity: 0.7;
            box-shadow: 0 0 10px rgba(252, 163, 17, 0.4);
        }
        .top-left { top: 15px; left: 15px; border-bottom: none; border-right: none; border-top-left-radius: 10px; }
        .top-right { top: 15px; right: 15px; border-bottom: none; border-left: none; border-top-right-radius: 10px; }
        .bottom-left { bottom: 15px; left: 15px; border-top: none; border-right: none; border-bottom-left-radius: 10px; }
        .bottom-right { bottom: 15px; right: 15px; border-top: none; border-left: none; border-bottom-right-radius: 10px; }
            
            /* =========================================
           9. واجهة الأستوديو (Main Chat Studio)
           ========================================= */
        /* الهيدر العلوي للمشروع */
        .studio-header-bar {
            background: linear-gradient(90deg, rgba(252, 163, 17, 0.1) 0%, rgba(0,0,0,0) 100%);
            border-right: 5px solid #fca311;
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .studio-title {
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            color: #ffffff;
            margin: 0 !important;
            text-shadow: 0 0 15px rgba(252, 163, 17, 0.3);
        }

        /* حاوية المدخلات (Floating Input) */
        .stChatInputContainer {
            border-top: 1px solid rgba(252, 163, 17, 0.2) !important;
            background: rgba(10, 10, 10, 0.8) !important;
            backdrop-filter: blur(10px) !important;
            padding-bottom: 20px !important;
        }
            
        /* 10. فهرس المخططات المطور جداً */
        div[data-testid="stSidebar"] button {
            padding: 8px 10px !important;
            border-radius: 0px 8px 8px 0px !important;
            border: none !important;
            border-right: 3px solid #222 !important;
            background-color: rgba(255, 255, 255, 0.03) !important;
            margin-bottom: 5px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: clip !important; /* قطع النص بدقة */
            font-size: 0.78rem !important; /* تصغير الخط لضمان دخول ZONING */
            display: flex !important;
            justify-content: flex-start !important;
            transition: 0.3s ease-in-out !important;
        }

        /* القفل الحقيقي: إجبار الشفافية واللون الأحمر الباهت */
        div[data-testid="stSidebar"] button:disabled {
            opacity: 0.25 !important; /* شفافية حقيقية */
            filter: grayscale(100%) !important;
            color: #ff4b4b !important; /* تلميح باللون الأحمر للقفل */
            border-right: 3px solid #441111 !important;
            background-color: transparent !important;
        }

        /* المرحلة النشطة: توهج ذهبي */
        div[data-testid="stSidebar"] button[kind="primary"] {
            border-right: 5px solid #fca311 !important;
            background: linear-gradient(90deg, rgba(252, 163, 17, 0.15) 0%, rgba(0,0,0,0) 100%) !important;
            color: #fca311 !important;
            font-weight: 800 !important;
            opacity: 1 !important; /* وضوح كامل */
        }
            
        }

        /* المرحلة النشطة */
        div[data-testid="stSidebar"] button[kind="primary"] {
            border-right: 5px solid #fca311 !important;
            background: linear-gradient(90deg, rgba(252, 163, 17, 0.15) 0%, rgba(0,0,0,0) 100%) !important;
            color: #fca311 !important;
            font-weight: bold !important;
        }
            
            /* استهداف الأزرار المعطلة داخل السايدبار مباشرة لضمان الشفافية */
        div[data-testid="stSidebar"] button:disabled {
            opacity: 0.2 !important; /* شفافة جداً */
            filter: grayscale(100%) blur(1px) !important; /* باهتة ومموّهة قليلاً */
            border: 1px dashed rgba(255,255,255,0.2) !important;
            background-color: transparent !important;
            cursor: not-allowed !important;
        }

        /* ستايل المرحلة النشطة (توهج ذهبي) */
        .active-phase-highlight {
            border-right: 5px solid #fca311 !important;
            background: linear-gradient(90deg, rgba(252, 163, 17, 0.2) 0%, rgba(0,0,0,0) 100%) !important;
            box-shadow: -10px 0 20px rgba(252, 163, 17, 0.1) !important;
        }

        /* إخفاء جملة Press Enter المزعجة */
        .stChatInput div[data-testid="InputInstructions"] {
            display: none !important;
        }
            
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 👤 المرحلة الأولى: الملف الشخصي (واجهة الدخول الفخمة - Luxury Login UI)
# =============================================================================
if st.session_state.app_stage == 'profile':
    
    # --- 1. حقن ستايل الفخامة (CSS Magic) ---
    st.markdown("""
        <style>
            /* إخفاء السايدبار في هذه الصفحة للتركيز التام */
            section[data-testid="stSidebar"] {display: none !important;}

            /* حاوية العنوان الرئيسية - نسخة مضغوطة */
            .luxury-hero-container {
                text-align: center;
                padding: 40px 20px 0px 20px; /* 👈 جعلنا الـ bottom صفراً */
                background: radial-gradient(ellipse at center, rgba(252, 163, 17, 0.15) 0%, rgba(0,0,0,0) 70%);
                margin-bottom: -30px !important; /* 👈 سحبنا صندوق الدخول للأعلى بقوة */
                position: relative;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
                
                .mega-title {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin-bottom: 0px !important; /* 👈 إلغاء أي فراغ تحت كلمة آيلا */
            }

            /* موازنة السلوجان للسنترة المطلقة */
            .slogan-text {
                color: #aaaaaa;
                font-size: 1.2rem;
                letter-spacing: 5px;
                margin-top: 10px;
                /* الخدعة هنا: إضافة بادنج يسار لتعويض الفراغ يمين الحرف الأخير */
                padding-left: 5px; 
                text-align: center;
                width: 100%;
            }

            /* سنترة العنوان في الموبايل */
            @media (max-width: 768px) {
                .mega-title { 
                    flex-direction: column; 
                    gap: 10px; 
                    font-size: 2.5rem; /* صغرنا الخط قليلاً للموبايل */
                    text-align: center;
                }
                .mega-title span { width: 100%; }
            }

            /* تنسيق الجزء الإنجليزي */
            .mega-title .en {
                color: #ffffff;
                text-transform: uppercase;
                letter-spacing: 2px; /* تباعد أحرف للفخامة */
            }

            /* تنسيق الفاصل */
            .mega-title .sep {
                color: #fca311; /* لون ذهبي */
                font-weight: 300;
                opacity: 0.6;
                font-size: 3.5rem;
            }

            /* تنسيق الجزء العربي */
            .mega-title .ar {
                color: #fca311; /* لون ذهبي مميز للاسم العربي */
                font-family: 'IBM Plex Sans Arabic', sans-serif;
            }

            /* الشعار الفرعي (Slogan) - نسخة مضغوطة */
            .slogan-text {
                color: #aaaaaa;
                font-size: 1.2rem;
                font-weight: 300;
                letter-spacing: 5px;
                text-transform: lowercase;
                margin-top: -15px !important; /* 👈 سحبنا النص للأعلى ليقترب من آيلا */
                padding-bottom: 0px;
                opacity: 0.7;
            }
            
            /* تأثيرات إضافية للشاشات الصغيرة */
            @media (max-width: 768px) {
                .mega-title { flex-direction: column; gap: 5px; font-size: 3rem; }
                .mega-title .sep { display: none; } /* إخفاء الفاصل في الموبايل */
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. رسم الواجهة (HTML Structure) ---
    st.markdown("""
        <div class="luxury-hero-container">
            <h1 class="mega-title">
                <span class="en">Ayla Arc</span>
                <span class="sep">|</span>
                <span class="ar">المعمارية آيلا</span>
            </h1>
            <p class="slogan-text">your architecture soulmate</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 3. منطقة التبويبات (Tabs) - تبقى كما هي في الكود الأصلي ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # مسافة بسيطة قبل التابات
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["تسجيل دخول", "إنشاء حساب جديد"])
        
        # --- تاب تسجيل الدخول ---
        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني:", key="login_email")
                password = st.text_input("كلمة المرور:", type="password", key="login_pass")
                submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True)
                
                if submitted:
                    if email and password:
                        with st.spinner("جاري الاتصال بالسيرفر..."):
                            result = db_handler.login_user(email, password)
                            if "success" in result:
                                st.success("تم تسجيل الدخول بنجاح!")
                                st.session_state.user = result["user"]
                                
                                session = db_handler.supabase.auth.get_session()
                                if session:
                                    st.query_params["auth_token"] = session.access_token
                                
                                profile = result["profile"]
                                st.session_state.project_data["user_real_name"] = profile.get("real_name", "Architect")
                                st.session_state.project_data["user_nickname"] = profile.get("nickname", "Arch")
                                time.sleep(1)
                                st.session_state.app_stage = 'project_landing'
                                st.rerun()
                            else:
                                st.error(f"خطأ: {result.get('error')}")
                    else:
                        st.warning("يرجى إدخال البريد وكلمة المرور.")

        # --- تاب إنشاء الحساب (النسخة الخاصة بأسراء) ---
        with tab2:
            # 1. الرسالة المخصصة (بستايل فخم)
            st.markdown("""
                <div class="exclusive-msg-box">
                    <p style='margin:0; color: #e0e0e0; font-size: 0.95rem; line-height: 1.6;'>
                         <b>ملاحظة من النظام:</b> تم تطويري وبرمجتي خصيصاً للمهندسة <b>إسراء</b>.
                        <br>إذا حضرتك مو إسراء، نعتذر منك، غير مسموح الدخول لآيلا.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("signup_form_esraa"):
                 st.caption("👤 البيانات الشخصية (مثبتة في النظام):")
                 
                 # نستخدم حاوية لتطبيق ستايل الحقول الشفافة
                 with st.container():
                     st.markdown('<div class="static-info-field">', unsafe_allow_html=True)
                     col_info1, col_info2 = st.columns(2)
                     with col_info1:
                          # الاسم واللقب (قراءة فقط - شفاف)
                          st.text_input("الاسم:", value="اسراء احمد", disabled=True, key="static_name")
                          st.text_input("اللقب المفضل:", value="سيرو", disabled=True, key="static_nick")
                     with col_info2:
                          # البلد والجامعة (قراءة فقط - شفاف)
                          st.text_input("البلد:", value="العراق", disabled=True, key="static_country")
                          st.text_input("الجامعة:", value="جامعة كربلاء", disabled=True, key="static_uni")
                     
                     # البريد المشفر (قراءة فقط - شفاف)
                     st.text_input("البريد الإلكتروني المعتمد:", value="2isr*****med@gmail.com", disabled=True, key="static_email")
                     st.markdown('</div>', unsafe_allow_html=True)

                 st.markdown("---")
                 
                 # 2. حقول الأمان (قابلة للكتابة - بستايل الإدخال العادي)
                 st.caption("🔒 يرجى إكمال بيانات الأمان لتفعيل الحساب:")
                 
                 # حقل رمز التوثيق الجديد
                 verify_code = st.text_input("رمز التوثيق (Verification Code):", placeholder="أدخلي الرمز السري المزود لكِ...")
                 
                 # حقول كلمة المرور
                 col_pass1, col_pass2 = st.columns(2)
                 with col_pass1:
                     new_pass1 = st.text_input("كلمة المرور الجديدة:", type="password", placeholder="••••••••")
                 with col_pass2:
                     new_pass2 = st.text_input("تأكيد كلمة المرور:", type="password", placeholder="••••••••")

                 st.markdown("<br>", unsafe_allow_html=True)
                 # زر التسجيل (مفعل الآن)
                 submitted_signup = st.form_submit_button("✨ تفعيل الحساب وبدء الرحلة", use_container_width=True)

                 if submitted_signup:
                      # 1. التحقق من صحة المدخلات
                      if new_pass1 and new_pass2 and verify_code:
                           if new_pass1 != new_pass2:
                               st.warning("⚠️ كلمتا المرور غير متطابقتين.")
                           
                           # 2. التحقق من الرمز السري (الحارس)
                           elif verify_code != "AYLA-X5390-SERO.ENG": # 👈 تأكد أن هذا هو الرمز الذي ستعطيه لها
                               st.error("⛔ رمز التوثيق غير صحيح. يرجى التأكد من البطاقة المزودة لكِ.")
                           
                           else:
                               # 3. كل شيء صحيح - نبدأ عملية التسجيل الحقيقية
                               with st.spinner("جاري حفر اسمك في سجلات المعماريين..."):
                                   
                                   # 👈 ملاحظة مهمة: هنا نضع الايميل الحقيقي كاملاً لأننا نعرفه مسبقاً
                                   # هذا الايميل هو الذي سيسجل في سوبابيس
                                   real_email_for_signup = "2israa0ahmed@gmail.com" 
                                   
                                   # استدعاء دالة التسجيل من الهاندلار
                                   # نمرر المعلومات الثابتة (الاسم واللقب) لأننا نعرفها
                                   res = db_handler.signup_user(real_email_for_signup, new_pass1, "إسراء أحمد", "سيرو")
                                   
                                   if "success" in res:
                                       # 4. نجاح التسجيل - تسجيل الدخول تلقائياً
                                       st.session_state.user = res["user"]
                                       
                                       # حفظ التوكن في الرابط
                                       session = db_handler.supabase.auth.get_session()
                                       if session:
                                           st.query_params["auth_token"] = session.access_token
                                       
                                       # حفظ بيانات البروفايل في الجلسة
                                       st.session_state.project_data["user_real_name"] = "إسراء أحمد"
                                       st.session_state.project_data["user_nickname"] = "سيرو"
                                       
                                       st.toast("تم تفعيل الحساب بنجاح! 🏛️", icon="✨")
                                       time.sleep(1.5)
                                       st.session_state.app_stage = 'project_landing'
                                       st.rerun()
                                   else:
                                       # في حال حدوث خطأ من السيرفر (مثلاً الايميل مسجل مسبقاً)
                                       st.error(f"حدث خطأ في التسجيل: {res.get('error')}")
                      else:
                           st.warning("⚠️ يرجى تعبئة رمز التوثيق وكلمة المرور.")

# =============================================================================
# 🏛️ المرحلة الثانية: لوحة المشاريع (المرسم المعماري الفاخر)
# =============================================================================
elif st.session_state.app_stage == 'project_landing':
    user = st.session_state.get('user')
    profile = st.session_state.get('project_data', {}) 

    # --- 1. ستايل "المرسم المعماري" (CSS Magic) ---
    st.markdown("""
        <style>
            /* حاوية البطاقة الزجاجية */
            .project-card {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(252, 163, 17, 0.15);
                border-right: 6px solid #fca311; /* العمود الذهبي للهوية */
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 15px;
                transition: all 0.3s ease;
            }
            .project-card:hover {
                transform: translateX(-8px);
                background: rgba(252, 163, 17, 0.05);
                border-color: #fca311;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            /* تنسيق الأيقونة المتوهجة */
            .icon-box {
                font-size: 2.2rem;
                margin-left: 20px;
                filter: drop-shadow(0 0 10px rgba(252, 163, 17, 0.4));
            }
            .p-name { color: #fca311; font-size: 1.6rem; font-weight: bold; margin:0; }
            .p-meta { color: #888; font-size: 0.9rem; margin-top: 5px; letter-spacing: 1px; }
        </style>
    """, unsafe_allow_html=True)

    # الهيدر (نسخة النص الثابت الفخم) 🏛️✨
    col_h, col_l = st.columns([4, 1.2])
    with col_h:
        # العنوان الرئيسي الثابت
        st.markdown("<h1 style='color: #fca311; margin:0;'>أنرتِ مرسمكِ الرقمي.. ✨</h1>", unsafe_allow_html=True)
        
        # النص الذي طلبته بالضبط (Fixed)
        st.markdown("""
            <p style='color: #ccc; font-size: 1.2rem;'>
                المعمارية اسراء | <span style='color: #fca311; font-weight: bold;'>مترقبة تحديثات مشروعكِ الحالي.</span>
            </p>
        """, unsafe_allow_html=True)
    with col_l:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("تسجيل الخروج", key="logout_top", type="primary", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear()
            db_handler.logout_user()
            st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
  
    # جلب المشاريع من قاعدة البيانات
    with st.spinner("جاري جلب المخططات من الأرشيف..."):
        response = db_handler.get_user_projects(user.id)
        
    # --- بداية نظام المشروع الواحد (The Single Workspace) ---
    if "error" in response:
        st.error(f"حدث خطأ في جلب البيانات: {response['error']}")
    else:
        projects = response.get("data", [])
        
        if projects:
            # نأخذ المشروع الوحيد الموجود
            p = projects[0] 
            
            # 1. عرض بوابة المشروع الملكية (The Royal Gateway) 🏛️✨
            project_icon = ""
            # نضمن إن السستم ما يوكع إذا كان النوع فارغ
            p_type_check = p.get('project_type') or ""
            project_icon = "🏛️" # أيقونة افتراضية
            if "Residential" in p_type_check: project_icon = "🏡"
            elif "Commercial" in p_type_check: project_icon = "🏢"
            elif "Educational" in p_type_check: project_icon = "🏫"
            
            # ملاحظة: تم تنظيف الكود من أي رموز قد تسبب تداخل (Escaping)
            html_content = f"""
                <div class="royal-project-gateway">
                    <div class="gateway-content">
                        <div class="royal-icon">{project_icon}</div>
                        <h1 class="royal-title">{p['name']}</h1>
                        <div class="royal-meta">
                            <span class="meta-item">📌 {p['project_type']}</span>
                            <span class="golden-sep">♦</span>
                            <span class="meta-item">📅 بدأنا الرحلة: {p['created_at'][:10]}</span>
                        </div>
                    </div>
                    <div class="corner top-left"></div>
                    <div class="corner top-right"></div>
                    <div class="corner bottom-left"></div>
                    <div class="corner bottom-right"></div>
                </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            
            # 2. أزرار التحكم المركزية (فتح أو تصفير)
            st.markdown("<br>", unsafe_allow_html=True)
            c_open, c_reset = st.columns([1, 1])
            
            with c_open:
                if st.button("دخول المرسم المعماري 🔓", use_container_width=True, type="primary"):
                    st.query_params["pid"] = p['id']
                    # نحدث الذاكرة بكل محتويات المشروع p اللي جلبناه من الداتابيس
                    st.session_state.project_data.update(p)
                    st.session_state.project_data["user_real_name"] = profile.get('user_real_name')
                    st.session_state.project_data["user_nickname"] = profile.get('user_nickname')
                    })
                    st.session_state.messages = db_handler.get_project_messages(p['id'])
                    st.session_state.app_stage = 'main_chat'
                    st.rerun()
                    
            with c_reset:
                # زر "تغيير المشروع" يظهر بداخل بوب أوفر للأمان
                with st.popover("إنهاء وحذف المشروع", use_container_width=True):
                    st.error("⚠️ تحذير: هذا الإجراء سيحذف المشروع الحالي لبدء مشروع جديد كلياً.")
                    if st.button("تأكيد الحذف النهائي", key="reset_single_p", type="primary", use_container_width=True):
                        db_handler.delete_project_permanently(p['id'])
                        st.rerun()
        
        else:
            # 3. حالة "المرسم الفارغ" (عندما لا يوجد مشروع)
            st.markdown("""
                <div style='text-align: center; padding: 100px 20px;'>
                    <div style="font-size: 4rem; opacity: 0.2; margin-bottom: 20px;">📐</div>
                    <h2 style='color: #666;'>المرسم بانتظار خطواتكِ الأولى..</h2>
                    <p style='color: #444;'>إسراء، آيلا جاهزة لمرافقتكِ في تحدي هذا الكورس.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("➕ ابدأي مشروعكِ المعماري الآن", use_container_width=True, type="primary"):
                st.session_state.app_stage = 'project_form'
                st.rerun()
    # --- نهاية نظام المشروع الواحد ---

# =============================================================================
# 📝 المرحلة الثالثة: فورم بيانات المشروع
# =============================================================================
elif st.session_state.app_stage == 'project_form':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 👇👇 إضافة زر الرجوع هنا 👇👇
        if st.button("⬅️ رجوع للقائمة", use_container_width=True):
            st.session_state.app_stage = 'project_landing'
            st.rerun()
        # 👆👆 انتهت الإضافة 👆👆

        st.markdown("<h2 style='text-align: right; color: #fca311;'>📝 بيانات المشروع الجديد</h2>", unsafe_allow_html=True)
        st.caption("")
        
        with st.form("project_setup_form"):
            # --- القسم الأول: معلومات أكاديمية ثابتة (مقفلة تماماً) ---
            st.markdown("<p style='color: #888; font-size: 0.8rem; margin-bottom: 10px;'>🏛️ السجل الأكاديمي المثبت:</p>", unsafe_allow_html=True)
            
            row_static_1, row_static_2 = st.columns(2)
            with row_static_1:
                st.text_input("المرحلة:", value="الثانية", disabled=True, key="p_fixed_stage")
                st.text_input("المادة:", value="دزاين - Design", disabled=True, key="p_fixed_subject")
            with row_static_2:
                st.text_input("عدد المنافسين مع رفع ملفاتهم:", value="45", disabled=True, key="p_fixed_comp")
                st.text_input("اسم دكتور المادة (رئيس لجنة ال Jury):", value="د. أنور", disabled=True, key="p_fixed_dr")
            
            st.markdown("<hr style='margin: 15px 0; border-color: rgba(252, 163, 17, 0.1);'>", unsafe_allow_html=True)
            
            # --- القسم الثاني: تفاصيل المشروع (المتغيرة) ---
            p_name = st.text_input("اسم المشروع:", placeholder="مثال: مركز ثقافي...")
            
            # نوع المشروع مع التعريب والخيار اليدوي
            project_options = [
                "سكنى (Residential)", 
                "ثقافي / عام (Cultural/Public)", 
                "تجاري (Commercial)", 
                "لاندسكيب (Landscape)", 
                "تصميم حضري (Urban Design)", 
                "مباني تعليمية (Educational)", 
                "أخرى (كتابة يدوية)..."
            ]
            selected_type = st.selectbox("نوع المشروع:", project_options)
            
            if selected_type == "أخرى (كتابة يدوية)...":
                p_type = st.text_input("اكتبي نوع المشروع هنا:", placeholder="مثال: فندق، مستشفى...")
            else:
                p_type = selected_type

            p_site = st.text_area("تفاصيل الموقع (Site Context):")
            
            # 💡 الحقل المنسي المهم جداً: المساحة
            p_area = st.text_input("مساحة الأرض (م2) أو الأبعاد:", placeholder="مثال: 600 متر مربع")
            
            p_req = st.text_area("أهم المتطلبات (Program):")
            
            submitted = st.form_submit_button("🚀 حفظ وبدء الرحلة")
            
            if submitted:
                if p_name and p_req:
                    with st.spinner("جاري أرشفة المشروع في السحابة..."):
                        user_id = st.session_state.user.id
                        
                        # ندمج المساحة مع الموقع لضمان وصولها لآيلا بدون تغيير هيكل الداتابيز
                        full_site_info = f"{p_site}\nالمساحة: {p_area}"
                        
                        result = db_handler.create_project(user_id, p_name, p_type, p_site, p_req, p_area)
                    
                    if "success" in result:
                        st.success("تم الحفظ بنجاح!")
                        new_project = result['data'][0]
                        current_real_name = st.session_state.project_data.get('user_real_name')
                        current_nickname = st.session_state.project_data.get('user_nickname')

                        # نحدث البيانات كاملة من اللي رجع من الداتابيس حتى ما ننسى شي
                        # 1. شحن البيانات كاملة
                        st.session_state.project_data = new_project
                        st.session_state.project_data["user_real_name"] = current_real_name
                        st.session_state.project_data["user_nickname"] = current_nickname
                        
                        # 2. تثبيت المعرف في الرابط
                        st.query_params["pid"] = new_project['id']
                        
                        # 3. توجيه آيلا لغرفة الشات (لأن الـ dashboard ممسوح من الكود عندك)
                        st.session_state.app_stage = 'main_chat' 
                        st.rerun()
                    else:
                        st.error(f"فشل الحفظ: {result.get('error')}")
                else:
                    st.error("يرجى ملء الحقول الأساسية.")
# =============================================================================
# 💬 المرحلة الرابعة: الشات الرئيسي (Main Chat) - نظام الأقفال 🔒
# =============================================================================
elif st.session_state.app_stage == 'main_chat':

    with st.sidebar:
        st.title("👩‍💼 AylaArc")
        st.caption("Your Architectural Companion Soulmate")
        
        # --- 1. زر الرجوع للقائمة الرئيسية ---
        if st.button("🔙", use_container_width=True):
            st.session_state.app_stage = 'project_landing'
            st.session_state.messages = [] 
            st.rerun()
            
        st.markdown("---")
        
        # --- المحرك المطور V4: فهرس المخططات بالأقفال الحمراء ---
        st.markdown("<p style='color: #666; font-size: 0.75rem; margin-bottom: 12px; letter-spacing: 2px; text-align:right;'>ARCHITECTURE INDEX</p>", unsafe_allow_html=True)
        
        phase_keys = list(phases.keys())
        max_unlocked = st.session_state.project_data.get('unlocked_phase', 0) 

        for idx, p_name in enumerate(phase_keys):
            is_active = (idx == st.session_state.active_phase_idx)
            is_locked = (idx > max_unlocked) 
            
            # تحديد الأيقونة: أحمر للمقفل، ذهبي للنشط، أخضر للمكتمل
            if is_locked: status_icon = "🔴" # العلامة الحمراء كما طلبت
            elif idx < st.session_state.active_phase_idx: status_icon = "🟢"
            else: status_icon = "📐"

            # رسم الزر
            if st.button(f"{status_icon} {p_name}", 
                         key=f"nav_v4_{idx}", 
                         use_container_width=True, 
                         disabled=is_locked, 
                         type="primary" if is_active else "secondary"):
                st.session_state.active_phase_idx = idx
                st.rerun()
            
            # سطر متغير بعد المرحلة النشطة فقط
            if is_active and idx == max_unlocked:
                st.markdown(f"""
                    <div style='background: rgba(252, 163, 17, 0.1); border-right: 2px solid #fca311; padding: 5px 10px; margin: -5px 0 10px 0; border-radius: 0 5px 5px 0;'>
                        <p style='color: #fca311; font-size: 0.75rem; margin: 0;'>📝 للانتقال للمرحلة التالية.. يجب أن توافق آيلا.</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # ربط المرحلة المختارة ببقية الكود (للحفاظ على الوظائف)
        selected_phase_key = phase_keys[st.session_state.active_phase_idx]
        
        st.markdown("---")
        
        # --- 2. زر محادثة جديدة (النسخة الآمنة مع الأرشيف) 🛡️ ---
        if st.button("✨ محادثة جديدة (ارشفة الحالية)", help="يحفظ المحادثة الحالية في الأرشيف، يلخصها للذاكرة، ثم يفرغ الشات.", use_container_width=True):
            
            if len(st.session_state.messages) > 0:
                with st.spinner("جاري الأرشفة وتنظيف المكتب..."):
                    try:
                        pid = st.session_state.project_data['id']
                        
                        # أ) التلخيص والحفظ في الذاكرة الحية
                        old_sum = db_handler.get_project_summary(pid)
                        new_sum = old_sum
                        if len(st.session_state.messages) > 2:
                            new_sum = core_logic.generate_summary(st.session_state.messages, old_sum)
                            db_handler.update_project_summary(pid, new_sum)
                        
                        # ب) الأرشفة (الجديد! 🆕): نحفظ النص الكامل في جدول الأرشيف
                        db_handler.archive_current_chat(pid, st.session_state.messages, new_sum)
                        
                        # ج) التنظيف: الآن نحذف من الشات النشط بقلب مطمئن
                        db_handler.clear_project_chat_history(pid)
                        
                        st.toast("تمت الأرشفة وبدء صفحة جديدة!", icon="✅")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
            
            st.session_state.messages = []
            time.sleep(1)
            st.rerun()

        # --- 3. خانة المحادثات السابقة (طلبك) 📜 ---
        with st.expander("📜 أرشيف المحادثات السابقة"):
            pid = st.session_state.project_data.get('id')
            archives = db_handler.get_project_archives(pid)
            
            if not archives:
                st.caption("لا توجد محادثات مؤرشفة بعد.")
            else:
                for arch in archives:
                    # عرض التاريخ كعنوان
                    date_label = arch['created_at'][:10] + " " + arch['created_at'][11:16]
                    if st.button(f"📅 {date_label}", key=f"arch_{arch['id']}", use_container_width=True):
                        # عرض المحادثة في نافذة منبثقة (Modal)
                        @st.dialog("📜 تفاصيل المحادثة المؤرشفة")
                        def show_archive_content(text):
                            st.text_area("", value=text, height=400, disabled=True)
                        show_archive_content(arch['full_conversation'])

        st.markdown("---")
        
        # --- 4. منطقة الخطر ---
        with st.expander("حذف المشروع"):
            st.warning("لا يمكن التراجع!")
            if st.button("تأكيد الحذف", type="primary", use_container_width=True):
                pid = st.session_state.project_data['id']
                db_handler.delete_project_permanently(pid)
                st.session_state.app_stage = 'project_landing'
                st.rerun()

        if st.button("تسجيل خروج", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear() 
            db_handler.logout_user()
            st.rerun()

    p_data = st.session_state.get('project_data', {})
    project_title = p_data.get('name', 'New Project')
    
    # هيدر الأستوديو المطور (Architecture Studio Header)
    st.markdown(f"""
        <div class="studio-header-bar">
            <div>
                <h1 class="studio-title">🏛️ {project_title}</h1>
                <p style="color: #888; margin-top: 5px; font-size: 0.9rem; letter-spacing: 1px;">
                    STUDIO: {p_data.get('type')} | <span style="color: #fca311;">PHASE: {phases[selected_phase_key]}</span>
                </p>
            </div>
            <div style="text-align: left; opacity: 0.5;">
                <span style="font-size: 0.8rem; color: #fca311;">AYLA ARC SYSTEM v2.5</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # 🕵️‍♂️ منطق الأقفال (The Guard System)
    # ==================================================
    
    is_active_phase = False
    is_locked_phase = False
    is_dev_phase = False

    if selected_phase_key.startswith("0️⃣") or selected_phase_key.startswith("1️⃣"):
        is_active_phase = True
    elif selected_phase_key.startswith("2️⃣"):
        if st.session_state.phase2_unlocked:
            is_active_phase = True
        else:
            is_locked_phase = True
    else:
        is_dev_phase = True

    if is_locked_phase:
        st.markdown("""
            <div class='lock-overlay'>
                <h1 style='font-size: 60px;'>🔒</h1>
                <h3>عذراً يا معمارية، هذه المرحلة مقفلة!</h3>
                <p style='color: #888;'>آيلا تعتقد أنك لم تنهي تحليل الموقع (Phase 1) بشكل كامل بعد.<br>
                الانتقال للفكرة دون تحليل دقيق هو "انتحار تصميمي".</p>
            </div>
        """, unsafe_allow_html=True)
        col_L1, col_L2, col_L3 = st.columns([1, 2, 1])
        with col_L2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚠️ أنا أتحمل المسؤولية (دخول مجازفة)", use_container_width=True, type="primary"):
                st.session_state.phase2_unlocked = True
                st.toast("تم كسر القفل! آيلا ستراقب قراراتك بدقة...", icon="👀")
                time.sleep(1.5)
                st.rerun()

    elif is_dev_phase:
        st.markdown("""
            <div class='lock-overlay' style='border-color: #fca311; opacity: 0.7;'>
                <h1 style='font-size: 60px;'>🚧</h1>
                <h3>هذه المنطقة قيد الإنشاء</h3>
                <p>فريق التطوير يعمل حالياً على تجهيز أدوات هذه المرحلة.<br>
                ستكون متاحة في التحديث القادم.</p>
            </div>
        """, unsafe_allow_html=True)

    else:

        # --- عرض الرسائل ---
        user_indices = [i for i, m in enumerate(st.session_state.messages) if m['role'] == 'user']
        last_user_index = user_indices[-1] if user_indices else -1

        for i, message in enumerate(st.session_state.messages):
            role = message["role"]
            avatar = "👷‍♀️" if role == "user" else "👩‍💼"
            
            if st.session_state.edit_index == i:
                with st.container(border=True):
                    st.caption("📝 تعديل الرسالة:")
                    new_text = st.text_area("نص الرسالة:", value=message["content"], key=f"edit_area_{i}")
                    c1, c2 = st.columns([1, 1])
                    if c1.button("✅ حفظ", key=f"save_{i}"):
                        st.session_state.messages[i]["content"] = new_text
                        st.session_state.messages = st.session_state.messages[:i+1]
                        st.session_state.edit_index = None
                        st.session_state.trigger_generation = True 
                        st.rerun()
                    if c2.button("❌ إلغاء", key=f"cancel_{i}"):
                        st.session_state.edit_index = None
                        st.rerun()
            else:
                with st.chat_message(role, avatar=avatar):
                    if role == "user": st.markdown('<div class="user-marker"></div>', unsafe_allow_html=True)
                    else: st.markdown('<div class="assistant-marker"></div>', unsafe_allow_html=True)
                    
                    if message.get("image"):
                        st.image(message["image"], width=300)
                    st.markdown(message["content"])
                
                if role == "user" and i == last_user_index:
                    c1, c2, c3 = st.columns([0.05, 0.05, 0.9])
                    with c1:
                        st.markdown('<div class="tiny-btn">', unsafe_allow_html=True)
                        if st.button("❌", key=f"del_{i}"):
                            msg_to_del = st.session_state.messages[i]
                            if "db_id" in msg_to_del:
                                db_handler.delete_message(msg_to_del["db_id"])
                            st.session_state.messages = st.session_state.messages[:i]
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown('<div class="tiny-btn">', unsafe_allow_html=True)
                        if st.button("✏️", key=f"edit_btn_{i}"):
                            st.session_state.edit_index = i
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

        # --- منطقة الإدخال ---
        with st.popover("📎", use_container_width=False):
            st.caption("📂 رفع ملفات المشروع")
            uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"], key="chat_uploader")

        if 'trigger_generation' not in st.session_state:
            st.session_state.trigger_generation = False

        prompt = st.chat_input("سولفلي عن مشروعك...")

        if prompt:
            with st.chat_message("user", avatar="👷‍♀️"):
                st.markdown('<div class="user-marker"></div>', unsafe_allow_html=True)
                if uploaded_file: st.image(uploaded_file, width=300)
                st.markdown(prompt)
            
            image_url = None
            if uploaded_file:
                with st.spinner("جاري رفع المخطط للسحابة..."):
                    up_res = db_handler.upload_image(uploaded_file)
                    if "success" in up_res:
                        image_url = up_res["url"]
                    else:
                        st.error(f"⚠️ فشل رفع الصورة: {up_res.get('error')}")
            
            st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_file})
            
            if 'id' in st.session_state.project_data:
                current_pid = st.session_state.project_data['id']
                db_handler.save_message(current_pid, "user", prompt, image_url) 
            
            st.session_state.trigger_generation = True

        if st.session_state.trigger_generation:
            last_msg = st.session_state.messages[-1]
            with st.chat_message("assistant", avatar="👩‍💼"):
                st.markdown('<div class="assistant-marker"></div>', unsafe_allow_html=True)
                ph = st.empty()
                full_res = ""
                with st.status("Analyzing...", expanded=False) as status:
                    try:
                        current_pid = st.session_state.project_data['id']
                        memory_txt = db_handler.get_project_summary(current_pid)

                        res_stream = core_logic.stream_response(
                            last_msg["content"], 
                            st.session_state.messages[:-1], 
                            phases[selected_phase_key], 
                            st.session_state.project_data,
                            image_file=last_msg.get("image"),
                            summary_text=memory_txt
                        )
                        for chunk in res_stream:
                            full_res += chunk
                            ph.markdown(full_res + "▌")
                        ph.markdown(full_res)
                        status.update(label="Done", state="complete")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
           # --- منطقة معالجة الرد النهائي ---
            if full_res and full_res.strip():
                
            # 🕵️‍♂️ المحرك الذكي للأقفال (من المرحلة 1 إلى 8)
                for phase_num in range(1, 9):
                    unlock_key = f"[UNLOCK_PHASE_{phase_num}]"
                    
                    if unlock_key in full_res:
                        # 1. تنظيف النص لكي لا يرى الطالب الكود البرمجي
                        full_res = full_res.replace(unlock_key, "")
                        
                        # 2. تحديث قاعدة البيانات (سوبابيس) لضمان عدم ضياع الإنجاز
                        if 'id' in st.session_state.project_data:
                            current_pid = st.session_state.project_data['id']
                            db_handler.update_project_phase(current_pid, phase_num)
                        
                        # 3. تحديث الجلسة الحالية لفتح الزر فوراً
                        st.session_state.project_data['unlocked_phase'] = phase_num
                        
                        # 4. رسالة تشجيعية تظهر لإسراء
                        phase_display_name = list(phases.keys())[phase_num]
                        st.toast(f"🔓 مبروك! آيلا فتحت لكِ: {phase_display_name}", icon="✨")
                        break # نخرج من اللوب بمجرد إيجاد المفتاح

                # 2. الكود القديم: حفظ وعرض الرسالة (بعد التنظيف) 💾
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
                if 'id' in st.session_state.project_data:
                    current_pid = st.session_state.project_data['id']
                    db_handler.save_message(current_pid, "assistant", full_res)
            
            elif not full_res:
                st.warning("⚠️ لم يتم استلام رد من النموذج.")
            
            # إنهاء التوليد وإعادة التشغيل
            st.session_state.trigger_generation = False

            st.rerun()








