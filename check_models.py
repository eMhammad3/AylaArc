import google.generativeai as genai
import os
from dotenv import load_dotenv

# تحميل المفتاح
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🔍 جاري البحث عن الموديلات المتاحة لحسابك...\n")

try:
    count = 0
    for m in genai.list_models():
        # احنا نريد بس الموديلات اللي تكدر "تولد محتوى" (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ اسم الموديل: {m.name}")
            print(f"   الوصف: {m.description}")
            print("-" * 30)
            count += 1
    
    if count == 0:
        print("❌ لم يتم العثور على أي موديل يدعم generateContent! تأكد من صلاحيات المفتاح.")
    else:
        print(f"\n✨ تم العثور على {count} موديل شغال.")

except Exception as e:
    print(f"🚨 حدث خطأ أثناء البحث: {e}")