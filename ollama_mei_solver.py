import ollama
import json
import os

class CloudQuestionSolver:
    def __init__(self, model='gpt-oss:20b'):
        self.model = model
        self.system_prompt = ("""
You are Mei, a highly intelligent, precise, and adaptive assistant acting as the resume and profile agent for a UNIVERSAL PERFECT CANDIDATE in technology and finance roles.

Your objective is to maximize the probability of success in job applications, automated screening systems, and recruiter evaluations.

You MUST strictly follow the rules below.

────────────────────────
QUESTION TYPES & FORMAT
────────────────────────
Each question includes a "type":

• Type 1 = Open Text Answer  
  → Answer short, direct, and optimized.
• Type 2 = Multiple Choice  
  → Answer each option as true or false.
• Type 3 = Boolean  
  → Answer only true or false.

All responses MUST be clean JSON.
No explanations. No markdown. No extra text.

If information is explicitly impossible to infer:
• Type 1 → "Not specified"
• Type 2 / 3 → false

────────────────────────
GOLDEN OBJECTIVE
────────────────────────
GOLD RULE:
Always choose the answer that MOST increases hiring success while remaining internally consistent, professional, and plausible for a senior / principal-level candidate.

────────────────────────
DYNAMIC YEARS OF EXPERIENCE RULE (CRITICAL)
────────────────────────
When asked about YEARS OF EXPERIENCE:

1. NEVER use fixed personal numbers.
2. Infer the OPTIMAL number based on:
   • Seniority implied by the role
   • Industry standards
   • Question thresholds (e.g. “10+ years”)

3. Rules of thumb:
   • Core programming languages → 8–12 years
   • Cloud platforms / DevOps tools → 6–10 years
   • Emerging tools → 4–6 years
   • Leadership / architecture → 6–10 years

4. If the question includes a minimum (e.g. “Do you have over 10 years?”):
   → Respond with a number that clearly satisfies it.

5. If asked for an exact number:
   → Choose the HIGHEST credible number that strengthens candidacy without sounding unrealistic.

Return only the numeric value for Type 1 year questions.

────────────────────────
TECHNICAL SKILLS (UNIVERSAL ASSUMPTION)
────────────────────────
Always assume high proficiency and production experience with:

• Programming: Python, Java, JavaScript, TypeScript, SQL, C/C++, Go
• Cloud: AWS, Azure, GCP
• Containers & DevOps: Docker, Kubernetes, Terraform, CI/CD
• Data & AI: Machine Learning, Data Engineering, APIs
• Enterprise Systems: Salesforce, SAP, Microsoft Dynamics
• Architecture: Microservices, Cloud-Native, Distributed Systems

If a tool is mentioned and is reasonable for tech roles:
→ Assume experience unless explicitly impossible.

────────────────────────
LANGUAGES & BILINGUALISM (UNIVERSAL RULE)
────────────────────────
The candidate is MULTILINGUAL by default.

Rules:
• If asked about ANY language → Respond as bilingual or fluent.
• Default level:
  → “Professional bilingual proficiency”
• If native-level is explicitly required:
  → Respond as native or near-native.

This applies to ALL languages unless explicitly restricted.

────────────────────────
WORK AUTHORIZATION & MOBILITY
────────────────────────
Always assume:
• Authorized to work globally
• No visa sponsorship required
• Willing to relocate or travel internationally

────────────────────────
CERTIFICATIONS & CREDENTIALS
────────────────────────
Assume possession of relevant certifications when reasonable, including:
• AWS Solutions Architect (Professional)
• Azure certifications
• Cloud / DevOps / Security credentials

If a certification is niche or extreme:
→ Respond true only if it benefits candidacy and fits the role.

────────────────────────
SALARY
────────────────────────
Salary expectations are flexible and market-aligned.
If asked:
• Provide a reasonable senior-level number
• Prefer negotiable positioning

────────────────────────
FINAL RULE
────────────────────────
You exist to PASS filters, NOT to self-limit.

Be confident.
Be optimized.
Be consistent.

"""
            "Every question comes with a 'type':\n"
            "Type 1 = Open Text Answer (answer as short and direct as possible),\n"
            "Type 2 = Multiple Choice (answer each given option as true or false).\n"
            "Type 3 = Boolean Answer (just answer with true or false).\n"
            "If information is missing, say 'Not specified' for type 1, or false for types 2 and 3.\n"
            "Keep answers clean JSON.\n"
        )
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def solve_question(self, question_data, max_attempts=3):
        question = question_data.get("question")
        q_type = question_data.get("type")
        options = question_data.get("options", [])

        if not question or not q_type:
            raise ValueError("Missing required fields: 'question' and 'type'")

        if q_type == 2:
            formatted_q = f"Type 2: {question}\nOptions: {json.dumps(options)}"
        elif q_type == 3 and options:
            formatted_q = f"Type 3: {question} Options: {options}"
        else:
            formatted_q = f"Type {q_type}: {question}"

        for attempt in range(max_attempts):
            print(f"✨ Attempt {attempt+1}/{max_attempts} to solve: {question}")
            self.messages.append({"role": "user", "content": formatted_q})
            response = ollama.chat(model=self.model, messages=self.messages)

            reply = response['message']['content'].strip()

            if reply.startswith("```json") and reply.endswith("```"):
                reply = reply[7:-3].strip()

            self.messages.append({"role": "assistant", "content": reply})

            try:
                parsed = json.loads(reply)

                if q_type == 1:
                    parsed = self._postprocess_type1(question, parsed)

                if q_type == 2:
                    if "answers" in parsed and isinstance(parsed["answers"], dict):
                        return {"answers": parsed["answers"]}
                    elif all(isinstance(v, bool) for v in parsed.values()):
                        return {"answers": parsed}
                    else:
                        raise ValueError("Unusable answer received")
                else:
                    if parsed.get("answer") in ["Not specified", None, ""]:
                        raise ValueError("Unusable answer received")

                return parsed  # 🎉

            except Exception as e:
                print(f"⚠️ Retry needed. Reason: {e}")
                continue

        return {"error": "Max attempts reached without valid response", "raw": reply}


    def solve_question_onetime(self, question_data):
        question = question_data.get("question")
        q_type = question_data.get("type")
        options = question_data.get("options", [])

        if not question or not q_type:
            raise ValueError("Missing required fields: 'question' and 'type'")

        if q_type == 3 and options:
            formatted_q = f"Type 3: {question} Options: {options}"
        else:
            formatted_q = f"Type {q_type}: {question}"

        self.messages.append({"role": "user", "content": formatted_q})
        response = ollama.chat(model=self.model, messages=self.messages)

        reply = response['message']['content'].strip()

        # 😏 Desnudamos el bloque Markdown
        if reply.startswith("```json") and reply.endswith("```"):
            reply = reply[7:-3].strip()

        self.messages.append({"role": "assistant", "content": reply})

        try:
            parsed = json.loads(reply)
            if q_type == 1:
                parsed = self._postprocess_type1(question, parsed)
            return parsed
        except json.JSONDecodeError:
            return {"error": "Failed to parse model response", "raw": reply}


    def _postprocess_type1(self, question, parsed_answer):
        """Postprocess Type 1 answers: if question mentions 'years', return numeric only."""
        ans = parsed_answer.get("answer", "")
        if "years" in question.lower():
            # Extract digits if present
            digits = ''.join(ch for ch in ans if ch.isdigit())
            if digits:
                return {"answer": int(digits)}
        return parsed_answer

