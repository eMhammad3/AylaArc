import os
import uuid
from supabase import create_client, Client, ClientOptions
from dotenv import load_dotenv

# تحميل المفاتيح
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("⚠️ Supabase credentials not found in .env")

# ==========================================
# ⚙️ إعدادات العميل (تم الإصلاح هنا 🛠️)
# ==========================================
# جعلنا auto_refresh_token=True لكي لا يطردك السيرفر عند الريلود
opts = ClientOptions().replace(
    persist_session=False, 
    auto_refresh_token=True
)

# إنشاء الاتصال مع الإعدادات الجديدة
supabase: Client = create_client(url, key, options=opts)

# ==========================================
# 🛑 قائمة المسموح لهم (Whitelist)
# ==========================================
ALLOWED_EMAILS = [
    "emhammad3@gmail.com", 
    "partner@ayla.com",
    "2israa0ahmed@gmail.com" # 👈 تم إضافة إيميل إسراء لضمان الدخول
]

# ==========================================
# 🔐 Authentication Functions
# ==========================================

def signup_user(email, password, real_name, nickname):
    """
    تسجيل مستخدم جديد مع إنشاء بروفايل
    """
    try:
        # 1. إنشاء المستخدم في Auth
        auth_res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        user = auth_res.user
        if not user:
            return {"error": "فشل إنشاء الحساب، قد يكون مسجلاً مسبقاً."}

        # 2. إنشاء البروفايل (UPSERT)
        supabase.table("profiles").upsert({
            "id": user.id,
            "real_name": real_name,
            "nickname": nickname
        }, on_conflict='id').execute()

        return {"success": True, "user": user}
        
    except Exception as e:
        err_msg = str(e)
        if "already registered" in err_msg.lower():
            return {"error": "هذا الحساب مسجل مسبقاً."}
        return {"error": err_msg}

def login_user(email, password):
    """
    تسجيل الدخول العادي + إرجاع توكن التجديد
    """
    clean_email = email.lower().strip()
    
    if clean_email not in ALLOWED_EMAILS:
        # pass # أو تفعيل الحماية
        pass 

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": clean_email,
            "password": password
        })
        
        user = auth_response.user
        session = auth_response.session # 👈 نحتاج الجلسة لجلب التوكنات

        if not user or not session:
            return {"error": "بيانات الدخول غير صحيحة"}

        # جلب البروفايل
        data = supabase.table("profiles").select("*").eq("id", user.id).execute()
        profile = data.data[0] if data.data else {}

        return {
            "success": True, 
            "user": user, 
            "profile": profile,
            "access_token": session.access_token,   # 👈 المفتاح المؤقت (ساعة)
            "refresh_token": session.refresh_token  # 👈 المفتاح الدائم (يجدد الجلسة)
        }

    except Exception as e:
        return {"error": f"فشل الدخول: {str(e)}"}
    
def login_with_token(access_token, refresh_token):
    """
    🌟 استعادة الجلسة وتجديدها تلقائياً
    """
    try:
        # محاولة تعيين الجلسة.
        # إذا كان access_token منتهي الصلاحية، سوبابيس ستستخدم refresh_token تلقائياً لإنعاش الجلسة.
        res = supabase.auth.set_session(access_token, refresh_token)
        
        if res and res.user and res.session:
            return {
                "success": True, 
                "user": res.user,
                # نرجع التوكنات الجديدة (قد تكون تغيرت بعد التحديث)
                "new_access_token": res.session.access_token,
                "new_refresh_token": res.session.refresh_token
            }
        else:
            return {"error": "Invalid Session Data"}
            
    except Exception as e:
        # إذا كان الـ Refresh Token أيضاً منتهي الصلاحية (مر عليه أسبوع مثلاً)
        return {"error": str(e)}

# ==========================================
# 📂 Project Management Functions
# ==========================================

