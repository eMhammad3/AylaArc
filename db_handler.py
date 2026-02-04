import os
import uuid
from supabase import create_client, Client, ClientOptions # 👈 إضافة ClientOptions
from dotenv import load_dotenv

# تحميل المفاتيح
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠️ Supabase credentials not found in .env")

# ==========================================
# ⚙️ إعدادات العميل (الحل الجذري لمشاكل الجلسات)
# ==========================================
# نقوم بتعطيل حفظ الجلسة تلقائياً (persist_session=False)
# هذا يمنع السيرفر من تذكر المستخدم الخطأ، ويجبرنا على الاعتماد على التوكن اللحظي
opts = ClientOptions().replace(
    persist_session=False, 
    auto_refresh_token=False
)

# إنشاء الاتصال مع الإعدادات الجديدة
supabase: Client = create_client(url, key, options=opts)

# ==========================================
# 🛑 قائمة المسموح لهم (Whitelist)
# ==========================================
ALLOWED_EMAILS = [
    "emhammad3@gmail.com", 
    "partner@ayla.com"
]

# ==========================================
# 🔐 Authentication Functions
# ==========================================

def signup_user(email, password, real_name, nickname):
    """
    نسخة محصنة: تسجل المستخدم وتنشئ البروفايل بدون أخطاء تكرار
    """
    try:
        # 1. محاولة إنشاء المستخدم في Auth
        auth_res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        user = auth_res.user
        if not user:
            return {"error": "فشل إنشاء الحساب، قد يكون الحساب مسجلاً مسبقاً أو هناك مشكلة في الاتصال."}

        # 2. إنشاء أو تحديث البروفايل (UPSERT)
        # نستخدم upsert لضمان أنه إذا كان السطر موجوداً لا يظهر خطأ Duplicate Key
        supabase.table("profiles").upsert({
            "id": user.id,
            "real_name": real_name,
            "nickname": nickname
        }, on_conflict='id').execute()

        return {"success": True, "user": user}
        
    except Exception as e:
        # إذا كان الخطأ هو أن المستخدم موجود أصلاً، نعتبره نجاحاً جزئياً أو نوضح السبب
        err_msg = str(e)
        if "already registered" in err_msg.lower():
            return {"error": "هذا الحساب مسجل مسبقاً، يرجى تسجيل الدخول مباشرة."}
        return {"error": err_msg}

def login_user(email, password):
    """
    إعادة دالة تسجيل الدخول المفقودة (المسؤولة عن حل خطأ image_ff69e8.png)
    """
    clean_email = email.lower().strip()
    
    # التحقق من القائمة البيضاء (تأكد أن ALLOWED_EMAILS معرفة في أعلى الملف)
    if clean_email not in ALLOWED_EMAILS:
        return {"error": "هذا الحساب غير مصرح له بالدخول للنظام."}

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": clean_email,
            "password": password
        })
        
        user = auth_response.user
        if not user:
            return {"error": "بيانات الدخول غير صحيحة"}

        # جلب البروفايل
        data = supabase.table("profiles").select("*").eq("id", user.id).execute()
        profile = data.data[0] if data.data else {}

        return {"success": True, "user": user, "profile": profile}

    except Exception as e:
        return {"error": f"فشل الدخول: {str(e)}"}

# ==========================================
# 📂 Project Management Functions
# ==========================================

def create_project(user_id, name, p_type, site, reqs):
    try:
        response = supabase.table("projects").insert({
            "user_id": user_id,
            "name": name,
            "project_type": p_type,
            "site_context": site,
            "requirements": reqs,
            "current_phase": "Phase 1",
            "unlocked_phase": 1 
        }).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": str(e)}

def get_user_projects(user_id):
    try:
        response = supabase.table("projects").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": str(e)}

def get_project_by_id(project_id):
    try:
        response = supabase.table("projects").select("*").eq("id", project_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching project: {e}")
        return None

def update_project_phase(project_id, new_phase_level):
    try:
        supabase.table("projects").update({"unlocked_phase": new_phase_level}).eq("id", project_id).execute()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 💬 Chat Persistence Functions
# ==========================================

def save_message(project_id, role, content, image_url=None):
    try:
        data = {
            "project_id": project_id,
            "role": role,
            "content": content,
            "image_url": image_url
        }
        supabase.table("chat_messages").insert(data).execute()
    except Exception as e:
        print(f"Error saving message: {e}")

def get_project_messages(project_id):
    try:
        response = supabase.table("chat_messages").select("*")\
            .eq("project_id", project_id)\
            .order("created_at", desc=False)\
            .execute()
        
        formatted_messages = []
        for msg in response.data:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "image": msg.get("image_url"),
                "db_id": msg["id"]
            })
        return formatted_messages
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

