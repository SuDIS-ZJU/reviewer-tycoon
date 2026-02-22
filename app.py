import streamlit as st
import os
import time
from datetime import datetime
from utils import (
    parse_uploaded_file, truncate_text, generate_output_filename, 
    save_review, create_session_folder, save_origin_file, save_metadata, 
    format_file_link, strip_think_tags
)
from agents import (
    StudentReviewerAgent, TeacherEvaluatorAgent, 
    DEFAULT_STUDENT_PROMPT, DEFAULT_TEACHER_PROMPT, DEFAULT_MODE3_PROMPT
)
from dotenv import load_dotenv

# Load environment variables securely from .env file
load_dotenv()

# ------------------------------------------------------------------
# APP SETUP
# ------------------------------------------------------------------
st.set_page_config(page_title="Reviewer Tycoon: Clash of Agents", layout="wide", page_icon="🎢")

# Inject Cartoonish Fun CSS
st.markdown("""
<style>
    /* Playful rounded buttons */
    .stButton>button {
        border-radius: 25px !important;
        font-weight: bold;
        transition: transform 0.2s;
        border: 2px solid transparent;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        border: 2px solid #FFB6C1;
    }
    /* Rounded expanders with dashed borders */
    div[data-testid="stExpander"] {
        border-radius: 15px !important;
        border: 2px dashed #87CEEB !important;
    }
    /* Round inputs */
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎢 Reviewer Tycoon: Clash of the Agents 🥊")
st.markdown("🌟 基于多智能体的全自动学术论文评审与对抗进化系统 (Paper Grader Arcade Edition 👾)")

# ------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------------
if "logs" not in st.session_state:
    st.session_state.logs = []
if "sys_prompt_student" not in st.session_state:
    st.session_state.sys_prompt_student = DEFAULT_STUDENT_PROMPT.strip()
if "sys_prompt_teacher" not in st.session_state:
    st.session_state.sys_prompt_teacher = DEFAULT_TEACHER_PROMPT.strip()
if "sys_prompt_mode3" not in st.session_state:
    st.session_state.sys_prompt_mode3 = DEFAULT_MODE3_PROMPT.strip()
if "final_result" not in st.session_state:
    st.session_state.final_result = None

def log_to_console(msg: str):
    """Add a timestamped message to the console session state."""
    ts = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {msg}")

# ------------------------------------------------------------------
# GLOBAL CONFIGURATION EXPANDER
# ------------------------------------------------------------------
with st.expander("⚙️ Provider & Model Configuration", expanded=True):
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        api_key_default = os.getenv("API_KEY", "")
        api_key_type = "password" if api_key_default else "default"
        api_key = st.text_input("API Key", type="password", value=api_key_default, help="Enter your LLM API Key (defaults to .env)")
    with col_c2:
        model_name = st.text_input("Model Name", value=os.getenv("MODEL_NAME", "openai/minimax-m2.5"), help="e.g. gpt-4o, openai/minimax-m2.5")
    with col_c3:
        base_url = st.text_input("Base URL (Optional)", value=os.getenv("BASE_URL", "https://api.minimax.chat/v1"), help="Custom API Endpoint")
    with col_c4:
        group_id = st.text_input("Group ID (Optional)", value=os.getenv("GROUP_ID", ""), help="Required only for some Minimax endpoints")

# ------------------------------------------------------------------
# UI TABS
# ------------------------------------------------------------------
tab_exec, tab_prompts, tab_logs = st.tabs(["🚀 Execution Area", "🛠️ Prompt Engineering", "📊 System Logs"])

with tab_prompts:
    st.header("Customize System Prompts")
    st.info("💡 你可以在这里调整智能体的人设和行为约束。修改完成后请点击【保存】，新配置将在下次执行 Run Agent 时生效。")
    
    with st.form("prompt_form"):
        new_student = st.text_area("🎓 Student Reviewer Prompt", value=st.session_state.sys_prompt_student, height=200)
        new_teacher = st.text_area("🧑‍🏫 Teacher Evaluator Prompt", value=st.session_state.sys_prompt_teacher, height=200)
        new_mode3 = st.text_area("⚔️ Mode 3 Adversarial Prompt (For Student)", value=st.session_state.sys_prompt_mode3, height=100)
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            submitted = st.form_submit_button("💾 保存/Save")
        with col_btn2:
            reset = st.form_submit_button("🔄 恢复默认值/Reset to Defaults")
            
        if reset:
            st.session_state.sys_prompt_student = DEFAULT_STUDENT_PROMPT.strip()
            st.session_state.sys_prompt_teacher = DEFAULT_TEACHER_PROMPT.strip()
            st.session_state.sys_prompt_mode3 = DEFAULT_MODE3_PROMPT.strip()
            st.rerun()
            
        if submitted:
            st.session_state.sys_prompt_student = new_student
            st.session_state.sys_prompt_teacher = new_teacher
            st.session_state.sys_prompt_mode3 = new_mode3
            st.success("🎉 Prompts 保存成功！你可以前往 Execution Area 运行智能体了。")

with tab_exec:
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("📂 Uploads & Mode")
        mode = st.radio(
            "Select Working Mode:",
            ["Mode 1: Student Reviewer", "Mode 2: Teacher Evaluator", "Mode 3: Adversarial Mode"]
        )
        st.divider()
        pdf_file = st.file_uploader("1. Upload Paper (PDF) - 必填", type=["pdf"])
        
        # 动态控制组件启用/禁用状态
        disable_template = (mode == "Mode 2: Teacher Evaluator")
        disable_draft = (mode == "Mode 1: Student Reviewer")
        
        template_file = st.file_uploader(
            "2. Upload Template (TXT/MD) - Mode1/3需要", 
            type=["txt", "md"], 
            disabled=disable_template,
            help="在 Mode 2 中不需要此文件" if disable_template else ""
        )
        
        draft_file = st.file_uploader(
            "3. Upload Draft Review - Mode2/3需要", 
            type=["txt", "md", "docx"], 
            disabled=disable_draft,
            help="在 Mode 1 中不需要此文件" if disable_draft else ""
        )
        
        run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)
    
    with col_right:
        st.subheader("🖥️ Live Execution Stream")
        output_placeholder = st.empty()
        
        if run_button:
            if not api_key:
                st.error("Please enter your API Key in the settings.")
                st.stop()
            if not pdf_file:
                st.error("Please upload the target Paper (PDF).")
                st.stop()

            # Initialize directories
            session_id, session_dir, origin_dir = create_session_folder()
            log_to_console(f"Created new session: {session_id}")
            log_to_console(f"Session path: {session_dir}")

            # Save origin files
            paper_path = save_origin_file(pdf_file, origin_dir)
            template_path = save_origin_file(template_file, origin_dir) if template_file else None
            draft_path = save_origin_file(draft_file, origin_dir) if draft_file else None

            # Setup basic metadata
            session_metadata = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "mode": mode,
                "model": model_name,
                "base_url": base_url,
                "files": {
                    "paper": pdf_file.name if pdf_file else None,
                    "template": template_file.name if template_file else None,
                    "draft": draft_file.name if draft_file else None
                },
                "iterations": [],
                "total_cost_note": "Token tracking per iteration."
            }

            student_agent = StudentReviewerAgent(model_name, api_key, base_url if base_url else None, group_id if group_id else None)
            teacher_agent = TeacherEvaluatorAgent(model_name, api_key, base_url if base_url else None, group_id if group_id else None)
            
            with st.spinner("Extracting text from PDF..."):
                try:
                    paper_text = parse_uploaded_file(pdf_file)
                    paper_text = truncate_text(paper_text)
                    paper_title = os.path.splitext(pdf_file.name)[0]
                    log_to_console(f"Parsed PDF successfully: {paper_title}")
                except Exception as e:
                    st.error(f"Error parsing PDF: {e}")
                    st.stop()

            # Execute logic
            if mode == "Mode 1: Student Reviewer":
                if not template_file:
                    st.error("Please upload a Template for Mode 1.")
                    st.stop()
                
                template_text = parse_uploaded_file(template_file)
                log_to_console("Mode 1 Started: Student Base Review")
                
                try:
                    with st.expander("🤔 🎓 Student is writing the review (Click to collapse)", expanded=True):
                        stream_generator, used_messages = student_agent.generate_review_stream(
                            paper_text, template_text, st.session_state.sys_prompt_student
                        )
                        start_time = time.time()
                        full_response = st.write_stream(stream_generator)
                        duration = time.time() - start_time
                    
                    tokens = student_agent.calculate_tokens(used_messages, full_response)
                    
                    filename = generate_output_filename("Mode1", paper_title, "Student", 1)
                    filepath = save_review(session_dir, filename, full_response)
                    
                    st.success("✨ Generation Complete! You can copy or download the final review below.")
                    
                    clean_final_response = strip_think_tags(full_response)
                    st.session_state.final_result = {
                        "text": clean_final_response,
                        "filename": filename,
                        "label": "📥 Download Final Review (.md)"
                    }
                    
                    iter_meta = {
                        "round": 1, "agent": "Student", "duration_s": round(duration, 2),
                        "tokens": tokens, "output_file": filename
                    }
                    session_metadata["iterations"].append(iter_meta)
                    
                    log_to_console(f"✅ Mode 1 Finished in {duration:.2f}s! Tokens: {tokens.get('total_tokens')}")
                    log_to_console(f"Saved: {format_file_link(filepath)}")
                
                except Exception as e:
                    st.error(f"Error: {e}")

            elif mode == "Mode 2: Teacher Evaluator":
                if not draft_file:
                    st.error("Please upload a Draft Review for Mode 2.")
                    st.stop()
                    
                draft_text = parse_uploaded_file(draft_file)
                log_to_console("Mode 2 Started: Teacher Evaluation")
                
                try:
                    with st.expander("🤔 🧑‍🏫 Teacher is evaluating the draft (Click to collapse)", expanded=True):
                        stream_generator, used_messages = teacher_agent.evaluate_review_stream(
                            paper_text, draft_text, st.session_state.sys_prompt_teacher
                        )
                        start_time = time.time()
                        full_response = st.write_stream(stream_generator)
                        duration = time.time() - start_time
                    
                    tokens = teacher_agent.calculate_tokens(used_messages, full_response)
                    
                    filename = generate_output_filename("Mode2", paper_title, "Teacher", 1)
                    filepath = save_review(session_dir, filename, full_response)
                    
                    st.success("✨ Evaluation Complete! You can copy or download the evaluation below.")
                    
                    clean_final_response = strip_think_tags(full_response)
                    st.session_state.final_result = {
                        "text": clean_final_response,
                        "filename": filename,
                        "label": "📥 Download Teacher Evaluation (.md)"
                    }
                    
                    iter_meta = {
                        "round": 1, "agent": "Teacher", "duration_s": round(duration, 2),
                        "tokens": tokens, "output_file": filename
                    }
                    session_metadata["iterations"].append(iter_meta)
                    
                    log_to_console(f"✅ Mode 2 Finished in {duration:.2f}s! Tokens: {tokens.get('total_tokens')}")
                    log_to_console(f"Saved: {format_file_link(filepath)}")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

            elif mode == "Mode 3: Adversarial Mode":
                if not template_file and not draft_file:
                    st.error("Please upload either a Template or a Draft Review.")
                    st.stop()
                    
                log_to_console("Mode 3 Started: Adversarial Iteration")
                max_iters = 3
                current_review_text = parse_uploaded_file(draft_file) if draft_file else ""
                template_text = parse_uploaded_file(template_file) if template_file else "Standard Academic Review Structure (Motivation, Strengths, Weaknesses, Questions)"
                teacher_feedback_text = ""
                
                student_starts = not bool(draft_file) 
                
                # We will append UI elements to this container dynamically
                stream_container = st.container()
                
                passed = False
                error_occurred = False
                
                for i in range(1, max_iters + 1):
                    with stream_container:
                        st.divider()
                        st.subheader(f"🔄 Iteration Round {i}")
                    
                    if student_starts or i > 1:
                        log_to_console(f"Round {i}: Student working...")
                        with stream_container:
                            try:
                                with st.expander(f"🤔 🎓 Round {i}: Student Generation (Click to collapse)", expanded=True):
                                    start_time = time.time()
                                    stream_generator, used_messages = student_agent.generate_review_stream(
                                        paper_text, template_text, st.session_state.sys_prompt_student,
                                        previous_feedback=teacher_feedback_text,
                                        mode3_prompt=st.session_state.sys_prompt_mode3,
                                        previous_draft=current_review_text
                                    )
                                    current_review_text = st.write_stream(stream_generator)
                                    duration = time.time() - start_time
                                
                                tokens = student_agent.calculate_tokens(used_messages, current_review_text)
                                filename = generate_output_filename("Mode3", paper_title, "Student", i)
                                filepath = save_review(session_dir, filename, current_review_text)
                                
                                iter_meta = {
                                    "round": i, "agent": "Student", "duration_s": round(duration, 2),
                                    "tokens": tokens, "output_file": filename
                                }
                                session_metadata["iterations"].append(iter_meta)
                                log_to_console(f"✅ Student R{i} done ({duration:.1f}s, {tokens.get('total_tokens')} tk). {format_file_link(filepath)}")
                            except Exception as e:
                                st.error(f"Student Agent Generation Error: {e}")
                                error_occurred = True
                                break

                    # --- Teacher Phase ---
                    log_to_console(f"Round {i}: Teacher evaluating...")
                    with stream_container:
                        try:
                            with st.expander(f"🤔 🧑‍🏫 Round {i}: Teacher Evaluation (Click to collapse)", expanded=True):
                                start_time = time.time()
                                stream_generator, used_messages = teacher_agent.evaluate_review_stream(
                                    paper_text, current_review_text, st.session_state.sys_prompt_teacher
                                )
                                teacher_feedback_text = st.write_stream(stream_generator)
                                duration = time.time() - start_time
                                
                            tokens = teacher_agent.calculate_tokens(used_messages, teacher_feedback_text)
                            filename = generate_output_filename("Mode3", paper_title, "Teacher", i)
                            filepath = save_review(session_dir, filename, teacher_feedback_text)
                            
                            iter_meta = {
                                "round": i, "agent": "Teacher", "duration_s": round(duration, 2),
                                "tokens": tokens, "output_file": filename
                            }
                            session_metadata["iterations"].append(iter_meta)
                            log_to_console(f"✅ Teacher R{i} done ({duration:.1f}s, {tokens.get('total_tokens')} tk). {format_file_link(filepath)}")
                            
                            if "[Verdict: Approved]" in teacher_feedback_text:
                                log_to_console(f"🎉 Paper Passed at Round {i}.")
                                st.balloons()
                                st.success(f"🎉 恭喜！审稿过程在第 {i} 轮正式通过 (Passed)！")
                                
                                clean_final_review = strip_think_tags(current_review_text)
                                final_filename = generate_output_filename("Mode3_Final", paper_title, "Approved_Review", i)
                                save_review(session_dir, final_filename, clean_final_review)
                                
                                st.session_state.final_result = {
                                    "text": clean_final_review,
                                    "filename": final_filename,
                                    "label": "📥 Download Final Approved Review (.md)"
                                }
                                
                                passed = True
                                break
                        except Exception as e:
                            st.error(f"Teacher Evaluator API Error: {e}")
                            error_occurred = True
                            break
                            
                if error_occurred:
                    st.error("🚨 Adversarial iteration was aborted due to critical API errors. Please check your network or provider limits.")
                    log_to_console("Aborted due to API errors.")
                elif not passed:
                    log_to_console(f"⚠️ Reached max iterations limit ({max_iters}).")
                    st.warning(f"⚠️ Adversarial mode reached the maximum iteration limit ({max_iters}) without passing the Teacher's review (Status: Needs Revision).")

            # Finalize Metadata
            meta_path = save_metadata(session_dir, session_metadata)
            log_to_console(f"💾 Session metadata saved to: {format_file_link(meta_path)}")
            st.success("✨ Execution completed successfully! Check the System Logs tab for file links.")

        # Display final result unconditionally to survive reruns
        if st.session_state.final_result:
            st.markdown("### 🌟 Final Result")
            res = st.session_state.final_result
            st.download_button(label=res["label"], data=res["text"], file_name=res["filename"], mime="text/markdown")
            st.code(res["text"], language="markdown")

with tab_logs:
    st.header("Console Log Stream")
    if st.button("Clear Logs"):
        st.session_state.logs = []
        st.rerun()
    
    # We use markdown instead of text_area to support clickable links and basic formatting
    log_text_md = "\n\n".join(st.session_state.logs)
    if log_text_md:
        st.markdown(log_text_md)
    else:
        st.info("No logs yet. Run the agent to see execution details.")
