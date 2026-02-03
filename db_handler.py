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
    return {"error": "عذراً، التسجيل مغلق حالياً. يرجى مراجعة الإدارة."}

def login_user(email, password):
    """
    تسجيل الدخول مع تنظيف المدخلات (Safety Net)
    """
    # 1. تنظيف المدخلات مرة أخرى هنا للأمان (Lower case & Strip)
    clean_email = email.lower().strip()
    
    # 2. التحقق من القائمة البيضاء
    if clean_email not in ALLOWED_EMAILS:
        return {"error": "هذا الحساب غير مصرح له بالدخول للنظام."}

    try:
        # 3. محاولة تسجيل الدخول
        auth_response = supabase.auth.sign_in_with_password({
            "email": clean_email,
            "password": password
        })
        
        user = auth_response.user
        
        if not user:
             return {"error": "بيانات الدخول غير صحيحة"}

        # 4. جلب بيانات البروفايل
        data = supabase.table("profiles").select("*").eq("id", user.id).execute()
        
        profile = {}
        if data.data:
            profile = data.data[0]

        return {"success": True, "user": user, "profile": profile}

    except Exception as e:
        # رسالة خطأ أوضح
        return {"error": f"فشل الدخول: {str(e)}"}

def logout_user():
    try:
        supabase.auth.sign_out()
    except:
        pass

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