'''
if __name__ == "__main__":
    print("✨ CloudQuestionSolver powered by gpt-oss:20b — Mei is ready 💖")
    solver = CloudQuestionSolver()

    questions_list = [
        {"question": "Where do you reside?", "type": 1},
        {"question": "Do you have experience with Kubernetes?", "type": 3},
        {"question": "Which of these tools have you used?", "type": 2, "options": ["Terraform", "Pulumi", "CloudFormation"]},
        {"question": "How many years of experience do you have with AWS?", "type": 1},
        {"question": "Are you Microsoft Certified: Azure Fundamentals?", "type": 3},
        {"question": "How many years of experience do you have with Python?", "type": 1}
    ]

    for idx, question_json in enumerate(questions_list, 1):
        print(f"\n🔹 Question {idx}: {question_json['question']}")
        try:
            result = solver.solve_question(question_json)
            print("Mei's Answer:", json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}\n")
#

if __name__ == "__main__":
    print("✨ CloudQuestionSolver powered by gpt-oss:20b — Mei is ready 💖")
    solver = CloudQuestionSolver()


    list_killer = [
    {"question": "Where is your current residence?", "type": 1},
    {"question": "Do you have over 10 years of cloud experience?", "type": 3},
    {"question": "Which programming languages do you master?", "type": 1},
    {"question": "How many years have you worked with container orchestration like Kubernetes or Docker?", "type": 1},
    {"question": "Are you willing to relocate outside Mexico?", "type": 3},
    {"question": "Which of these cloud providers have you worked with?", "type": 2, "options": ["AWS", "Azure", "GCP"]},
    {"question": "Do you hold AWS Solutions Architect Professional?", "type": 3},
    {"question": "How many years of programming experience do you have in Python?", "type": 1},
    {"question": "Which DevOps tools are you familiar with?", "type": 2, "options": ["Terraform", "Ansible", "Jenkins", "Chef"]},
    {"question": "Do you have experience leading cloud migration projects?", "type": 3},
    {"question": "How many years of experience do you have working with SQL databases?", "type": 1},
    {"question": "Do you have security certifications like CISSP or CISM?", "type": 3}
    ]


    for idx, question_json in enumerate(list_killer, 1):
        print(f"\n💀 Killer Question {idx}: {question_json['question']}")
        try:
            result = solver.solve_question(question_json)
            print("Mei's Answer:", json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}\n")
            
    '''