def delete_message(msg_db_id):
    try:
        supabase.table("chat_messages").delete().eq("id", msg_db_id).execute()
    except Exception as e:
        print(f"Error deleting message: {e}")

# ==========================================
# 📂 Storage Functions (Uploads)
# ==========================================

def upload_image(file_obj):
    try:
        file_ext = file_obj.name.split('.')[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        bucket_name = "chat-images"
        file_bytes = file_obj.getvalue()

        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file_obj.type}
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return {"success": True, "url": public_url}

    except Exception as e:
        return {"error": str(e)}
    
    # ==========================================
# 🧠 AI Memory & Summarization Functions
# ==========================================

def update_project_summary(project_id, summary_text):
    """
    تحديث ملخص المشروع (الذاكرة طويلة المدى)
    """
    try:
        # نقوم بتحديث حقل summary للمشروع المحدد
        supabase.table("projects").update({"summary": summary_text}).eq("id", project_id).execute()
        return {"success": True}
    except Exception as e:
        print(f"Error updating summary: {e}")
        return {"error": str(e)}

def get_project_summary(project_id):
    """
    جلب الملخص الحالي للمشروع لحقنه في الذاكرة
    """
    try:
        # نجلب فقط حقل الـ summary
        response = supabase.table("projects").select("summary").eq("id", project_id).execute()
        if response.data and response.data[0]:
            return response.data[0].get("summary", "")
        return ""
    except Exception as e:
        print(f"Error getting summary: {e}")
        return ""
    
    # ==========================================
# 🗑️ Deletion & Cleanup Functions
# ==========================================

def clear_project_chat_history(project_id):
    """
    حذف جميع رسائل الشات لمشروع معين من قاعدة البيانات
    (يستخدم عند بدء محادثة جديدة لتخفيف الحمل)
    """
    try:
        supabase.table("chat_messages").delete().eq("project_id", project_id).execute()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def delete_project_permanently(project_id):
    """
    حذف المشروع بالكامل (مع رسائله وملخصه) من قاعدة البيانات
    """
    try:
        # 1. حذف الرسائل المرتبطة بالمشروع أولاً (للأمان)
        supabase.table("chat_messages").delete().eq("project_id", project_id).execute()
        
        # 2. حذف المشروع نفسه
        supabase.table("projects").delete().eq("id", project_id).execute()
        
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}
    
    # ==========================================
# 📜 Archiving System (History Viewer)
# ==========================================

def archive_current_chat(project_id, messages_list, summary_snapshot):
    """
    نقل المحادثة الحالية إلى جدول الأرشيف قبل حذفها
    """
    try:
        # تحويل قائمة الرسائل إلى نص مقروء
        formatted_text = ""
        for msg in messages_list:
            role = "👤 المعماري" if msg['role'] == 'user' else "👷‍♀️ آيلا"
            content = msg['content']
            if isinstance(content, list): # في حالة وجود صور
                content = "[صورة + نص]"
            formatted_text += f"{role}: {content}\n{'-'*20}\n"

        data = {
            "project_id": project_id,
            "full_conversation": formatted_text,
            "summary_snapshot": summary_snapshot
        }
        supabase.table("archives").insert(data).execute()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def get_project_archives(project_id):
    """
    جلب قائمة المحادثات المؤرشفة لهذا المشروع
    """
    try:
        response = supabase.table("archives").select("*")\
            .eq("project_id", project_id)\
            .order("created_at", desc=True)\
            .execute()
        return response.data
    except Exception as e:
        return []
    
    # تأكد أن هذا السطر يبدأ من بداية السطر تماماً (صفر فراغات)
def logout_user():
    """
    تقوم بتسجيل خروج المستخدم من نظام سوبابيس برمجياً
    """
    try:
        supabase.auth.sign_out()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}