<div align="center">
  <h1>🎢 Reviewer Tycoon: Clash of the Agents 🥊</h1>
  <p><strong>A Dual-Agent Academic Paper Review & Refinement System / 基于双智能体对抗的学术论文评审进化系统</strong></p>

  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Org-SuDIS-orange" alt="SuDIS" />
</div>

---

🇬🇧 **[English Version](#english-version)** | 🇨🇳 **[中文版本](#中文版本)**

---

<h2 id="english-version">🇬🇧 English Version</h2>

### 📖 Introduction

Welcome to **Reviewer Tycoon**, an automated, multi-agent AI framework designed for academic paper reviewing and refinement. Born out of the frustration of dealing with vague AI-generated reviews that hallucinate experiments and offer empty praises, this system introduces a "Left-hand vs. Right-hand" adversarial mechanism.

By pitting a rigorous **Student Reviewer Agent** against a highly critical **Teacher Meta-Reviewer Agent**, the system forces the review through multiple rounds of adversarial scrutiny. This process eliminates hallucinations and polishes the feedback until it becomes extremely sharp, actionable, and top-tier.

### 🌟 Key Features

1. **Dual-Agent Adversarial Architecture**: 
   - 🎓 **Student Reviewer**: Drafts the initial review based on the PDF and a strictly enforced conference template.
   - 🧑‍🏫 **Teacher Evaluator**: Scrutinizes the draft, acting as a ruthless Meta-Reviewer to point out factual errors and logical loopholes.
2. **Three Playing Modes**: 
   - Single-agent mode (Student Only or Teacher Only) and the fully automated **Adversarial Mode (Mode 3)**.
3. **Anti-Hallucination Engine**: Built-in `<think>` tag strippers and XML context limits completely eradicate reasoning-leakage and role confusion.
4. **Cartoonish UI**: A highly polished, engaging Streamlit Arcade-style UI 🎨.

### � Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Your API (Critical)**:
   Copy the environment template and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to include your `API_KEY` and `MODEL_NAME` (e.g., `openai/minimax-m2.5`). The system uses Litellm and supports any major provider.*
3. **Run the Arcade**:
   ```bash
   chmod +x start.sh
   ./start.sh
   # Or directly: streamlit run app.py
   ```

### 💡 Future Work & Call for Maintainers (SuDIS Lab)
This is currently an MVP, and there is immense potential to package it into an efficiency SaaS or publish a high-impact Tool Paper. **We are looking for passionate maintainers within the SuDIS GitHub Organization to take over!**

- **Review Memory (RAG)**: Inject real Accepted/Rejected review historical data so the agent learns to be sharper.
- **Multimodal Support**: Upgrade the pipeline to inherently read complex graphs and pipeline charts directly from the PDF.
- **Inference Optimization**: Leverage our lab's core expertise to optimize the multi-agent token lifecycle and inference speed.
- **Conference Template DB**: Build a one-click switching library for ICML, NeurIPS, CVPR, etc.

*Interested in owning a highly impactful open-source tool? Ping the author directly to get a demo and claim your ultimate resume booster! 💪*

---

<h2 id="中文版本">🇨🇳 中文版本</h2>

### 📖 项目起源

同学们，欢迎来到 **“Reviewer Tycoon”**（一个双 Agent 对抗的论文评审系统）。目前系统已经完全跑通了核心架构和超酷的 Web UI，效果极佳！🚀

**起因是啥？**
大家都知道，不管咱们自己投顶会前打磨本子，还是帮忙审稿，人工看 Draft 太痛苦了。但如果直接扔给大模型呢？它们往往尽说些讨好的废话，甚至还会瞎编实验（严重幻觉）。
所以本系统实现了一套“左右互搏”机制：我们配置了一个异常严厉的 **Teacher Agent**，专门给 **Student Agent** 写的 Review 疯狂挑刺。经过几轮底层对抗和打磨，强行把幻觉全部干掉，逼出来的评审意见极其锐利！这东西不仅咱们实验室能当效率神器，以后包装成 SaaS 插件或者发篇 Tool Paper 都很有想象空间。

### 🌟 核心功能

1. **双智能体对抗架构**: 
   - 🎓 **Student Reviewer (学生审稿人)**: 负责根据上传的 PDF 和顶会模板，起草最初的 Review。
   - 🧑‍🏫 **Teacher Evaluator (导师元审稿人)**: 极其刻薄的 Meta-Reviewer，专门挑刺、打回重写并且清理幻觉。
2. **三模运行机制**: 支持纯生成（Mode 1）、纯评价（Mode 2）以及最核心的全自动多轮打回重写模式（Mode 3）。
3. **硬核反幻觉引擎**: 底层强制挂载 `<think>` 标签清洗器和 `<xml>` 隔离舱，彻底封死大模型角色混淆的 Bug。
4. **游戏化 UI 界面**: 专门重构的 Cartoonish & Fun Streamlit 可视化大盘 🎨。

### 🚀 开箱即用指南

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
2. **配置 API 秘钥 (必做)**:
   复制环境模板并填入你的 Key，系统自带 `.gitignore` 保护，绝对安全：
   ```bash
   cp .env.example .env
   ```
   *编辑 `.env` 文件，填入你的 `API_KEY` 和 `MODEL_NAME`。系统底层基于 Litellm，无缝支持 Minimax, OpenAI, DeepSeek 等众多模型。*
3. **启动游乐场**:
   ```bash
   chmod +x start.sh
   ./start.sh
   # 或者直接运行: streamlit run app.py
   ```

### 💡 扩展方向 & 英雄帖 (SuDIS 实验室招募)
目前这是个初版 MVP，能玩的花活还有很多。**我准备把这套代码开源到咱们 SuDIS 的 GitHub Organization 里。热烈欢迎对大模型 Agent 开发、或者全栈搞事感兴趣的同学来接盘和主导本项目！** 当个高质量开源工具的 owner，绝对是简历上的超级加分项。💪

**划重点，待开发的超级特性：**
- **审稿记忆体 (RAG)**：用真实被拒/接收的 Review 风格喂给它，越审越毒舌。
- **多模态支持**：直接让大模型看懂论文里的复杂折线图和架构图。
- **降本增效优化**：结合咱们实验室的老本行，在多轮对抗下搞搞 Token 节约和推理加速体系。
- **顶会模板库**：支持一键切换各类顶会（ICML, ICLR, CVPR 等）的打分标准。

*👉 有兴趣的同学直接群里吱一声或私聊我，随时带你们跑个 Demo 体验一下！*
