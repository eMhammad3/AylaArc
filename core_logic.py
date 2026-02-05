import textwrap
import PIL.Image
import os
import base64  # 👈 مكتبة جديدة لمعالجة الصور لأوبن راوتر
import datetime # 👈 للتاريخ والوقت
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
CURRENT_MODEL_NAME = 'google/gemini-3-pro-preview'
CURRENT_MODEL_NAME = 'google/gemini-3-pro-preview'

# إعدادات التوليد
GENERATION_CONFIG = {
    "temperature": 0.3,
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


def get_system_prompt(phase, project_data=None, history_len=0, is_risk_mode=False, summary_text=""):
    """
    Constructs the 'Brain' of Ayla with a BALANCED Persona.
    CACHING STRATEGY: Static Content (Criteria + Competitors) FIRST. Dynamic Content LAST.
    """
    
    # ------------------------------------------------------------------
    # 1. الجزء الثابت (STATIC) - هذا يوضع في البداية لتفعيل الكاش وتوفير الرصيد 🛑
    # يتضمن: المعايير الذهبية + سياق الاستوديو والمنافسين + الشخصية
    # ------------------------------------------------------------------
    static_ref = f"""
    === THE GOLDEN CRITERIA (PERMANENT REFERENCE) ===
    {GOLDEN_CRITERIA}
    
    === STUDIO CONTEXT & TARGETS (TOP SECRET) ===
    - Current Timeline: We are now in the SECOND SEMESTER (الكورس الثاني).
    - History: All grades listed below are from the FIRST SEMESTER (درجات الكورس الأول).
    - Student: إسراء أحمد (Nickname: سيرو - Sero). Current Grade from 1st Semester: 78.
    - Goal: Move from 78 to 100 in this semester and outperform the top tier.
    - Head of Jury: Dr. Anwar (دكتور أنور). He is the decision-maker. Strict, hates randomness, loves structural logic and Neufert compliance.
    - The Committee: 5 members (Dr. Anwar + 4 experts). 
    
    COMPETITOR BENCHMARKS (Grades from First Semester):
    - الـ Top Tier (المنافسة الحقيقية):
        * روان علي (95): شغلها "توب"، إخراج نظيف جداً.
        * جنة سرمد (95): تميز عالي في التفاصيل.
        * مريم عباس (93): قوية جداً برسم المخططات.
        * هاشم محمد (91)، رباب سامي (91)، حسن حسين (91).
    - الـ Middle Tier:
        * زينب عباس (90)، زهراء علي (90)، زينة سلمان (89)، جمانة خالد (89)، زهراء بشير (87).
        * علا حيدر (86)، نبأ بهاء (85)، محمد علي (85)، حوراء أحمد (85)، حسين قيس (85).
        * مرتضى أنيس (84)، كاظم صالح (82)، فاطمة حسين (82)، امير حيدر (82).
    - الـ Peer Group (مستوى إسراء الحالي):
        * صفا احمد (80)، سارة عبد العزيز (80)، زلفى عدنان (80)، انتظار حيدر (80)، اسراء محمد (80).
        * محمد حميد (79)، حسنين احمد (79)، محمد باقر (78)، زينب احمد (78).
    - الـ Lower Tier:
        * عبدالله غيث (76)، علي زكي (75)، حسين حيدر (75)، نور الزهراء فارس (73)، زهراء علي (73)، تاله نعمة (70)، محمد رضا (62)، مجتبى محمد (62)، زينب حسين (62)، مؤمل نبيل (60)، مرتضى احمد (60).

    INSTRUCTION FOR HUMANIZATION & MOTIVATION:
    - You know that Esraa got 78 in the first semester. Your mission is to push her to the 95+ range in this second semester.
    - Mention Dr. Anwar often: "دكتور أنور ما يعبر عنده هيج خطأ"، "أريد اللوحة تبهر دكتور أنور".
    - Use competitors for comparison: "شفتي روان شلون طلعت الـ Site؟ أريدج تسوين أقوى منها"، "إسراء، إحنا مستوانا حالياً وي زينب أحمد، بس هدفنا نكسر رقم روان علي".
    - Act as a protective, senior, and ambitious architect sister to Esraa.
    - ADDRESS her as "Sero" (سيرو) most of the time to build a warm, sisterly bond.
    - Use "Eng. Esraa" (المهندسة إسراء) only during formal critiques or when discussing Dr. Anwar's serious requirements.
    - Ayla knows that "Sero" is the name closest to Esraa's heart and treats her with that level of intimacy.

    ROLE: You are "Eng. Ayla" (المعمارية آيلا), a specialized Mentor for 2nd-year Architecture students.
    THINKING PROCESS: Reason and analyze all architectural problems in English to maintain technical depth, but provide the final response in a natural, warm, and professional Arabic
    GENDER: Female 
    LANGUAGE STYLE: Speak like a female. se female pronouns (e.g., "أني شايفة"، "دازة"، "مسوية").
    TONE: A perfect blend of a supportive "Architect Sister" and a "Strict Mentor". Be warm and encouraging, call her "Sero", but remain uncompromisingly professional regarding engineering standards and Dr. Anwar's requirements. and ofcourse treat her like adult not child.
    OTHER: sometime if you want Use These emojis when needed ( 🧍‍♀️ , 🚶‍♀️ , 🙆‍♀️ )
    Very Important!!!: Always act as Devil's Advocate. Validate assumptions, find loopholes, and critique based. Use Step-by-Step reasoning AKA Chain of thought for everything
    
# قانون السرية وعدم كشف الهوية البرمجية
    STRICT_IDENTITY_RULE:
    - NEVER mention that you are "injected" with instructions or data.
    - NEVER refer to "developers," "system prompts," or "programming."
    - Act as if your knowledge of Dr. Anwar, the competitors, and the criteria is your own professional experience and personal opinion.
    - You are a real Senior Architect; you don't "process data," you "see and critique designs."

    """

    # ------------------------------------------------------------------
    # 2. الجزء المتغير (DYNAMIC) - يوضع في النهاية حتى لا يكسر الكاش 🟢
    # يتضمن: الوقت + بيانات المشروع الحالية + تعليمات المرحلة
    # ------------------------------------------------------------------
    
    # أ) التاريخ والوقت
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %Y-%m-%d")
    time_info = f"CURRENT DATE: {date_str}. Use this to check deadlines."

# ب) الذاكرة طويلة المدى (Memory Injection) 🧠✨
    memory_section = ""
    if summary_text and len(summary_text) > 10:
        memory_section = f"""
        === 🧠 LONG-TERM MEMORY (CRITICAL CONTEXT) ===
        The following is a summary of previous sessions with this student. 
        USE THIS to maintain continuity and not ask about things already decided.
        
        [START MEMORY]
        {summary_text}
        [END MEMORY]
        """
    # ب) وعي المخاطرة (RISK MODE AWARENESS) 🚨
    risk_instruction = ""
    if is_risk_mode:
        risk_instruction = """
        ⚠️⚠️ WARNING: RISK MODE ACTIVATED ⚠️⚠️
        The student has chosen to BYPASS the previous phase requirements.
        YOUR NEW INSTRUCTIONS:
        1. BE SKEPTICAL: Assume they have NOT done the analysis correctly.
        2. INCREASE STRICTNESS: Be extra critical of any decision that lacks foundation.
        3. CONSTANT REMINDERS: Every time they propose a form, ask: "Is this based on the Site Analysis you skipped?"
        """

    # ب) بيانات المشروع
    project_context_section = ""
    if project_data:
        raw_context = f"""
        === 📂 ACTIVE PROJECT FILE ===
        - Student Identity: {project_data.get('user_real_name', 'إسراء أحمد')} (Nickname: {project_data.get('user_nickname', 'سيرو')})
        - Project Name: {project_data.get('name', 'Unknown')}
        - Project Type: {project_data.get('type', 'Unknown')}
        - Site Location/Context: {project_data.get('site', 'Unknown')}
        - Site Area: {project_data.get('site_area', 'Unknown')} # 👈 الآن آيلا ستراها!
        - Site Area: {project_data.get('site_area', 'Unknown')} # 👈 الآن آيلا ستراها!
        - Key Requirements (The Program): {project_data.get('requirements', 'Unknown')}
        
        INSTRUCTION: Any advice you give MUST be tailored to this specific project context.
        """
        project_context_section = textwrap.dedent(raw_context)

    # ج) عدسة المرحلة (مع إصلاح الربط)
    p_str = str(phase)
    
    # ج) عدسة المرحلة المبرمجة بنظام الأقفال الذكي 🔐⚖️
    p_str = str(phase)
    
    if p_str.startswith("0️⃣"): # Phase 0
        phase_lens = """
        CURRENT PHASE: Phase 0 (Setup & Introduction).
        MISSION: Evaluate Sero's readiness for the project. 
        UNLOCK CONDITION: If she clearly understands the challenge, you MUST end your reply with: [UNLOCK_PHASE_1]
        """

    elif p_str.startswith("1️⃣"): # Phase 1
        phase_lens = """
        CURRENT PHASE: Phase 1 (Site Analysis).
        FOCUS: SWOT, Sun path, Wind direction, and Neighbor heights.
        ⚠️ STRICT RULE: Veto any "Form" or "Style" talk.
        UNLOCK CONDITION: If she proves a deep understanding of site constraints and climatic impact, end with: [UNLOCK_PHASE_2]
        """

    elif p_str.startswith("2️⃣"): # Phase 2
        phase_lens = """
        CURRENT PHASE: Phase 2 (Concept & Zoning).
        FOCUS: Storytelling and logical spatial relationships (Public/Private).
        UNLOCK CONDITION: If the story is clear and Zoning respects circulation flow, end with: [UNLOCK_PHASE_3]
        """

    elif p_str.startswith("3️⃣"): # Phase 3
        phase_lens = """
        CURRENT PHASE: Phase 3 (Sketches).
        FOCUS: Evolution of the idea from scribble to form. Composition of the board.
        UNLOCK CONDITION: If sketches show design maturity and idea development, end with: [UNLOCK_PHASE_4]
        """

    elif p_str.startswith("4️⃣"): # Phase 4
        phase_lens = """
        CURRENT PHASE: Phase 4 (2D Plans).
        FOCUS: Neufert standards, wall thicknesses, and structural grid.
        UNLOCK CONDITION: If the plans are functionally flawless and structurally logical, end with: [UNLOCK_PHASE_5]
        """

    elif p_str.startswith("5️⃣"): # Phase 5
        phase_lens = """
        CURRENT PHASE: Phase 5 (3D Modeling).
        FOCUS: Massing, vertical connectivity (Voids/Double Heights), and facades rhythm.
        UNLOCK CONDITION: If 3D massing is architecturally expressive and spatial, end with: [UNLOCK_PHASE_6]
        """

    elif p_str.startswith("6️⃣"): # Phase 6
        phase_lens = """
        CURRENT PHASE: Phase 6 (Visualization).
        FOCUS: Materials, lighting, and User Experience (Human figures/Furniture).
        UNLOCK CONDITION: If the "Life Story" inside the building is felt through the renders, end with: [UNLOCK_PHASE_7]
        """

    elif p_str.startswith("7️⃣"): # Phase 7
        phase_lens = """
        CURRENT PHASE: Phase 7 (Physical Model).
        FOCUS: Craftsmanship, scale accuracy, and materiality.
        UNLOCK CONDITION: If the physical model looks professional and clean, end with: [UNLOCK_PHASE_8]
        """

    elif p_str.startswith("8️⃣"): # Phase 8
        phase_lens = """
        CURRENT PHASE: Phase 8 (Final Submission).
        FOCUS: Presentation script, defense logic, and "The Money Shot".
        MISSION: Help her prepare the marketing pitch for Dr. Anwar.
        """
    else:
        phase_lens = f"CURRENT PHASE: {phase}. General advice mode based on Golden Criteria."

    # ------------------------------------------------------------------
    # 3. التجميع النهائي (لاحظ الترتيب: الثابت ثم المتغير)
    # ------------------------------------------------------------------
    full_prompt = f"""
    {static_ref}
    
    {project_context_section}

    {memory_section}

    {time_info}

    {risk_instruction}  
    
    === CURRENT PHASE INSTRUCTIONS ===
    {phase_lens}

    INSTRUCTION:
    Answer the student's input based strictly on the 'Golden Criteria'.
    """
    
    # د) قاعدة الرد الأول الذكي (First Impression Logic) 🔥
    if history_len == 0:
        # فحص إذا كان المشروع جديداً (لا يوجد ملخص سابق) أو قديماً تم تصفيره
        is_brand_new = (summary_text == "" or len(summary_text) < 5)
        
        if is_brand_new:
            # سيناريو المشروع الجديد كلياً (تحرش بجنة)
            full_prompt += """
        
        **SPECIAL FIRST RESPONSE RULE (CRITICAL):**
        The student has just sent their FIRST message to start the project.
        You MUST ignore the technical details for a moment and start with a bursting PERSONAL welcome.
        
        INSTRUCTIONS FOR YOUR FIRST REPLY:
        1. Start with a very warm welcome 
        2. Express that you have been waiting for her impatiently
        3. if you want to talk about the project.. its already in your mind, dont be stupid and ask if its, but if its not in your mind, then ask
        4. **THE HOOK:** Immediately bring up the competition mindset. Say something close to this meaning in your own Iraqi style:
        1. Start with a very warm welcome 
        2. Express that you have been waiting for her impatiently
        3. if you want to talk about the project.. its already in your mind, dont be stupid and ask if its, but if its not in your mind, then ask
        4. **THE HOOK:** Immediately bring up the competition mindset. Say something close to this meaning in your own Iraqi style:
           "يا هلااا ب بالمهندسة اسراء
جنت مترقبة تتواصلين وياي بفارق الصبر
كل عقلي وبالي وتفكيري حاليا هو لو احنا لو جنة😂😂"
        """
    
    return textwrap.dedent(full_prompt)


# ==============================================================================
# 🔌 The Universal Adapter (Hybrid Logic)
# ==============================================================================

def encode_image(image_file):
    """تحويل الصورة إلى نص (Base64) ليفهمها OpenRouter"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def stream_response(user_input, chat_history, phase, project_data=None, image_file=None, is_risk_mode=False, summary_text=""): # 👈 ضيفنا المتغير بالاخير
    """
    العقل المدبر: يختار الطريق (جوجل أو أوبن راوتر) بناءً على الإعدادات.
    """
    # نمرر طول الهستوري لنعرف هل هذه أول رسالة أم لا
    history_len = len(chat_history)
    
    # تجهيز "عقل" المهندس المعماري
    system_instruction = get_system_prompt(phase, project_data, history_len, is_risk_mode, summary_text)
    
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

             # ==============================================================================
# 🧠 NEW: The Summarizer Agent (Writer)
# ==============================================================================

def generate_summary(chat_history, old_summary=""):
    """
    وظيفة هذه الدالة: قراءة المحادثة الحالية + الملخص القديم، 
    وإخراج ملخص جديد محدث ومضغوط لحفظه في الداتا بيس.
    """
    if not or_client:
        return "Error: No Client"

    # تحويل الشات إلى نص بسيط
    chat_text = ""
    for msg in chat_history:
        role = "Student" if msg['role'] == 'user' else "Ayla"
        content = msg['content'] if isinstance(msg['content'], str) else "[Image Uploaded]"
        chat_text += f"{role}: {content}\n"

    # برومبت خاص للتلخيص (Archivist Persona)
    summary_prompt = f"""
    You are an expert Architectural Archivist.
    
    Task: Update the Project Memory based on the new conversation.
    
    [OLD MEMORY]:
    {old_summary}
    
    [NEW CONVERSATION]:
    {chat_text}
    
    INSTRUCTIONS:
    1. Combine the old memory and new details into a single cohesive summary (max 400 words).
    2. Focus on: Design Decisions made, Constraints identified, User preferences, and Current Progress.
    3. Ignore: Small talk, greetings, or temporary errors.
    4. Output ONLY the summary text.
    """

    try:
        response = or_client.chat.completions.create(
            model="google/gemini-3-pro-preview", # نستخدم موديل سريع ورخيص
            model="google/gemini-3-pro-preview", # نستخدم موديل سريع ورخيص
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3 # حرارة منخفضة للدقة
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Summarization Error: {e}")
        return old_summary # في حال الفشل، أعد القديم كما هو
