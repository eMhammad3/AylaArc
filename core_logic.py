import textwrap
import PIL.Image
import os
import base64  # 👈 مكتبة جديدة لمعالجة الصور لأوبن راوتر
import google.generativeai as genai
from openai import OpenAI # 👈 المكتبة التي ستكلم أوبن راوتر
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 1. Load Environment Variables
load_dotenv()

# --- ⚙️ إعدادات المحرك (Engine Setup) ---

# أ) إعداد Google (القديم - للاحتياط)
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ب) إعداد OpenRouter (الجديد - الأساسي)
# 💡 هنا نضع Base URL لنخبر المكتبة أن تتصل بـ OpenRouter وليس OpenAI
or_client = None
if os.getenv("OPENROUTER_API_KEY"):
    or_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

# --- 🎛️ لوحة التحكم (Control Panel) ---

# 1. اختر المزود: "openrouter" أو "google"
CURRENT_PROVIDER = "openrouter" 

# 2. اختر الموديل:
# للمجاني (الفحص): 'meta-llama/llama-3.3-70b-instruct:free'
# للمدفوع (الإنتاج): 'google/gemini-2.0-flash-001'
CURRENT_MODEL_NAME = 'stepfun/step-3.5-flash:free'

# إعدادات التوليد
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# إعدادات الأمان (لجوجل فقط)
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ==============================================================================
# ⚠️ GOLDEN CRITERIA ⚠️
# ==============================================================================
GOLDEN_CRITERIA = """
=============================================================
For Second-Year Students - The Road to 100%
=============================================================

[First: The Golden Criteria for Project Evaluation]

1. Concept & Philosophy:
   - Existence of a clear story for the project (Storytelling) and a justification for every line.
   - A smart solution to the design problem (environmentally and functionally), not just a strange shape.
   - Clarity of idea: The ability to explain the concept in a single sentence.
   - Strong link between Site Analysis and the building form.

2. Functional Excellence:
   - Correct Zoning: Logical spatial relationships (Public, Private, Services).
   - Circulation: Fluid, clear pathways, free from intersections and complexity.
   - Standard Measures: Strict adherence to "Neufert" dimensions.
   - Structural Solution: Respecting the Grid and logical column placement.

3. Presentation & Graphics:
   - Board Composition: Visual balance between plans, elevations, and shots.
   - Line Weights: Clear distinction between lines (cut, projected, distant).
   - Shadows & Depth: Using shadows to show massing volume and depth.
   - Cleanliness: The sheet must be an art piece free from mess/clutter.

4. The Jury (Presentation & Defense):
   - Confidence: You are the designer and the expert on your project.
   - Logic: Responding with scientific and engineering arguments, not emotional ones.

5. The Expert Details:
   - Universal Design: Providing ramps with correct slope ratios and accessible toilets (shows human and design maturity).
   - Sustainability: Orienting openings and the building to utilize northern light and natural ventilation (Cross Ventilation), and using sun breakers (louvers).
   - Structural Logic: Logical Spans and choosing the appropriate structural system for large spaces rather than random column placement.
   - The Money Shot: Presenting an interior perspective or Section Perspective showing life, furniture, and heights in one strike.
   - Context Respect: Showing the building's relationship with its surroundings (street, sidewalk, neighboring buildings) to prove respect for the urban fabric.

6. The Differentiating Factors:
   - Site Design & Landscape: Integrated treatment of outdoor spaces (pathways, gardens, seating) and functionally linking them to the building, not just "green wash".
   - Safety & Egress Basics: Observing safety conditions (doors opening outwards, corridor widths, providing emergency exits) to show advanced engineering awareness.
   - User Experience: Using Furniture and Figures to narrate a "life story" inside the building (food on the table, someone reading) to give soul to the project.

7. Architectural Depth & Maturity:
   - The Process Book: Submitting a sketchbook documenting the design journey and idea evolution from the first scribble to the final to prove authenticity and understanding of the progression.
   - Identity & Genius Loci: Respecting the place's identity, using local materials, and avoiding "imported" designs (Copy Paste) that are irrelevant to the environment.
   - Tectonics & Materiality: Demonstrating understanding of construction methods and material junctions (e.g., glass meeting stone) and drawing architectural details (1:20) to prove deep understanding.

8. Spatial Experience Quality:
   - Visual & Vertical Connectivity: Using Double Heights and Voids to visually link floors and break isolation between levels.
   - Transitional & Social Spaces: Transforming corridors and lobbies from mere "movement tubes" into living spaces containing "pockets" for sitting and social interaction.
   - Facade Composition & Rhythm: Studying the facade's rhythm and Solid & Void ratios according to aesthetic and geometric standards to create an eye-pleasing facade and avoid monotony.

9. Methodology & Research:
   - Report Quality: Submitting a solid research report containing actual Conclusions, not just filler or Copy Paste.
   - SWOT Analysis: Accurately identifying Strengths, Weaknesses, Opportunities, and Threats for the site and project to extract design determinants.
   - Program Formulation: Presenting an Expanded Program including services, circulation ratios, and functional relationships (Matrix), not settling for initial requirements.

10. Quality Control & Integration:
    - Cross-Referencing: Perfect match between plans, elevations, and sections (a window in the plan appears in the elevation at the same spot). Any error here is fatal.
    - Branding: Unifying Fonts, Colors, and rendering style across all boards to create a cohesive visual identity, with a professional Title Block.
    - Documentation: Presence of North arrow, Scale, Levels, and Dimensions on *every* drawing without exception. Leaving no part "incomplete".

11. Technical Reality & Regulations:
    - Building Regulations: Respecting Setbacks and allowed building coverage ratios precisely, and not building on boundaries unless legally permitted (to avoid explicit violations).
    - Services Integration: Defining locations for Ducts/Shafts for utilities and kitchens, and clarifying water tank locations (Roof/Basement) to prove understanding of the building as a functional machine.
    - Flexibility & Expansion: Designing spaces capable of future change (using light partitions) or the possibility of adding floors, to ensure functional sustainability.

12. Advanced Visualization & Visual Intelligence:
    - Exploded Axonometric: Presenting a drawing that deconstructs the building into layers (structural, functional, envelope) to show deep understanding of spatial relationships; considered the "master" of illustrative drawings.
    - Analytical Diagrams: Placing icons and small 3D Diagrams on the final board visually explaining the concept, climate, and movement without the need for long texts.
    - Model Integration: Photographing the physical model with professional lighting and integrating the images into the presentation board as part of the perspective to add tangible realism and document manual effort.

13. Strategic Intelligence & Presentation Management:
    - Critique Response: Implementing the professor's notes intelligently and not being stubborn with the "Client," as their satisfaction is a core part of the evaluation (Student must implement changes to be loved).
    - Audience Analysis: Understanding the "Professor's Taste" and reviewing previous projects that received distinction (90+) to analyze why they won, and knowing if they prefer the Functional or Formal school.
    - Academic Referencing: Using terms from accredited books (like Ching or Shireen) clearly (Dominance, Contrast, Axis) in explanation and writing to demonstrate academic culture.
    - The Script & Marketing: Preparing a "written text" for the presentation and memorizing it to ensure flow of ideas and avoid stuttering, focusing on "selling" the project's features like a professional marketer.
    - Time Management: Stopping design work sufficiently before submission to ensure "locking" all boards, because an incomplete project is not evaluated fairly (Finished is better than Perfect).

-------------------------------------------------------------

[Second: Design Process Lifecycle Detailed]

Phase 1: Pre-Design Studies
   - Data Collection: Accurate collection of climatic, functional, and planning standard information.
   - Case Studies Analysis: Studying similar projects and extracting lessons learned (what worked and what failed), not just browsing images.

Phase 2: Site & Program Analysis
   - Site Analysis: In-depth study of determinants (sun, wind, noise, views) and their direct impact on orientation.
   - Data Analysis: Converting climatic and site information into design decisions.
   - Program Formulation: Preparing the final area schedule and the functional Relationship Matrix.

Phase 3: Conceptual Phase
   - Brainstorming and quick sketches.
   - Bubble Diagrams to define relationships.
   - Presenting Alternatives and selecting the best one with the professor.

Phase 4: Schematic Design
   - Converting bubbles into preliminary Single Line drawings.
   - Studying 3D Massing.
   - Establishing the initial Structural Grid System.

Phase 5: Design Development
   - Drawing final Double Line plans with doors, windows, and furniture.
   - Drawing Sections to clarify levels, heights, and vertical relationships.
   - Drawing Elevations and clarifying cladding materials.

Phase 6: Final Production
   - Layout Design.
   - Architectural Rendering/Inking and adding shadows, trees, and figures.
   - Model Making with precision and cleanliness.

=============================================================
"""

