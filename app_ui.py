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

# تعريف المراحل (تم تحديث الأسماء لتعكس الحالة)
phases = {
    "0️⃣ محادثة عامة (General Chat)": "0️⃣ General Chat & Setup",
    "1️⃣ تحليل الموقع (Site Analysis)": "1️⃣ Site & Research (Active)",
    "2️⃣ الفكرة والتوزيع (Concept & Zoning) 🔒": "2️⃣ Concept & Zoning",
    # 👇👇 هنا التغيير: إضافة (قيد التطوير) للنص الظاهر 👇👇
    "3️⃣ السكيتشات (Sketches) 🚧 (قيد التطوير)": "3️⃣ Sketches & Freehand (Locked)",
    "4️⃣ المخططات (2D Plans) 🚧 (قيد التطوير)": "4️⃣ 2D Drafting / Plans (Locked)",
    "5️⃣ المودل (3D Modeling) 🚧 (قيد التطوير)": "5️⃣ 3D Modeling (Locked)",
    "6️⃣ الإظهار المعماري (Visualization) 🚧 (قيد التطوير)": "6️⃣ Visualization (Locked)",
    "7️⃣ الماكيت (Physical Model) 🚧 (قيد التطوير)": "7️⃣ Physical Model (Locked)",
    "8️⃣ التحكيم والتسليم (Jury & Submission) 🚧 (قيد التطوير)": "8️⃣ Jury & Marketing (Locked)"
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
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
            transition: 0.3s;
        }
        .stButton button:hover {
            border-color: #fca311;
            color: #fca311;
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
                submitted = st.form_submit_button("تسجيل الدخول 🔐", use_container_width=True)
                
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

    # الهيدر (الترحيب الملكي)
    col_h, col_l = st.columns([4, 1.2])
    with col_h:
        st.markdown(f"<h1 style='color: #fca311; margin:0;'>أهلاً بكِ في المرسم.. 👋</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ccc; font-size: 1.2rem;'>المعمارية: <b>{profile.get('user_real_name', 'إسراء')}</b></p>", unsafe_allow_html=True)
    with col_l:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", key="logout_top", type="primary", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear()
            db_handler.logout_user()
            st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
  
    # جلب المشاريع من قاعدة البيانات
    with st.spinner("جاري جلب المخططات من الأرشيف..."):
        response = db_handler.get_user_projects(user.id)
        
    if "error" in response:
        st.error(f"حدث خطأ: {response['error']}")
    else:
        projects = response.get("data", [])
        if not projects:
            st.info("المرسم فارغ حالياً.. ابدأي مشروعكِ الأول بالأسفل! ✨")
        else:
            # --- 2. محرك الرسم الذكي (The Intelligent Loop) ---
            # قاموس الأيقونات المعمارية حسب النوع
            type_icons = {
                "Sakkany (Residential)": "🏠",
                "Cultural/Public": "🏛️",
                "Commercial": "🏢", # 👈 ناطحة السحاب التي طلبتها
                "Landscape": "🌳",
                "Urban Design": "🏙️"
            }

            for p in projects:
                # اختيار الأيقونة بناءً على نوع المشروع القادم من الداتا بيس
                current_icon = type_icons.get(p['project_type'], "📐")
                
                # أ) صب معلومات المشروع داخل قالب الـ HTML الفخم
                st.markdown(f"""
                    <div class="project-card">
                        <div style="display: flex; align-items: center; justify-content: flex-end; direction: rtl;">
                            <div class="icon-box">{current_icon}</div>
                            <div style="flex-grow: 1; text-align: right;">
                                <h3 class="p-name">{p['name']}</h3>
                                <div class="p-meta">
                                    <span>TYPE: {p['project_type']}</span> | 
                                    <span>CREATED: {p['created_at'][:10]}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # ب) رسم أزرار التحكم (برمجياً) تحت كل بطاقة
                c1, c2, _ = st.columns([1.2, 1, 3])
                with c1:
                    if st.button(f"فتح المشروع 🔓", key=f"open_{p['id']}", use_container_width=True):
                        st.query_params["pid"] = p['id']
                        st.session_state.project_data.update({
                            "id": p['id'], "name": p['name'], "type": p['project_type'],
                            "site": p['site_context'], "requirements": p['requirements']
                        })
                        st.session_state.messages = db_handler.get_project_messages(p['id'])
                        st.session_state.app_stage = 'main_chat'
                        st.rerun()
                with c2:
                    with st.popover("حذف 🗑️", use_container_width=True):
                        st.caption("هل أنتِ متأكدة؟ لا يمكن التراجع.")
                        if st.button("نعم، حذف نهائي", key=f"del_{p['id']}", type="primary", use_container_width=True):
                            db_handler.delete_project_permanently(p['id'])
                            st.rerun()
                
                st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    # زر إضافة مشروع جديد
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ إضافة مشروع جديد للمرسم", use_container_width=True):
        st.session_state.app_stage = 'project_form'
        st.rerun()

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
        st.caption("هذه البيانات سيتم حقنها في عقل النموذج.")
        with st.form("project_setup_form"):
            p_name = st.text_input("اسم المشروع:", placeholder="مثال: مركز ثقافي...")
            p_type = st.selectbox("نوع المشروع:", ["Sakkany (Residential)", "Cultural/Public", "Commercial", "Landscape", "Urban Design"])
            p_site = st.text_area("تفاصيل الموقع (Site Context):")
            p_req = st.text_area("أهم المتطلبات (Program):")
            submitted = st.form_submit_button("🚀 حفظ وبدء الرحلة")
            if submitted:
                if p_name and p_req:
                    with st.spinner("جاري أرشفة المشروع في السحابة..."):
                        user_id = st.session_state.user.id
                        result = db_handler.create_project(user_id, p_name, p_type, p_site, p_req)
                    
                    if "success" in result:
                        st.success("تم الحفظ بنجاح!")
                        new_project = result['data'][0]
                        current_real_name = st.session_state.project_data.get('user_real_name')
                        current_nickname = st.session_state.project_data.get('user_nickname')

                        st.session_state.project_data = {
                            "user_real_name": current_real_name,
                            "user_nickname": current_nickname,
                            "id": new_project['id'],
                            "name": new_project['name'],
                            "type": new_project['project_type'],
                            "site": new_project['site_context'],
                            "requirements": new_project['requirements']
                        }
                        time.sleep(1)
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
        st.title("🏛️ AylaArc")
        st.caption("Your Architectural Companion Soulmate")
        
        # --- 1. زر الرجوع للقائمة الرئيسية ---
        if st.button("🔙 العودة للمشاريع", use_container_width=True):
            st.session_state.app_stage = 'project_landing'
            st.session_state.messages = [] 
            st.rerun()
            
        st.markdown("---")
        
        # اختيار المرحلة
        selected_phase_key = st.selectbox("اختر مرحلة المشروع:", list(phases.keys()), index=0)
        
        st.markdown("---")
        
        # --- 2. زر محادثة جديدة (النسخة الآمنة مع الأرشيف) 🛡️ ---
        if st.button("✨ محادثة جديدة (أرشفة + تخفيف)", help="يحفظ المحادثة الحالية في الأرشيف، يلخصها للذاكرة، ثم يفرغ الشات.", use_container_width=True):
            
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
        with st.expander("🗑️ منطقة الخطر"):
            st.warning("حذف المشروع نهائياً")
            if st.button("تأكيد الحذف", type="primary", use_container_width=True):
                pid = st.session_state.project_data['id']
                db_handler.delete_project_permanently(pid)
                st.session_state.app_stage = 'project_landing'
                st.rerun()

        if st.button("🚪 تسجيل خروج", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear() 
            db_handler.logout_user()
            st.rerun()

    p_data = st.session_state.get('project_data', {})
    project_title = p_data.get('name', 'New Project')
    
    st.title(f"🏛️ {project_title}")
    st.caption(f"Project Type: {p_data.get('type')} | Phase: {phases[selected_phase_key]}")

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
        # --- (Active Mode) عرض الشات الطبيعي ---
        if not st.session_state.messages:
            real_name = p_data.get('user_real_name', 'إسراء')
            nickname = p_data.get('user_nickname', 'سيرو')
            
            # نجلب الملخص إن وجد لنشعر المستخدم بالاستمرارية رغم الصفحة البيضاء
            current_pid = st.session_state.project_data['id']
            existing_summary = db_handler.get_project_summary(current_pid)
            
            if existing_summary:
                welcome_msg = f"أهلاً {real_name}.. فتحنا صفحة جديدة نظيفة ✨.\nأنا راجعت ذاكرتي ومستحضرة تفاصيل المشروع (الموقع، المتطلبات، والقرارات السابقة). كملي، شنو الخطوة الجاية؟"
            else:
                welcome_msg = f"أهلاً يا زميلتي العزيزة {real_name} (أو مثل ما تحبين أسميج: {nickname})! 👷‍♀️\n\nتم استيعاب مشروع **{project_title}** بنجاح.\nإحنا حالياً بـ **{phases[selected_phase_key]}**. جاهز أشوف شغلك (صور/مخططات) أو نتناقش."
            
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

        # --- عرض الرسائل ---
        user_indices = [i for i, m in enumerate(st.session_state.messages) if m['role'] == 'user']
        last_user_index = user_indices[-1] if user_indices else -1

        for i, message in enumerate(st.session_state.messages):
            role = message["role"]
            avatar = "👷‍♀️" if role == "user" else "👩‍💼"
            
            if st.session_state.edit_index == i:
                with st.container(border=True):
                    st.caption("✏️ تعديل الرسالة:")
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
                        if st.button("🗑️", key=f"del_{i}"):
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
            
            if full_res and full_res.strip():
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                if 'id' in st.session_state.project_data:
                    current_pid = st.session_state.project_data['id']
                    db_handler.save_message(current_pid, "assistant", full_res)
            
            elif not full_res:
                st.warning("⚠️ لم يتم استلام رد من النموذج.")
            
            st.session_state.trigger_generation = False
            st.rerun()