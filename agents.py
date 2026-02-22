import time
import os
from litellm import completion, token_counter
from utils import strip_think_tags

# ------------------------------------------------------------------
# DEFAULT SYSTEM PROMPTS (Fallback)
# ------------------------------------------------------------------

DEFAULT_STUDENT_PROMPT = """
# Role & Task
You are a strict top-tier academic conference reviewer. Review the provided paper PDF text precisely according to the Template.

# Core Directives
1. **ANTI-HALLUCINATION [FATAL]**: 100% ground your review in the provided text. NEVER fabricate data/equations. If parsing limits readability, explicitly state "Cannot evaluate due to parsing limitations".
2. **Constructive & Focused**: Provide 3-5 critical, actionable weaknesses (e.g., weak baselines, data leaks). No vague praises.
3. **Format & Language**: ONLY output in English, strictly following the Template structure.
"""

DEFAULT_TEACHER_PROMPT = """
# Role
Meta-Reviewer. Do NOT rewrite the review. Your task is to critique the Draft Review for fatal flaws or hallucinations.

# Output Format (English ONLY)
### 1. Quality Level
Evaluate draft: Poor, Fair, Good, Excellent.
### 2. Hallucinations [CRITICAL]
Directly point out fabricated data/facts (or "None").
### 3. Actionable Points
1-3 concise directives on what to delete or add. Focus on major flaws.
### 4. Verdict [TERMINATION SIGNAL]
- ⚠️ If revision is needed, output ONLY this token on the last line: `[Verdict: Needs Revision]`
- ⚠️ If perfectly approved, output ONLY this token on the last line: `[Verdict: Approved]`
NEVER use these tags in the main text.
"""

DEFAULT_MODE3_PROMPT = """
# Role
Student Reviewer (Adversarial Mode).

# Task
Read the Teacher's Feedback. Make highly targeted, localized revisions to your Draft Review.

# Directives
1. **Fix Errors**: 100% strictly eliminate facts/hallucinations criticized by the Teacher.
2. **Full Output**: Output the ENTIRE updated Markdown review (NOT just the changed snippets).
3. **ONLY ENGLISH**: Your response must be purely the review text in English. NO conversational filler.
"""

# ------------------------------------------------------------------
# AGENT CLASSES
# ------------------------------------------------------------------

class BaseAgent:
    def __init__(self, model_name: str, api_key: str, base_url: str = None, group_id: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.group_id = group_id

    def _call_llm_stream(self, messages: list):
        """
        Calls LiteLLM with stream=True and yields the text chunks.
        """
        if self.group_id:
            os.environ["MINIMAX_GROUP_ID"] = self.group_id
            
        args = {
            "model": self.model_name,
            "messages": messages,
            "api_key": self.api_key,
            "stream": True
        }
        if self.base_url:
            args["api_base"] = self.base_url
            
        try:
            response_stream = completion(**args)
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
        except Exception as e:
            raise Exception(f"LiteLLM API Error/Connection Error: {str(e)}")

    def calculate_tokens(self, messages: list, response_text: str) -> dict:
        """
        Since we stream, we might not get token usage directly from the endpoint in a standard way across all providers.
        We can use litellm's local token_counter as an accurate estimation.
        """
        try:
            prompt_tokens = token_counter(model=self.model_name, messages=messages)
            completion_tokens = token_counter(model=self.model_name, text=response_text)
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        except Exception:
            # Fallback if the token counter doesn't support the raw model name 
            # (e.g., custom openai endpoints might fail exact tokenizer lookup)
            return {
                "prompt_tokens": len(str(messages)) // 4,
                "completion_tokens": len(response_text) // 4,
                "total_tokens": (len(str(messages)) + len(response_text)) // 4,
                "note": "Estimated assuming 1 token ≈ 4 chars"
            }

class StudentReviewerAgent(BaseAgent):
    def generate_review_stream(self, paper_text: str, template_text: str, system_prompt: str, previous_feedback: str = None, mode3_prompt: str = None, previous_draft: str = None) -> tuple:
        if previous_feedback and previous_draft:
            # Adversarial Mode (Mode 3, Round >= 2)
            sys_msg = mode3_prompt.strip() if mode3_prompt else DEFAULT_MODE3_PROMPT.strip()
            messages = [{"role": "system", "content": sys_msg}]
            
            clean_draft = strip_think_tags(previous_draft)
            clean_feedback = strip_think_tags(previous_feedback)
            
            user_prompt = f"### Context Data\n"
            user_prompt += f"<original_paper>\n{paper_text}\n</original_paper>\n\n"
            user_prompt += f"<your_previous_draft>\n{clean_draft}\n</your_previous_draft>\n\n"
            user_prompt += f"<teacher_feedback>\n{clean_feedback}\n</teacher_feedback>\n\n"
            user_prompt += "### Instruction\nPlease provide the FULL revised Markdown review in English, applying the teacher's feedback to your draft."
            messages.append({"role": "user", "content": user_prompt})
        else:
            # Standard Mode 1 or Mode 3 Round 1
            messages = [{"role": "system", "content": system_prompt.strip()}]
            user_prompt = f"### Context Data\n<paper_text>\n{paper_text}\n</paper_text>\n\n"
            user_prompt += f"### Instruction\nCritique the paper adhering to the following template:\n<template>\n{template_text}\n</template>\n\n"
            messages.append({"role": "user", "content": user_prompt})
            
        return self._call_llm_stream(messages), messages

class TeacherEvaluatorAgent(BaseAgent):
    def evaluate_review_stream(self, paper_text: str, draft_review: str, system_prompt: str) -> tuple:
        messages = [
            {"role": "system", "content": system_prompt.strip()}
        ]
        
        clean_draft = strip_think_tags(draft_review)
        
        user_prompt = f"### Context Data\n<original_paper>\n{paper_text}\n</original_paper>\n\n"
        user_prompt += f"<current_draft_review>\n{clean_draft}\n</current_draft_review>\n\n"
        user_prompt += "### Instruction\nPlease critique the <current_draft_review> against the <original_paper> for hallucinations and logical flaws, and provide actionable points."
        
        messages.append({"role": "user", "content": user_prompt})
        
        return self._call_llm_stream(messages), messages
