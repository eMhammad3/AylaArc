# 1. نسخة البايثون
FROM python:3.12-slim

# 2. مكان العمل داخل الدوكر
WORKDIR /app

# 3. تثبيت المكتبات (تأكد من وجود ملف requirements.txt بجانب الملف)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. نسخ كل ملفاتك (app_ui.py, core_logic.py, إلخ)
COPY . .

# 5. فتح المنفذ الخاص بالمتصفح
EXPOSE 8501

# 6. أمر تشغيل ستريم ليت (لاحظ التغيير عن python main.py)
CMD ["streamlit", "run", "app_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]