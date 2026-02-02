import os
import uuid # نحتاجها لتسمية الملفات بأسماء فريدة
from supabase import create_client, Client
from dotenv import load_dotenv

# تحميل المفاتيح
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠️ Supabase credentials not found in .env")

# إنشاء الاتصال (Singleton)
supabase: Client = create_client(url, key)

# ==========================================
# 🔐 Authentication Functions
# ==========================================

def signup_user(email, password, real_name, nickname):
    try:
        # 1. إنشاء الحساب في Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "real_name": real_name,
                    "nickname": nickname
                }
            }
        })
        
        user = auth_response.user
        
        if not user:
            return {"error": "فشل إنشاء المستخدم"}

        # 2. تخزين البيانات الإضافية في جدول profiles
        profile_data = {
            "id": user.id,
            "email": email,
            "real_name": real_name,
            "nickname": nickname
        }
        
        supabase.table("profiles").insert(profile_data).execute()
        
        return {"success": True, "user": user}

    except Exception as e:
        return {"error": str(e)}

def login_user(email, password):
    """
    تسجيل الدخول وجلب بيانات البروفايل
    """
    try:
        # 1. تسجيل الدخول
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        user = auth_response.user
        
        # 2. جلب بيانات البروفايل (الاسم الحقيقي واللقب)
        data = supabase.table("profiles").select("*").eq("id", user.id).execute()
        
        if data.data:
            profile = data.data[0]
            return {"success": True, "user": user, "profile": profile}
        else:
            return {"success": True, "user": user, "profile": {}} # حالة نادرة: يوزر بدون بروفايل

    except Exception as e:
        return {"error": str(e)}

def logout_user():
    supabase.auth.sign_out()

# ==========================================
# 📂 Project Management Functions
# ==========================================

def create_project(user_id, name, p_type, site, reqs):
    """
    إنشاء مشروع جديد وربطه بالمستخدم
    """
    try:
        response = supabase.table("projects").insert({
            "user_id": user_id,
            "name": name,
            "project_type": p_type,
            "site_context": site,
            "requirements": reqs,
            "current_phase": "Phase 1"
        }).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": str(e)}

def get_user_projects(user_id):
    """
    جلب كافة مشاريع المستخدم الحالي
    """
    try:
        response = supabase.table("projects").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 💬 Chat Persistence Functions
# ==========================================

def save_message(project_id, role, content, image_url=None):
    """
    حفظ رسالة جديدة في الداتا بيس
    """
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
    """
    جلب تاريخ المحادثة مرتباً زمنياً
    """
    try:
        response = supabase.table("chat_messages").select("*")\
            .eq("project_id", project_id)\
            .order("created_at", desc=False)\
            .execute()
        
        # تحويل البيانات لصيغة يفهمها Streamlit
        formatted_messages = []
        for msg in response.data:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "image": msg.get("image_url"), # ملاحظة: حالياً لا نعالج الصور
                "db_id": msg["id"] # نحتاج الـ ID للحذف لاحقاً
            })
        return formatted_messages
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

def delete_message(msg_db_id):
    """
    حذف رسالة محددة من الداتا بيس
    """
    try:
        supabase.table("chat_messages").delete().eq("id", msg_db_id).execute()
    except Exception as e:
        print(f"Error deleting message: {e}")

def get_active_user():
    """
    تحقق إذا كان هناك مستخدم مسجل دخول حالياً في Supabase
    """
    try:
        session = supabase.auth.get_session()
        if session:
            return session.user
        return None
    except:
        return None
    
def get_project_by_id(project_id):
    """
    جلب بيانات مشروع واحد فقط بواسطة الـ ID
    """
    try:
        response = supabase.table("projects").select("*").eq("id", project_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching project: {e}")
        return None
    
# ==========================================
# 📂 Storage Functions (Uploads)
# ==========================================

def upload_image(file_obj):
    """
    رفع صورة إلى Supabase Storage وإرجاع الرابط العام
    """
    try:
        # 1. توليد اسم فريد للصورة (لتجنب تشابه الأسماء)
        file_ext = file_obj.name.split('.')[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        bucket_name = "chat-images"

        # 2. قراءة البيانات من الملف (Streamlit UploadedFile)
        file_bytes = file_obj.getvalue()

        # 3. الرفع للسيرفر
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file_obj.type}
        )

        # 4. الحصول على الرابط العام (Public URL)
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        
        return {"success": True, "url": public_url}

    except Exception as e:
        return {"error": str(e)}