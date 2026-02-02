import streamlit as st
import core_logic  # العقل المدبر
import time
import db_handler

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="AylaArc",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تهيئة الذاكرة والمراحل (النسخة الاحترافية: التوجيه عبر الرابط)
if 'app_stage' not in st.session_state:
    active_user = db_handler.get_active_user()
    
    if active_user:
        st.session_state.user = active_user
        
        # 🟢 فحص الرابط: هل يوجد مشروع محدد؟
        query_params = st.query_params
        pid = query_params.get("pid")
        
        if pid:
            # إذا وجدنا ID مشروع في الرابط، نحاول تحميله فوراً
            with st.spinner("جاري استعادة جلسة العمل..."):
                p = db_handler.get_project_by_id(pid)
                if p:
                    # بناء بيانات المشروع في الذاكرة
                    st.session_state.project_data = {
                        "id": p['id'],
                        "name": p['name'],
                        "type": p['project_type'],
                        "site": p['site_context'],
                        "requirements": p['requirements']
                    }
                    # تحميل المحادثات السابقة
                    st.session_state.messages = db_handler.get_project_messages(pid)
                    st.session_state.app_stage = 'main_chat'
                else:
                    st.session_state.app_stage = 'project_landing'
        else:
            st.session_state.app_stage = 'project_landing'
            
        # استرجاع بروفايل المستخدم (الاسم واللقب) في كل الأحوال
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
    st.session_state.edit_index = None  # لتتبع الرسالة المراد تعديلها

# تعريف المراحل
phases = {
    "Phase 1": "1️⃣ Site & Research (Active)",
    "Phase 2": "2️⃣ Concept & Zoning (Soon)",
    "Phase 3": "3️⃣ Sketches & Freehand (Locked)",
    "Phase 4": "4️⃣ 2D Drafting / Plans (Locked)",
    "Phase 5": "5️⃣ 3D Modeling (Locked)",
    "Phase 6": "6️⃣ Visualization (Locked)",
    "Phase 7": "7️⃣ Physical Model (Locked)",
    "Phase 8": "8️⃣ Jury & Marketing (Locked)"
}

