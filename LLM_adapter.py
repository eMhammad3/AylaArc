import os
import base64
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# تهيئة العملاء (Clients)
# 1. Google Native
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. OpenRouter
or_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def get_chat_response(messages, system_instruction, provider="openrouter", model_name="google/gemini-2.0-flash-lite-preview-02-05:free", image_file=None):
    """
    محول عالمي يختار بين OpenRouter و Google AI Studio تلقائياً
    """
    
    if provider == "google":
        # --- منطق Google AI Studio الأصلي ---
        model = genai.GenerativeModel(
            model_name=model_name.replace("google/", ""), # تنظيف الاسم
            system_instruction=system_instruction
        )
        # تحويل صيغة الرسائل لـ Gemini Native
        gemini_messages = [] # (هنا نضع منطق تحويل الهستوري كما فعلنا سابقاً)
        
        # الإرسال
        response = model.generate_content([messages[-1]['content'], image_file] if image_file else messages[-1]['content'], stream=True)
        for chunk in response:
            yield chunk.text

    elif provider == "openrouter":
        # --- منطق OpenRouter (OpenAI SDK) ---
        formatted_messages = [{"role": "system", "content": system_instruction}]
        formatted_messages.extend(messages) # نمرر الرسائل كما هي لأن OpenRouter يفهمها
        
        response = or_client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            stream=True,
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "AylaArc",
                "X-OpenRouter-Is-Free": "true" if ":free" in model_name else "false"
            }
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content