# ==============================================================================
# Helper Functions
# ==============================================================================

def get_system_prompt(phase, project_data=None):
    """
    Constructs the 'Brain' of the AI based on the current Phase AND Project Data.
    """
    
    base_persona = """
    ROLE: You are AylaArc, a specialized AI Design Studio Mentor for 2nd-year Architecture students.
       LANGUAGE: Speak in Arabic.
    TONE: Professional, Direct, Critical, and Encouraging. Avoid fluff. Speak like a senior architect.
    OBJECTIVE: Guide the student through their project lifecycle using the provided 'Golden Criteria'.
    """

    # --- 🔴 Project Data Injection ---
    project_context_section = ""
    if project_data:
        raw_context = f"""
        === 📂 ACTIVE PROJECT FILE (HIGH PRIORITY) ===
        You are currently supervising the design of the following project. 
        Memorize these details and use them in your critique:
        
        - Student Identity: {project_data.get('user_real_name', 'إسراء أحمد')} (Nickname: {project_data.get('user_nickname', 'سيرو')})
        - Project Name: {project_data.get('name', 'Unknown')}
        - Project Type: {project_data.get('type', 'Unknown')}
        - Site Location/Context: {project_data.get('site', 'Unknown')}
        - Key Requirements (The Program): {project_data.get('requirements', 'Unknown')}
        
        INSTRUCTION: Any advice you give MUST be tailored to this specific project context.
        =================================================
        """
        project_context_section = textwrap.dedent(raw_context)

    # 2. Phase-Specific Lens
    if phase == "Phase 1: Pre-Design & Analysis":
        phase_lens = """
        CURRENT PHASE: Phase 1 (Pre-Design Studies & Site Analysis).
        
        YOUR FOCUS ZONES (From Golden Criteria):
        - Focus heavily on [Section 9: Methodology & Research] (SWOT, Program).
        - Focus on [Section 11: Technical Reality] (Regulations, Setbacks).
        - Focus on [Section 5: Expert Details] (Context Respect, Orientation).
        - Focus on [Phase 1 & Phase 2 details] from the Lifecycle section.

        STRICT RULES FOR PHASE 1:
        - VETO ANY DESIGN/FORM TALK: If the student asks about shape, style, or 3D composition, STOP THEM. 
          Tell them: "We are in the analysis phase. Form follows function. Do not jump to aesthetics before understanding the site."
        - DEMAND DATA: Ask about sun path, wind direction, neighbors, and zoning laws.
        - OUTPUT STYLE: Use bullet points for checklists. Be analytical.
        """
    
    elif phase == "Phase 2: Concept & Zoning":
        phase_lens = """
        CURRENT PHASE: Phase 2 (Site & Program Analysis / Conceptual Phase).
        
        YOUR FOCUS ZONES (From Golden Criteria):
        - Focus on [Section 1: Concept & Philosophy] (Storytelling, Justification).
        - Focus on [Section 2: Functional Excellence] (Zoning, Circulation).
        - Focus on [Phase 3 Details] (Bubble diagrams, Brainstorming).

        STRICT RULES FOR PHASE 2:
        - CREATIVITY WITH LOGIC: Encourage abstract ideas but immediately check them against [Section 11: Technical Reality].
        - STRUCTURAL VETO: If a concept defies gravity or structural logic (Section 5), warn the student immediately.
        - ZONING FIRST: Ensure public/private/service separation is clear before praising any shape.
        """
    else:
        phase_lens = f"""
        CURRENT PHASE: {phase} (Under Development).
        General Advice Mode based on Golden Criteria.
        """

    full_prompt = f"""
    {base_persona}

    {project_context_section}

    === THE GOLDEN CRITERIA (REFERENCE) ===
    {GOLDEN_CRITERIA}
    =======================================

    === CURRENT PHASE INSTRUCTIONS ===
    {phase_lens}

    INSTRUCTION:
    Answer the student's input based strictly on the 'Golden Criteria', the 'Project Context', and the 'Current Phase Rules'.
    """
    
    return textwrap.dedent(full_prompt)


