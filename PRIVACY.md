# Privacy Policy — Kunlun Growth Skills for Gemini CLI

**Effective Date:** November 26, 2026  
**Publisher:** Kunlun Growth ([https://kunlungrowth.com](https://kunlungrowth.com))  
**Support Contact:** [dasean@yeah.net](mailto:dasean@yeah.net)

## 1. Local-First Execution & Zero Telemetry
All skills, reference guides, and Python inspection scripts bundled in `kunlun-growth-skills` run **100% locally** inside your Gemini CLI environment.
- We do **not** collect, transmit, store, or sell any user prompts, local files, spreadsheets, documents, resumes, or diagnostic outputs.
- We do **not** embed any analytics trackers, telemetry beacons, or external network calls inside the bundled scripts.

## 2. Credentials & Sensitive Data
- This extension does not request, read, or transmit API keys, tokens, or personal credentials.
- The bundled `self-improving-agent` skill includes an explicit secret-detection guardrail (`scripts/memory_audit.py`) designed to block accidental persistence of API keys, tokens, phone numbers, or email addresses into local memory files.

## 3. Third-Party Services
When you invoke Gemini CLI with this extension enabled, your prompts are processed by the AI model provider you configured in Gemini CLI (Google Gemini API, Vertex AI, or Google Code Assist) under their respective terms of service and privacy policies.

## 4. Enterprise & Custom Deployments
For organizations requiring air-gapped deployments, custom skill packs, or enterprise AI workflow consulting, please contact [dasean@yeah.net](mailto:dasean@yeah.net) or visit [https://kunlungrowth.com](https://kunlungrowth.com).
