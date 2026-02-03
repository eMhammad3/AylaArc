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

# 2. تهيئة الذاكرة والمراحل (النسخة الآمنة)
if 'app_stage' not in st.session_state:
    active_user = None 
    
    if 'user' in st.session_state:
        active_user = st.session_state.user

    if active_user:
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
    "2️⃣ الفكرة والتوزيع (Concept & Zoning) 🔒": "2️⃣ Concept & Zoning", # لاحظ علامة القفل
    "3️⃣ السكيتشات (Sketches) 🚧": "3️⃣ Sketches & Freehand (Locked)",
    "4️⃣ المخططات (2D Plans) 🚧": "4️⃣ 2D Drafting / Plans (Locked)",
    "5️⃣ المودل (3D Modeling) 🚧": "5️⃣ 3D Modeling (Locked)",
    "6️⃣ الإظهار المعماري (Visualization) 🚧": "6️⃣ Visualization (Locked)",
    "7️⃣ الماكيت (Physical Model) 🚧": "7️⃣ Physical Model (Locked)",
    "8️⃣ التحكيم والتسليم (Jury & Submission) 🚧": "8️⃣ Jury & Marketing (Locked)"
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
           5. الشات والرسائل
           ========================================= */
        div[data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
        }
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
        div[data-testid="stChatMessage"]:has(.assistant-marker) div[data-testid="stChatMessageContent"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255,255,255,0.05);
            color: #e0e0e0;
            border-radius: 5px 20px 20px 20px !important;
            padding: 15px !important;
            text-align: right;
            direction: rtl;
        }
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
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 👤 المرحلة الأولى: الملف الشخصي
# =============================================================================
if st.session_state.app_stage == 'profile':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 1px solid #333; text-align: center;'>
                <h2 style='color: #fca311; margin: 0;'>👤 Ayla Arc Login</h2>
            </div>
            <br>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["تسجيل دخول", "إنشاء حساب جديد"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني:", key="login_email")
                password = st.text_input("كلمة المرور:", type="password", key="login_pass")
                submitted = st.form_submit_button("تسجيل الدخول 🔐")
                
                if submitted:
                    if email and password:
                        with st.spinner("جاري الاتصال بالسيرفر..."):
                            result = db_handler.login_user(email, password)
                            if "success" in result:
                                st.success("تم تسجيل الدخول بنجاح!")
                                st.session_state.user = result["user"]
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

        with tab2:
            new_name = st.text_input("الاسم الحقيقي:", placeholder="مثال: إسراء أحمد")
            new_nick = st.text_input("اللقب المفضل:", placeholder="مثال: سيرو")
            new_email = st.text_input("البريد الإلكتروني:", key="signup_email")
            new_pass = st.text_input("كلمة المرور:", type="password", key="signup_pass")
            
            if st.button("إنشاء حساب 🆕"):
                if new_email and new_pass and new_name:
                    with st.spinner("جاري إنشاء المستخدم..."):
                        result = db_handler.signup_user(new_email, new_pass, new_name, new_nick)
                        if "success" in result:
                            st.success("تم إنشاء الحساب! سجل دخولك الآن.")
                        else:
                            st.error(f"خطأ: {result.get('error')}")
                else:
                    st.warning("يرجى ملء جميع البيانات.")

# =============================================================================
# 🏛️ المرحلة الثانية: لوحة المشاريع
# =============================================================================
elif st.session_state.app_stage == 'project_landing':
    user = st.session_state.get('user')
    profile = st.session_state.get('project_data', {}) 

    st.markdown(f"""
        <h1 style='text-align: right; color: #fca311;'>مرحباً المعمارية {profile.get('user_real_name', 'إسراء')} 👋</h1>
        <p style='text-align: right; color: #888;'>إليك مشاريعك المحفوظة في الأرشيف:</p>
        <hr style='border-color: #333;'>
    """, unsafe_allow_html=True)

    with st.spinner("جاري استدعاء المخططات..."):
        response = db_handler.get_user_projects(user.id)
        
    if "error" in response:
        st.error(f"حدث خطأ في الاتصال: {response['error']}")
    else:
        projects = response.get("data", [])
        if not projects:
            st.info("لا توجد مشاريع حتى الآن. ابدأي رحلتك الأولى! 👇")
        else:
            for p in projects:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.subheader(f"📂 {p['name']}")
                        st.caption(f"Type: {p['project_type']} | Date: {p['created_at'][:10]}")
                    with c2:
                        if st.button("فتح 🔓", key=f"open_{p['id']}", use_container_width=True):
                            st.query_params["pid"] = p['id']
                            st.session_state.project_data = {
                                "user_real_name": profile.get('user_real_name'),
                                "user_nickname": profile.get('user_nickname'),
                                "id": p['id'],
                                "name": p['name'],
                                "type": p['project_type'],
                                "site": p['site_context'],
                                "requirements": p['requirements']
                            }
                            with st.spinner("استرجاع ذكريات المشروع..."):
                                history = db_handler.get_project_messages(p['id'])
                                st.session_state.messages = history
                                st.session_state.app_stage = 'main_chat'
                            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ مشروع جديد (New Project)", use_container_width=True):
        st.session_state.app_stage = 'project_form'
        st.rerun()

# =============================================================================
# 📝 المرحلة الثالثة: فورم بيانات المشروع
# =============================================================================
elif st.session_state.app_stage == 'project_form':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
        st.caption("Architectural Studio Companion")
        st.markdown("---")
        
        # اختيار المرحلة (القائمة المحدثة)
        selected_phase_key = st.selectbox("اختر مرحلة المشروع:", list(phases.keys()), index=0)
        
        st.markdown("---")
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل خروج (Logout)", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    p_data = st.session_state.get('project_data', {})
    project_title = p_data.get('name', 'New Project')
    
    st.title(f"🏛️ {project_title}")
    st.caption(f"Project Type: {p_data.get('type')} | Phase: {phases[selected_phase_key]}")

    # ==================================================
    # 🕵️‍♂️ منطق الأقفال (The Guard System)
    # ==================================================
    
    # تحديد نوع المرحلة الحالية بناءً على الاختيار
    is_active_phase = False
    is_locked_phase = False
    is_dev_phase = False

    # المرحلتين 0 و 1 مفتوحات دائماً
    if selected_phase_key.startswith("0️⃣") or selected_phase_key.startswith("1️⃣"):
        is_active_phase = True
    
    # المرحلة 2 (مقفلة إلا إذا تم فتحها)
    elif selected_phase_key.startswith("2️⃣"):
        if st.session_state.phase2_unlocked:
            is_active_phase = True
        else:
            is_locked_phase = True
            
    # بقية المراحل (قيد التطوير)
    else:
        is_dev_phase = True

    # ==================================================
    # 📺 العرض بناءً على الحالة (View Controller)
    # ==================================================

    if is_locked_phase:
        # --- عرض القفل للمرحلة الثانية ---
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
            # زر المخاطرة
            if st.button("⚠️ أنا أتحمل المسؤولية (دخول مجازفة)", use_container_width=True, type="primary"):
                st.session_state.phase2_unlocked = True
                st.toast("تم كسر القفل! آيلا ستراقب قراراتك بدقة...", icon="👀")
                time.sleep(1.5)
                st.rerun()

    elif is_dev_phase:
        # --- عرض قيد التطوير للبقية ---
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
            welcome_msg = f"أهلاً يا زميلتي العزيزة {real_name} (أو مثل ما تحبين أسميج: {nickname})! 👷‍♀️\n\nتم استيعاب مشروع **{project_title}** بنجاح.\nإحنا حالياً بـ **{phases[selected_phase_key]}**. جاهز أشوف شغلك (صور/مخططات) أو نتناقش."
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

        # --- 1. عرض الرسائل ---
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
                
                # أزرار التعديل والحذف
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

        # --- 2. منطقة الإدخال ---
        with st.popover("📎", use_container_width=False):
            st.caption("📂 رفع ملفات المشروع")
            uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"], key="chat_uploader")

        if 'trigger_generation' not in st.session_state:
            st.session_state.trigger_generation = False

        prompt = st.chat_input("سولفلي عن مشروعك...")

        # --- 3. المعالجة ---
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
                        res_stream = core_logic.stream_response(
                            last_msg["content"], 
                            st.session_state.messages[:-1], 
                            phases[selected_phase_key], 
                            st.session_state.project_data,
                            image_file=last_msg.get("image")
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