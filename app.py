import streamlit as st
import os
import time
import json
import requests
import base64
from groq import Groq

# ================== Page Config ==================
st.set_page_config(
    page_title="Gesner Deslandes AI Agent Builder",
    page_icon="🤖",
    layout="wide"
)

# ================== Custom CSS (Branded Light Purple Theme) ==================
st.markdown("""
<style>
    /* Light lavender background throughout the app and sidebar */
    .stApp, [data-testid="stSidebar"] {
        background-color: #E6E6FA !important;
    }
    
    /* Sidebar border adjustment */
    [data-testid="stSidebar"] {
        border-right: 3px solid #8A2BE2;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 {
        color: #333333 !important;
    }
    
    /* Elegant Dark Violet Typography */
    h1, h2, h3, h4 { color: #4B0082 !important; font-weight: bold; }
    p, li, span, .stMarkdown { color: #111111 !important; }
    
    /* White-Glass Cards for Content Blocks */
    .metric-card, .debugger-card, .agent-card, .video-preview-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #8A2BE2;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Custom CSS alignment wrapper for Title & Avatar */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 5px;
    }
    .title-avatar {
        border-radius: 50%;
        width: 75px;
        height: 75px;
        border: 3px solid #8A2BE2;
        object-fit: cover;
    }
    
    /* Code box styling */
    pre {
        background-color: #f4f4f9 !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #8A2BE2 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #4B0082 !important;
        border-color: #4B0082 !important;
    }
    
    /* Main footer design */
    .main-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 2px solid #8A2BE2;
        color: #4B0082 !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ================== Asset & API Configurations ==================
GITHUB_AVATAR_URL = "https://github.com/Deslandes1.png"
has_groq = "GROQ_API_KEY" in st.secrets
has_gemini = "GEMINI_API_KEY" in st.secrets

# ================== Active Agent Tools ==================

def tool_translation_haiti(text, target_lang):
    """Translates Haitian Creole text into English, Spanish, or French."""
    translations = {
        "english": {
            "enjenyè": "engineer",
            "pwofesè": "teacher",
            "lojisyèl": "software",
            "kòd": "code",
            "kreyòl": "Creole"
        },
        "french": {
            "enjenyè": "ingénieur",
            "pwofesè": "professeur",
            "lojisyèl": "logiciel",
            "kòd": "code",
            "kreyòl": "créole"
        },
        "spanish": {
            "enjenyè": "ingeniero",
            "pwofesè": "profesor",
            "lojisyèl": "software",
            "kòd": "código",
            "kreyòl": "criollo"
        }
    }
    target = target_lang.lower().strip()
    words = text.lower().replace(".", "").replace(",", "").split()
    translated_words = []
    
    if target in translations:
        for word in words:
            translated_words.append(translations[target].get(word, f"[{word}]"))
        return " ".join(translated_words)
    return f"Translation target '{target_lang}' not supported by tool."

def tool_accent_detector(text):
    """Analyzes text and catches common missing grave accents (È/Ò) in Creole words."""
    corrections = []
    text_lower = text.lower()
    if "enjenye" in text_lower and "enjenyè" not in text_lower:
        corrections.append("Correction: Changed 'enjenye' to 'enjenyè' (Missing È grave accent).")
    if "pwofese" in text_lower and "pwofesè" not in text_lower:
        corrections.append("Correction: Changed 'pwofese' to 'pwofesè' (Missing È grave accent).")
    if "lojisyel" in text_lower and "lojisyèl" not in text_lower:
        corrections.append("Correction: Changed 'lojisyel' to 'lojisyèl' (Missing È grave accent).")
    if "kod" in text_lower and "kòd" not in text_lower:
        corrections.append("Correction: Changed 'kod' to 'kòd' (Missing Ò grave accent).")
    
    if corrections:
        return "\n".join(corrections)
    return "No missing grave accents detected in Creole keywords."

def tool_imagen_generator(prompt):
    """Generates a base64 portrait image using Google's Imagen model."""
    if not has_gemini:
        # Fallback simulation image (Placeholder SVG avatar of an AI teacher)
        return "SIMULATED_IMAGE_DATA_AVATAR"
        
    api_key = st.secrets["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "outputMimeType": "image/jpeg"
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        base64_data = result["predictions"][0]["bytesBase64Encoded"]
        return f"data:image/jpeg;base64,{base64_data}"
    except Exception as e:
        return f"Simulation Fallback (Error calling Imagen: {str(e)})"

# ================== Sidebar Brand Panel ==================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 15px;">
        <img src="{GITHUB_AVATAR_URL}" style="border-radius: 50%; width: 110px; border: 3px solid #8A2BE2;">
        <h2 style="margin-top: 10px; font-size: 1.4rem; font-weight: bold;">GlobalInternet.py</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    if has_groq:
        st.success("⚡ Groq API Connected!")
    else:
        st.warning("⚠️ Groq Key missing in Secrets. Running Simulation Mode.")

    if has_gemini:
        st.success("🎨 Imagen Engine Connected!")
    else:
        st.info("💡 Add GEMINI_API_KEY to secrets to generate real images.")
        
    st.header("⚙️ Agent Settings")
    temperature = st.sidebar.slider("Agent Temperature (Creativity vs Determinism)", 0.0, 1.0, 0.1, step=0.05)
    model_name = st.sidebar.selectbox("LLM Core Engine:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"])
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Creator profile")
    st.markdown("**Enjenyè-an-Chèf:** GESNER DESLANDES")
    st.markdown("📱 (509) 4738 5663")
    st.markdown("[Visit Website](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")

# ================== Main Window Rendering ==================
st.markdown(f"""
<div class="title-container">
    <h1>Gesner Deslandes AI Agent Builder</h1>
    <img class="title-avatar" src="{GITHUB_AVATAR_URL}">
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 1.2rem; font-style: italic; color: #333333;'>Design, Validate, and Deploy AI Agents Using the Core Principles of Simple Agent Architecture</p>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #8A2BE2 !important; letter-spacing: 1px; font-weight: bold;'>BUILT BY GESNER DESLANDES FOR GLOBALINTERNET.PY</h4>", unsafe_allow_html=True)
st.markdown("---")

# ================== Rule 1: Task Evaluation Panel ==================
st.markdown("## 1️⃣ Rule 1: Don't Build Agents for Everything")
st.markdown("Before writing complex loops, verify if your task actually requires an agent, or if it can be mapped via standard Python workflows.")

col_input, col_eval = st.columns(2)

with col_input:
    st.markdown("#### Evaluate Your Next Task")
    task_desc = st.text_area(
        "What is the goal of your automation/agent?", 
        value="Generate a Haitian Creole teacher profile portrait and convert it into a talking photo lesson video.", 
        height=100
    )
    
    q1 = st.checkbox("Is the execution flow too ambiguous to map with standard if/else statements?", value=True)
    q2 = st.checkbox("Does the output format require natural language reasoning or contextual decisions?", value=True)
    q3 = st.checkbox("Does the task require choosing between multiple external interfaces/tools dynamically?", value=True)
    q4 = st.checkbox("Can this task be solved with 100% deterministic code? (If yes, map the workflow instead)", value=False)

with col_eval:
    st.markdown("#### Automation Recommendation Matrix")
    
    score = 0
    if q1: score += 30
    if q2: score += 30
    if q3: score += 40
    if q4: score -= 50
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f"### Design Recommendation Score: **{score}/100**")
    
    if score >= 60:
        st.success("🎯 **VERDICT: Build an AI Agent.** This workflow involves complex coordination between asset generation APIs, text layout engines, and dynamic rendering loops.")
    elif score >= 20:
        st.info("🔄 **VERDICT: Build a Hybrid Chain.** Use structured prompting or standard APIs sequentially rather than letting an agent run free in tool loops.")
    else:
        st.error("🛑 **VERDICT: Use standard Python scripts.** Save money and compute!")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================== Rule 2 & 3: Interactive Sandbox ==================
st.markdown("## 2️⃣ Rules 2 & 3: Simple Loop Design & Context Debugger")
st.markdown("An agent is merely a model inside a loop with access to a specific **Context**, **System Instructions**, and a **Set of Tools**.")

col_sandbox, col_terminal = st.columns([1.1, 1])

system_prompt_template = (
    "You are an AI Agent designed by Engineer Gesner Deslandes for GlobalInternet.py.\n"
    "Your environment has access to exactly three tools:\n"
    "1. translation_tool(text, target_lang) - translates Creole words to target language.\n"
    "2. accent_corrector(text) - checks and corrects missing accents in Creole.\n"
    "3. imagen_generator(prompt) - generates a portrait picture based on description.\n\n"
    "Respond using JSON format only:\n"
    "{\n"
    "  \"thought\": \"your reasoning process\",\n"
    "  \"tool_to_use\": \"tool_name or None\",\n"
    "  \"tool_input\": \"parameters\",\n"
    "  \"final_answer\": \"the final result or voice script content\"\n"
    "}"
)

with col_sandbox:
    st.markdown("#### Configure Agent Workspace Environment")
    
    system_instructions = st.text_area("Agent System Prompt (Context Boundaries):", value=system_prompt_template, height=180)
    
    st.markdown("**Active Tools in Workspace:**")
    st.code("🔧 translation_tool(target_lang, text)\n🔧 accent_corrector(text)\n🔧 imagen_generator(prompt)")
    
    st.markdown("#### 🖼️ Image Resource Selection")
    pic_source = st.radio("Portrait Image Source for Video:", ["Generate using AI Tool", "Upload My Own Picture"])
    uploaded_pic_base64 = None
    
    if pic_source == "Upload My Own Picture":
        uploaded_file = st.file_uploader("Upload a Portrait Picture (JPG/PNG)", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            bytes_data = uploaded_file.getvalue()
            uploaded_pic_base64 = f"data:image/jpeg;base64,{base64.b64encode(bytes_data).decode()}"
            st.image(uploaded_file, caption="🟢 Active Portrait Asset Loaded", width=150)
    else:
        st.info("💡 The agent will automatically trigger the 'imagen_generator' tool to create a portrait based on your description.")
    
    user_query = st.text_input(
        "Simulate User Query Input:", 
        value="Generate a portrait of an elegant Haitian Creole teacher, correct her motto 'pwofese a ap travay', and prepare a script."
    )
    
    run_agent = st.button("🚀 Execute Model-Tool Loop")

with col_terminal:
    st.markdown("#### 🔍 What the Agent Sees (Raw Context)")
    
    st.markdown('<div class="debugger-card">', unsafe_allow_html=True)
    st.markdown("**RAW PROMPT TO LLM ARCHITECTURE:**")
    debug_context = {
        "ROLE": "SYSTEM INSTRUCTIONS",
        "CONTEXT_PROMPT": system_instructions,
        "INPUT_QUERY": user_query,
        "USER_UPLOADED_IMAGE_ASSET": uploaded_pic_base64[:60] + "..." if uploaded_pic_base64 else None,
        "BOUNDARIES": "Respond using JSON matching defined format. No other words outside JSON container."
    }
    st.json(debug_context)
    st.markdown('</div>', unsafe_allow_html=True)

# Loop Execution Logic
if run_agent:
    st.markdown("---")
    st.markdown("## ⚙️ Execution Loop (ReAct Phase Trace)")
    
    if not has_groq:
        # Simulation Mode Trace with dynamic lipsync components
        with st.status("Running Multimedia Agent Loop Simulation...", expanded=True) as status:
            st.write("🔄 **Step 1: Parsing Multimedia request parameters...**")
            time.sleep(1.0)
            
            st.write("💭 **Step 2: LLM Reasoning (Handling Image Resource selection)...**")
            if pic_source == "Upload My Own Picture" and uploaded_pic_base64:
                st.write("✅ **Detected custom user-uploaded picture. Bypassing AI generation tool.**")
                img_data = uploaded_pic_base64
            else:
                simulated_thought_1 = {
                    "thought": "I need to generate a portrait first. I will call the imagen_generator tool with a description of an elegant Haitian teacher.",
                    "tool_to_use": "imagen_generator",
                    "tool_input": "An elegant Haitian Creole female teacher, professional profile picture, high quality",
                    "final_answer": ""
                }
                st.json(simulated_thought_1)
                time.sleep(1.2)
                
                st.write("🛠️ **Step 3: Generating Visual Asset...**")
                img_data = tool_imagen_generator("An elegant Haitian Creole female teacher, professional profile picture, high quality")
                st.code(f"Generated Asset Reference: {img_data[:40]}...")
                time.sleep(1.0)
            
            st.write("💭 **Step 4: LLM Reasoning (Checking grammar accents)...**")
            simulated_thought_2 = {
                "thought": "The image asset is ready. Now I will check the motto 'pwofese a ap travay' for missing accents using the accent_corrector tool.",
                "tool_to_use": "accent_corrector",
                "tool_input": "pwofese a ap travay",
                "final_answer": ""
            }
            st.json(simulated_thought_2)
            time.sleep(1.2)
            
            corrected_text = tool_accent_detector("pwofese a ap travay")
            st.code(f"Correction output: {corrected_text}")
            time.sleep(1.0)
            
            st.write("🎯 **Step 5: Compiling visual asset with audio lipsync configurations...**")
            final_res = {
                "thought": "All tools completed. I have corrected the motto to 'Pwofesè a ap travay' and generated the teacher's profile picture. Now compiling the talking photo profile.",
                "tool_to_use": "None",
                "tool_input": "None",
                "final_answer": "Pwofesè a ap travay. (The teacher is working.)"
            }
            st.json(final_res)
            time.sleep(0.8)
            
            status.update(label="Talking Photo Video Compilation Completed Successfully!", state="complete")
            
            # Interactive HTML5/CSS Lipsync Simulator component
            st.markdown('<div class="video-preview-card">', unsafe_allow_html=True)
            st.markdown("### 📽️ Simulated Talking Photo Video Output")
            col_v1, col_v2 = st.columns([1, 2])
            
            with col_v1:
                # Displays avatar alongside a talking CSS animation
                display_avatar = img_data if img_data else GITHUB_AVATAR_URL
                st.markdown(f"""
                <div style="text-align: center; background: #333; padding: 20px; border-radius: 12px; position: relative; overflow: hidden; width: 200px; height: 200px; margin: auto;">
                    <img src="{display_avatar}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">
                    <!-- Pulse effect simulating talking motion -->
                    <div style="position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); background: #8A2BE2; width: 25px; height: 25px; border-radius: 50%; animation: pulse 1s infinite;"></div>
                </div>
                <style>
                    @keyframes pulse {{
                        0% {{ transform: translateX(-50%) scale(1); opacity: 1; }}
                        50% {{ transform: translateX(-50%) scale(1.6); opacity: 0.4; }}
                        100% {{ transform: translateX(-50%) scale(1); opacity: 1; }}
                    }}
                </style>
                """, unsafe_allow_html=True)
                
            with col_v2:
                st.write("**🔈 Voice Track (Haitian Creole):**")
                st.info("« Genhen 2 lèt ki pran aksan fòs nan kreyòl Ayisyen, se È ak Ò. Pwofesè a ap travay sou kòd lojisyèl la! »")
                st.success("✅ Lipsync generated at 24fps matching original vocal track length.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # Live Run Mode utilizing actual Groq & Gemini Engines
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        with st.spinner("Executing Real-Time Agent reasoning on Groq platform..."):
            try:
                # Step 1: Query LLM for Tool Choice
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_query}
                    ],
                    model=model_name,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                raw_json = response.choices[0].message.content
                agent_decisions = json.loads(raw_json)
                
                st.markdown("### 🧠 Live LLM Agent Reasoning Trace")
                st.json(agent_decisions)
                
                # Step 2: Handle Tool Execution Dynamically
                tool_selected = agent_decisions.get("tool_to_use")
                tool_param = agent_decisions.get("tool_input")
                
                # Executing Image generation if targeted by Agent
                img_url_output = None
                if pic_source == "Upload My Own Picture" and uploaded_pic_base64:
                    img_url_output = uploaded_pic_base64
                    tool_result = f"Custom user portrait uploaded. Asset loaded successfully. Length: {len(img_url_output)}"
                elif tool_selected == "imagen_generator":
                    with st.spinner("Calling Imagen generator engine..."):
                        img_url_output = tool_imagen_generator(str(tool_param))
                        tool_result = f"Image generated successfully. Base64 string length: {len(img_url_output)}"
                elif tool_selected == "accent_corrector":
                    tool_result = tool_accent_detector(str(tool_param))
                elif tool_selected == "translation_tool":
                    if isinstance(tool_param, dict):
                        tool_result = tool_translation_haiti(tool_param.get("text", ""), tool_param.get("target_lang", "english"))
                    else:
                        tool_result = tool_translation_haiti(str(tool_param), "english")
                else:
                    tool_result = "No tools triggered by LLM core decision matrix."
                
                st.markdown("### 🛠️ Execution Observation Output")
                st.code(f"Observation Result: {tool_result}")
                
                if img_url_output:
                    st.image(img_url_output, caption="Active Portrait Asset", width=250)
                
                # Step 3: Synthesis of final result with observation context added
                synthesis_prompt = (
                    f"The tool output from execution is: '{tool_result}'. "
                    "Now compile the final clean response to the user. "
                    "CRITICAL: If the user requested a specific language in their original query, "
                    "you MUST output the final_answer in that same language."
                )
                
                final_response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_query},
                        {"role": "assistant", "content": raw_json},
                        {"role": "user", "content": synthesis_prompt}
                    ],
                    model=model_name,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                final_output_json = json.loads(final_response.choices[0].message.content)
                
                # Corrected block: Proper structure for try/except display
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                st.markdown("### 🏆 Live Agent Final Answer Output")
                final_answer_text = final_output_json.get("final_answer", "Processing Completed Successfully.")
                st.success(final_answer_text)
                
                # Browser-Native TTS Injection
                st.markdown(f"""
                <button onclick="speakText('{final_answer_text.replace("'", "\\'")}')" 
                        style="background-color: #8A2BE2; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px;">
                    🔊 Play Script Audio
                </button>
                <script>
                    function speakText(text) {{
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.lang = 'en-US'; // Defaulting to English, can be dynamic
                        window.speechSynthesis.speak(utterance);
                    }}
                </script>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# Bottom Branding Footer
st.markdown('<div class="main-footer">© GlobalInternet.py – Built by GESNER DESLANDES.</div>', unsafe_allow_html=True)
