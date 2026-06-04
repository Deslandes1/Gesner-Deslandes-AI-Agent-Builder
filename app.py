# ... existing code ...

# ================== Active Agent Tools ==================

# ... existing code ...

def tool_imagen_generator(prompt):
    # ... existing code ...
    # (Existing function remains as is)
    # ... existing code ...

def tool_generate_talking_video(image_url, script):
    """
    ARCHITECTURE STUB: Integration for Video Rendering APIs.
    To use this for real, register for a service like Replicate, HeyGen, or D-ID.
    """
    # This currently simulates the video generation rendering phase.
    # Replace the return string with an actual API call (e.g., requests.post to Replicate API)
    return f"VIDEO_RENDERING_STARTED: https://api.your-video-service.com/render?id=12345"

def tool_accent_detector(text):
    # ... existing code ...

# ================== Main Window Rendering ==================
# ... existing code ...

# ================== Sandbox UI Configuration ==================

# ... existing code ...

with col_sandbox:
    # ... existing code ...
    
    st.markdown("**Active Tools in Workspace:**")
    st.code("🔧 translation_tool\n🔧 accent_corrector\n🔧 imagen_generator\n🔧 generate_talking_video")
    
    # ... existing code ...

# Loop Execution Logic
if run_agent:
    # ... existing code ...
    
    else:
        # Live Run Mode utilizing actual Groq & Gemini Engines
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        with st.spinner("Executing Real-Time Agent reasoning..."):
            try:
                # Step 1: Query LLM for Tool Choice
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_query}
                    ],
                    model="llama-3.3-70b-versatile",
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
                
                # Handle Image, Accent, OR Video Request
                result_output = "No action taken."
                
                if tool_selected == "imagen_generator":
                    result_output = tool_imagen_generator(str(tool_param))
                elif tool_selected == "generate_talking_video":
                    # You can pass both the image reference and the script
                    result_output = tool_generate_talking_video("User_Provided_Image", str(tool_param))
                elif tool_selected == "accent_corrector":
                    result_output = tool_accent_detector(str(tool_param))
                
                st.markdown("### 🛠️ Execution Observation Output")
                st.code(f"Observation Result: {result_output}")
                
                # ... existing code ...
