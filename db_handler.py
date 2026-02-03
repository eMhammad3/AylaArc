import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

# تحميل المفاتيح
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠️ Supabase credentials not found in .env")

# إنشاء الاتصال
supabase: Client = create_client(url, key)

# ==========================================
# 🛑 قائمة المسموح لهم (Whitelist)
# ==========================================
# ضع هنا الإيميلات المسموح لها فقط بالدخول
ALLOWED_EMAILS = [
    "admin@ayla.com",  # غير هذا لإيميلك الحقيقي
    "partner@ayla.com" # غير هذا لإيميل شريكك
]

# ==========================================
# 🔐 Authentication Functions
# ==========================================

def signup_user(email, password, real_name, nickname):
    # تم تعطيل التسجيل لأسباب أمنية
    return {"error": "عذراً، التسجيل مغلق حالياً. يرجى مراجعة الإدارة."}

def login_user(email, password):
    """
    تسجيل الدخول مع التحقق من القائمة البيضاء وتنظيف الجلسة
    """
    # 1. التحقق من القائمة البيضاء (Security Check) 🛡️
    if email not in ALLOWED_EMAILS:
        return {"error": "هذا الحساب غير مصرح له بالدخول للنظام."}

    try:
        # 2. تنظيف أي جلسة سابقة عالقة (Fix for Ghost Login) 👻
        # هذه الخطوة تضمن أننا لا نستخدم توكن شخص آخر
        try:
            supabase.auth.sign_out()
        except:
            pass

        # 3. تسجيل الدخول
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        user = auth_response.user
        
        # 4. جلب بيانات البروفايل
        data = supabase.table("profiles").select("*").eq("id", user.id).execute()
        
        profile = {}
        if data.data:
            profile = data.data[0]

        # 5. خطوة مهمة جداً: نرجع البيانات للكود لكن لا نبقيها في المتغير العام
        # (نعتمد على session_state في الواجهة فقط)
        
        return {"success": True, "user": user, "profile": profile}

    except Exception as e:
        return {"error": str(e)}

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