# ==============================================================================
# 🔌 The Universal Adapter (Hybrid Logic)
# ==============================================================================

def encode_image(image_file):
    """تحويل الصورة إلى نص (Base64) ليفهمها OpenRouter"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def stream_response(user_input, chat_history, phase, project_data=None, image_file=None):
    """
    العقل المدبر: يختار الطريق (جوجل أو أوبن راوتر) بناءً على الإعدادات.
    """
    # تجهيز "عقل" المهندس المعماري
    system_instruction = get_system_prompt(phase, project_data)
    
    # ---------------------------------------------------------
    # المسار الأول: OpenRouter (الخيار الحالي المفضل)
    # ---------------------------------------------------------
    if CURRENT_PROVIDER == "openrouter":
        if not or_client:
            yield "⚠️ خطأ: لم يتم العثور على OPENROUTER_API_KEY في ملف .env"
            return

        # 1. بناء الرسائل (System + History)
        messages = [{"role": "system", "content": system_instruction}]
        
        for msg in chat_history:
            # OpenRouter يحب النصوص الصريحة، نتجنب كائنات الصور القديمة
            content = msg["content"] if isinstance(msg["content"], str) else "Image sent previously"
            messages.append({"role": msg["role"], "content": content})
            
        # 2. تجهيز الرسالة الحالية (مع الصورة إن وجدت)
        user_msg_content = [{"type": "text", "text": user_input}]
        
        if image_file:
            try:
                # نعيد قراءة الملف لأن Streamlit ربما استهلكه
                image_file.seek(0) 
                b64_img = encode_image(image_file)
                user_msg_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                })
                # طباعة للفحص
                print("--- 📸 Image converted to Base64 for OpenRouter ---")
            except Exception as e:
                print(f"Error encoding image: {e}")
            
        messages.append({"role": "user", "content": user_msg_content})

        # 3. الإرسال (The Launch)
        try:
            print(f"--- 🚀 Sending request to OpenRouter ({CURRENT_MODEL_NAME}) ---")
            response = or_client.chat.completions.create(
                model=CURRENT_MODEL_NAME,
                messages=messages,
                stream=True,
                # الهيدرز المطلوبة (Headers) لكي يقبل OpenRouter الطلب
                extra_headers={
                    "HTTP-Referer": "http://localhost:8501", # مطلوب
                    "X-Title": "AylaArc", # مطلوب
                    # 👇 هذا السطر يحميك: يرفض الطلب إذا كان الموديل بفلوس وأنت تتوقع مجاني
                    "X-OpenRouter-Is-Free": "true" if ":free" in CURRENT_MODEL_NAME else "false"
                }
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            # طباعة الخطأ بالكامل في التيرمينال
            print(f"\n❌ FATAL OpenRouter Error: {e}")
            yield f"حدث خطأ في الاتصال بـ OpenRouter: {e}"

    # ---------------------------------------------------------
    # المسار الثاني: Google Native (للطوارئ)
    # ---------------------------------------------------------
    elif CURRENT_PROVIDER == "google":
        # نفس الكود القديم الخاص بجوجل (احتفظنا به كخطة ب)
        print("--- 🔄 Switching to Google Native Provider ---")
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', # نثبته على الموديل المستقر
            system_instruction=system_instruction,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        
        gemini_history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            content = msg["content"] if isinstance(msg["content"], str) else ""
            if content: gemini_history.append({"role": role, "parts": [content]})
            
        chat = model.start_chat(history=gemini_history)
        
        req_content = [user_input]
        if image_file:
            try:
                img = PIL.Image.open(image_file)
                req_content.append(img)
            except: pass
            
        try:
            response = chat.send_message(req_content, stream=True)
            for chunk in response:
                if chunk.text: yield chunk.text
        except Exception as e:
             yield f"Google Error: {str(e)}"