# 3. الستايل (CSS) - النسخة الاحترافية (Glassmorphism & Neon)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');
        
        /* 1. الخلفية العامة (الفخامة الأصلية محفوظة) */
        .stApp {
            background: radial-gradient(circle at 10% 20%, #1a1a1a 0%, #000000 90%);
            font-family: 'Tajawal', sans-serif;
        }

        /* 2. النصوص والاتجاهات */
        [data-testid="stAppViewContainer"] { direction: ltr !important; }
        h1, h2, h3, h4, .stCaption, p, div, label, .stTextInput, .stTextArea {
            direction: rtl;
            text-align: right;
        }

        /* 3. العناوين (الذهب والأبيض محفوظ) */
        h1 {
            background: -webkit-linear-gradient(45deg, #fca311, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            padding-bottom: 10px;
        }

        /* 4. البطاقات الزجاجية (التاثير الزجاجي محفوظ) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(10px);
            border-radius: 16px !important;
            padding: 20px !important;
            transition: all 0.3s ease;
        }

        /* 5. فقاعات الشات (تم تحرير العرض لتأخذ راحتها 100%) */
        div[data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px !important;
            padding: 15px !important;
            /* التعديل الجوهري: إزالة قيود العرض */
            width: 100% !important; 
            max-width: 100% !important;
        }
        div[data-testid="stChatMessage"]:has(.user-marker) {
            background: linear-gradient(135deg, #0095F6 0%, #005c99 100%) !important;
            border: none !important;
        }

        /* 6. شريط الكتابة (Floating & Default) */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
        }
        [data-testid="stChatInput"] textarea {
            background-color: #1a1a1a !important;
            border: 1px solid #333 !important;
            border-radius: 25px !important;
        }

        /* 7. إعادة ترسيت الدبوس (إزالة الـ Fixed والـ 491px) */
        [data-testid="stPopover"] {
            position: relative !important;
            width: auto !important;
            bottom: auto !important;
            left: auto !important;
        }
        [data-testid="stPopover"] > button {
            background-color: #1a1a1a !important;
            border: 1px solid #333 !important;
            color: #fca311 !important;
            border-radius: 50% !important;
            width: 45px !important; height: 45px !important;
        }

        /* 8. ستايل القائمة الجانبية الفخم (المحفوظ بالكامل) */
        section[data-testid="stSidebar"] {
            background-color: #0a0a0a !important;
            border-left: 1px solid #333;
        }
        section[data-testid="stSidebar"] .stButton button {
            background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%) !important;
            border: 1px solid #444 !important;
            color: #ccc !important;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background: linear-gradient(135deg, #fca311 0%, #d48806 100%) !important;
            color: #000 !important;
            box-shadow: 0 4px 15px rgba(252, 163, 17, 0.4) !important;
        }

        /* إخفاء الزوائد */
        .user-marker, .assistant-marker { display: none; }
        header, footer { visibility: hidden; }

        /* تعديلات الموبايل الذكية */
        @media only screen and (max-width: 768px) {
            .block-container { padding: 1rem !important; }
            h1 { font-size: 1.8rem !important; }
        }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 👤 المرحلة الأولى: الملف الشخصي (Real Auth)
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
        
        # تبويبات (دخول / تسجيل جديد)
        tab1, tab2 = st.tabs(["تسجيل دخول", "إنشاء حساب جديد"])
        
        # --- LOGIN (تم التعديل لإستخدام Form لضمان وصول البيانات) ---
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

        # --- SIGN UP ---
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
                            st.success("تم إنشاء الحساب! يرجى التحقق من بريدك الإلكتروني لتأكيد الحساب (إذا كان مطلوباً) أو سجل الدخول الآن.")
                        else:
                            st.error(f"خطأ: {result.get('error')}")
                else:
                    st.warning("يرجى ملء جميع البيانات.")

# =============================================================================
# 🏛️ المرحلة الثانية: لوحة المشاريع (Dashboard) - متصلة بالداتا بيس
# =============================================================================
elif st.session_state.app_stage == 'project_landing':
    # 1. جلب بيانات المستخدم
    user = st.session_state.get('user')
    profile = st.session_state.get('project_data', {}) 

    # 2. ترويسة فخمة
    st.markdown(f"""
        <h1 style='text-align: right; color: #fca311;'>مرحباً المعمارية {profile.get('user_real_name', 'إسراء')} 👋</h1>
        <p style='text-align: right; color: #888;'>إليك مشاريعك المحفوظة في الأرشيف:</p>
        <hr style='border-color: #333;'>
    """, unsafe_allow_html=True)

    # 3. جلب المشاريع من السيرفر
    with st.spinner("جاري استدعاء المخططات..."):
        response = db_handler.get_user_projects(user.id)
        
    if "error" in response:
        st.error(f"حدث خطأ في الاتصال: {response['error']}")
    else:
        projects = response.get("data", [])
        
        # 4. عرض المشاريع كـ بطاقات (Cards)
        # 4. عرض المشاريع (تصميم جديد)
        if not projects:
            st.info("لا توجد مشاريع حتى الآن. ابدأي رحلتك الأولى! 👇")
        else:
            # عرض كل مشروع
            for p in projects:
                # الـ CSS الجديد سيحول هذا الكونتينر إلى زجاج
                with st.container(border=True):
                    c1, c2 = st.columns([0.85, 0.15])
                    with c1:
                        # العنوان بخط عريض
                        st.markdown(f"### 📂 {p['name']}")
                        # وصف وتاريخ بتنسيق HTML صغير وأنيق
                        st.markdown(f"""
                        <div style='display: flex; gap: 15px; margin-top: -10px;'>
                            <span style='background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 20px; font-size: 0.8em; color: #ccc;'>
                                🏗️ {p['project_type']}
                            </span>
                            <span style='background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 20px; font-size: 0.8em; color: #ccc;'>
                                📅 {p['created_at'][:10]}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🚀", key=f"open_{p['id']}", help="فتح المشروع"):
                            # 🟢 منطق الفتح (نفس القديم)
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
                            with st.spinner("🚀 الانطلاق..."):
                                history = db_handler.get_project_messages(p['id'])
                                st.session_state.messages = history
                            st.session_state.app_stage = 'main_chat'
                            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    # 5. زر إنشاء مشروع جديد
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
                    # 1. الاتصال بالسيرفر للحفظ
                    with st.spinner("جاري أرشفة المشروع في السحابة..."):
                        user_id = st.session_state.user.id
                        result = db_handler.create_project(user_id, p_name, p_type, p_site, p_req)
                    
                    if "success" in result:
                        st.success("تم الحفظ بنجاح!")
                        # 2. تحديث بيانات الجلسة بالبيانات الراجعة من الداتا بيس
                        # (Supabase يرجع قائمة، نأخذ العنصر الأول)
                        new_project = result['data'][0]
                        
                        # نحافظ على اسم المستخدم واللقب
                        current_real_name = st.session_state.project_data.get('user_real_name')
                        current_nickname = st.session_state.project_data.get('user_nickname')

                        st.session_state.project_data = {
                            "user_real_name": current_real_name,
                            "user_nickname": current_nickname,
                            "id": new_project['id'], # مهم جداً للمستقبل
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
                    st.error("يرجى ملء الحقول الأساسية (الاسم والمتطلبات).")

# =============================================================================
# 💬 المرحلة الرابعة: الشات الرئيسي (Main Chat) - النسخة المحدثة
# =============================================================================
elif st.session_state.app_stage == 'main_chat':
    
    st.markdown("""<style>section[data-testid="stSidebar"] { display: block !important; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 🏛️ AylaArc")
        st.caption("رفيقة الاستوديو المعماري")
        
        st.markdown("---")
        
        # 1. زر العودة (المفقود سابقاً)
        # نستخدم أيقونة وتسمية واضحة
        if st.button("🔙 العودة للأرشيف", use_container_width=True):
            st.session_state.app_stage = 'project_landing'
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. القوائم
        selected_phase_key = st.selectbox("📌 مرحلة المشروع:", list(phases.keys()), index=0)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # 3. زر "مشروع جديد" الفخم
        # غيرنا النص والوجهة ليذهب لصفحة إنشاء المشروع
        if st.button("✨ فتح مشروع جديد", key="gold_btn", use_container_width=True):
            st.session_state.app_stage = 'project_form'
            st.rerun()
            
        st.markdown("---")
        # زر تسجيل الخروج (اختياري بالأسفل)
        if st.button("🔒 تسجيل خروج", use_container_width=True):
             st.session_state.user = None
             st.session_state.app_stage = 'profile'
             st.rerun()

    p_data = st.session_state.get('project_data', {})
    project_title = p_data.get('name', 'New Project')
    
    st.title(f"🏛️ {project_title}")
    st.caption(f"Project Type: {p_data.get('type')} | Phase: {phases[selected_phase_key]}")

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
        avatar = "👷‍♀️" if role == "user" else "🏛️"
        
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
            
            # عرض الأزرار لآخر رسالة مستخدم فقط
            if role == "user" and i == last_user_index:
                c1, c2, c3 = st.columns([0.05, 0.05, 0.9])
                
                # تم إصلاح المسافات هنا
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
    # --- 3. المعالجة والحفظ (مع دعم الصور السحابية) ---
    if prompt:
        # عرض رسالة المستخدم فوراً
        with st.chat_message("user", avatar="👷‍♀️"):
            st.markdown('<div class="user-marker"></div>', unsafe_allow_html=True)
            if uploaded_file: st.image(uploaded_file, width=300)
            st.markdown(prompt)
        
        # 1. رفع الصورة للسيرفر (إن وجدت)
        image_url = None
        if uploaded_file:
            with st.spinner("جاري رفع المخطط للسحابة..."):
                up_res = db_handler.upload_image(uploaded_file)
                if "success" in up_res:
                    image_url = up_res["url"]
                else:
                    st.error(f"⚠️ فشل رفع الصورة: {up_res.get('error')}")
        
        # 2. الحفظ المحلي (نحتفظ بالملف الأصلي للسرعة في الجلسة الحالية)
        st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_file})
        
        # 3. الحفظ السحابي (نحفظ الرابط الدائم بدلاً من الملف)
        if 'id' in st.session_state.project_data:
            current_pid = st.session_state.project_data['id']
            # نمرر رابط الصورة (image_url) ليتم تخزينه في الجدول
            db_handler.save_message(current_pid, "user", prompt, image_url) 
        
        st.session_state.trigger_generation = True

    if st.session_state.trigger_generation:
        last_msg = st.session_state.messages[-1]
        with st.chat_message("assistant", avatar="🏛️"):
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
        
        # 👇 التعديل الهندسي: نتأكد أن الرد ليس فارغاً قبل الحفظ
        if full_res and full_res.strip():
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            if 'id' in st.session_state.project_data:
                current_pid = st.session_state.project_data['id']
                db_handler.save_message(current_pid, "assistant", full_res)
        else:
            # إذا كان الرد فارغاً (بسبب خطأ ما)، لا نحفظ شيئاً وننبه المستخدم
            st.warning("⚠️ لم يتم استلام رد من النموذج. حاول مرة أخرى.")
        
        st.session_state.trigger_generation = False
        st.rerun()
        
        # حفظ رد الـ AI
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        if 'id' in st.session_state.project_data:
            current_pid = st.session_state.project_data['id']
            db_handler.save_message(current_pid, "assistant", full_res)
        
        st.session_state.trigger_generation = False
        st.rerun()