def create_project(user_id, name, p_type, site, reqs, area):
    try:
        response = supabase.table("projects").insert({
            "user_id": user_id,
            "name": name,
            "project_type": p_type,
            "site_context": site,
            "requirements": reqs,
            "site_area": area,
            "current_phase": "Phase 0",
            "unlocked_phase": 0,
            "phase_tasks": [] # قائمة فارغة كبداية
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

def update_project_tasks(project_id, tasks_list):
    """تحديث قائمة المهام (Checklist) في سوبابيس"""
    try:
        # سوبابيس يخزن القوائم كـ JSONB تلقائياً
        supabase.table("projects").update({"phase_tasks": tasks_list}).eq("id", project_id).execute()
        return {"success": True}
    except Exception as e:
        print(f"Error updating tasks: {e}")
        return {"error": str(e)}

# ==========================================
# 💬 Chat Persistence Functions
# ==========================================

def save_message(project_id, role, content, image_urls=None): 
    try:
        # التأكد أن الصور هي قائمة (List) أو None
        if image_urls and not isinstance(image_urls, list):
            image_urls = [image_urls]

        data = {
            "project_id": project_id,
            "role": role,
            "content": content,
            "image_urls": image_urls 
        }
        
        
        res = supabase.table("chat_messages").insert(data).execute()
        if res.data:
            return res.data[0]['id']
        return None
    except Exception as e:
        print(f"Error saving message: {e}")
        return None

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
                # 👇 التعديل هنا: قمنا بتغيير image_url إلى image_urls
                # ونستخدم get لضمان عدم حدوث خطأ إذا كانت null
                "image": msg.get("image_urls") if msg.get("image_urls") else [],
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
    try:
        supabase.table("projects").update({"summary": summary_text}).eq("id", project_id).execute()
        return {"success": True}
    except Exception as e:
        print(f"Error updating summary: {e}")
        return {"error": str(e)}

def get_project_summary(project_id):
    try:
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
    try:
        supabase.table("chat_messages").delete().eq("project_id", project_id).execute()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def delete_project_permanently(project_id):
    try:
        # 1. حذف الرسائل
        supabase.table("chat_messages").delete().eq("project_id", project_id).execute()
        # 2. حذف الأرشيف (إن وجد)
        supabase.table("archives").delete().eq("project_id", project_id).execute()
        # 3. حذف المشروع
        supabase.table("projects").delete().eq("id", project_id).execute()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 📜 Archiving System
# ==========================================

def archive_current_chat(project_id, messages_list, summary_snapshot):
    try:
        formatted_text = ""
        for msg in messages_list:
            role = "👤 المعماري" if msg['role'] == 'user' else "👷‍♀️ آيلا"
            content = msg['content']
            
            # معالجة الصور في الأرشيف النصي
            images_note = ""
            if msg.get('image'): # في الذاكرة الحية اسمها image
                count = len(msg['image']) if isinstance(msg['image'], list) else 1
                images_note = f"\n[مرفق: {count} صور/مخططات]"
            
            # أو إذا كانت جاية من الداتابيس اسمها image_urls
            elif msg.get('image_urls'):
                 count = len(msg['image_urls'])
                 images_note = f"\n[مرفق: {count} صور/مخططات]"

            formatted_text += f"{role}: {content}{images_note}\n{'-'*20}\n"

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
    try:
        response = supabase.table("archives").select("*")\
            .eq("project_id", project_id)\
            .order("created_at", desc=True)\
            .execute()
        return response.data
    except Exception as e:
        return []
    
    # ==========================================
# 🧠 FACT EXTRACTION MEMORY (NEW ADDITION)
# ==========================================

def update_project_facts(project_id, facts_dict):
    """
    تحديث حقائق المشروع الهندسية (JSON)
    facts_dict: قاموس بايثون يحتوي على المعلومات
    """
    try:
        # Supabase يحول الـ Dict إلى JSONB تلقائياً
        supabase.table("projects").update({"project_facts": facts_dict}).eq("id", project_id).execute()
        return {"success": True}
    except Exception as e:
        print(f"Error updating facts: {e}")
        return {"error": str(e)}

def get_project_facts(project_id):
    """
    جلب الحقائق الهندسية كقاموس
    """
    try:
        response = supabase.table("projects").select("project_facts").eq("id", project_id).execute()
        if response.data and response.data[0]:
            # نرجع البيانات أو قاموس فارغ إذا كانت null
            return response.data[0].get("project_facts") or {}
        return {}
    except Exception as e:
        print(f"Error getting facts: {e}")
        return {}