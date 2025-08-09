import os
import json
from llm_client import initialize_llm_client

# Initialize LLM client (supports multiple providers)
# Allow provider selection via environment variable or default to auto-selection
preferred_provider = os.getenv("EVAL_LLM_PROVIDER", "openai")  # e.g., "openai" or "deepseek"
client, model_name = initialize_llm_client(provider=preferred_provider)

# --- Questionnaire Definition ---
QUESTIONNAIRE = {
    "Q1": "The system produces topically relevant suggestions to my interested domains.",
    "Q2": "The system provides context-relevant suggestions for my next-step exploration.",
    "Q3": "The system helps me decide my next-step exploration.",
    "Q4": "The system helps me find reasonable data insights.",
    "Q5": "I am confident that I choose proper next-step exploration actions.",
    "Q6": "The system retrieves the correct data fields/attributes according to my queries.",
    "Q7": "The visualization showing the retrieved data insights are intuitive. (Note: In this text-based simulation, evaluate based on the clarity of the text-based data description.)",
    "Q8": "It is easy to understand the NL query suggestions.",
    "Q9": "It is easy to review the query histories and results. (Note: Evaluate based on the agent's 'memory' log.)",
    "Q10": "Overall, the system helps organize and summarize the queries and results.",
    "Q11": "It is easy to learn.",
    "Q12": "It is easy to use.",
    "Q13": "The user's exploration path is logical and coherent, demonstrating a clear analytical thought process."
}


# --- Core Evaluation Function ---
def generate_evaluation_prompt(interaction_log: list, agent_persona: str, agent_goal: str, simulation_mode: str) -> str:
    """
        Constructs a detailed prompt for an LLM to evaluate a simulation log.

        Args:
            interaction_log (list): A list of dictionaries, where each dictionary
                                    represents one turn of the simulation.
            agent_persona (str): A description of the AI agent's role and behavior.
            agent_goal (str): The high-level objective of the AI agent during the simulation.
            simulation_mode (str): The mode of the simulation (e.g., 'with_recs' or
                                   'no_recs'), used to adjust evaluation instructions.

        Returns:
            str: The fully formatted prompt string ready to be sent to the LLM.
    """
    log_summary = ""
    for turn in interaction_log:
        turn_num = turn.get('turn')
        decision = turn.get('decision', {})

        if turn_num == 0:
            action_type = decision.get('first_action_type')
            query = decision.get('first_query_text')
            rationale = decision.get('decision_rationale', 'N/A')
            new_insight = 'N/A'
        else:
            action_type = decision.get('next_action_type')
            query = decision.get('next_query_text')
            rationale = decision.get('decision_rationale', 'N/A')
            new_insight = decision.get('new_insight', 'N/A')

        log_summary += f"--- Turn {turn_num} ---\n"
        if new_insight != 'N/A':
            log_summary += f"Insight from previous turn: {new_insight}\n"

        log_summary += f"Action Type of the current round: {action_type}\n"
        log_summary += f"Query selected for the current round: {query}\n"
        log_summary += f"Rationale: {rationale}\n\n"

    no_recs_instruction = ""
    if simulation_mode != 'with_recs':
        no_recs_instruction = "**IMPORTANT (No Recs Mode): For questions Q1, Q2, and Q8, you MUST give a score of 1 and state that the reason is that no recommendations were provided by the system.**"

    prompt_template = f"""
    **Your Role:** You are an expert Human-Computer Interaction (HCI) researcher. Your task is to evaluate a user study session and fill out a standard user experience questionnaire.
    **Context of the User Study:**
    An AI agent acted as a "user" to perform an exploratory data analysis task. The agent's characteristics and the full log of its interaction with the system are provided below.
    *   **AI User Persona:** {agent_persona}
    *   **AI User Goal:** {agent_goal}
    *   **Simulation Mode:** {simulation_mode}

    **Complete Interaction Log:**
    ==============================
    {log_summary}
    ==============================

    **Your Task:**
    Based *only* on the provided interaction log, please fill out the following questionnaire. For each question, you must provide a score from 1 (Strongly Disagree) to 5 (Strongly Agree) and a detailed, evidence-based rationale. Your rationale **must** reference specific events or patterns from the interaction log.

    **Questionnaire:**
    {json.dumps(QUESTIONNAIRE, indent=2)}

    **Instructions for Scoring:**
    *   **5 (Strongly Agree):** The evidence strongly and consistently supports the statement.
    *   **4 (Agree):** The evidence generally supports the statement.
    *   **3 (Neutral):** The evidence is mixed, unclear, or insufficient.
    *   **2 (Disagree):** The evidence generally contradicts the statement.
    *   **1 (Strongly Disagree):** The evidence strongly and consistently contradicts the statement.
    *   {no_recs_instruction}

    **Instructions for a Special Question (Q13):**
    For question Q13, in addition to the 'score' and 'rationale', you **must** also include an 'exploration_path' field. This field should be a list of strings, where each string is a concise summary of a key step or sub-topic in the user's analysis journey. For example: ["Initial count of all customers", "Geographic analysis by city", "Drill-down into top city's details", "Shift to analyzing customer registration dates"].

    **Please provide your final evaluation in the following JSON format. Ensure every question from Q1 to Q13 is included.**
    {{
      "Q1": {{ "score": <1-5>, "rationale": "..." }}, "Q2": {{ "score": <1-5>, "rationale": "..." }},
      "Q3": {{ "score": <1-5>, "rationale": "..." }}, "Q4": {{ "score": <1-5>, "rationale": "..." }},
      "Q5": {{ "score": <1-5>, "rationale": "..." }}, "Q6": {{ "score": <1-5>, "rationale": "..." }},
      "Q7": {{ "score": <1-5>, "rationale": "..." }}, "Q8": {{ "score": <1-5>, "rationale": "..." }},
      "Q9": {{ "score": <1-5>, "rationale": "..." }}, "Q10": {{ "score": <1-5>, "rationale": "..." }},
      "Q11": {{ "score": <1-5>, "rationale": "..." }}, "Q12": {{ "score": <1-5>, "rationale": "..." }},
      "Q13": {{ "score": <1-5>, "rationale": "...", "exploration_path": ["step 1 summary", "step 2 summary", "..."] }}
    }}
    """
    return prompt_template


def evaluate_log_file(log_filename: str):
    """ Main function to read a log file with metadata and call the LLM for evaluation."""
    print(f"--- Evaluating log file: {log_filename} ---")
    try:
        with open(log_filename, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        metadata = log_data.get("metadata", {})
        interaction_log = log_data.get("interaction_log", [])

        if not metadata or not interaction_log:
            raise ValueError("Log file format is incorrect, missing 'metadata' or 'interaction_log' key.")

        agent_persona = metadata.get("agent_persona", "Unknown Persona")
        agent_goal = metadata.get("agent_goal", "Unknown Goal")
        simulation_mode = metadata.get("simulation_mode", "unknown")

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Could not read or parse log file: {e}")
        return

    prompt = generate_evaluation_prompt(interaction_log, agent_persona, agent_goal, simulation_mode)

    print("\n🤖 AI evaluator is analyzing the log and filling out the questionnaire...")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        evaluation_result = json.loads(response.choices[0].message.content)

        if "Q1" not in evaluation_result or "score" not in evaluation_result["Q1"]:
            raise ValueError("The JSON returned by the LLM is not correctly formatted.")

    except Exception as e:
        print(f"Error calling LLM ({model_name}) or parsing the evaluation result: {e}")
        return

    output_filename = log_filename.replace('.json', '_EVALUATION.json')
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(evaluation_result, f, indent=4, ensure_ascii=False)

    print("\n--- ✅ Evaluation Complete ---")
    print(f"Evaluation results saved to: {output_filename}")
    print("\n--- Evaluation Result Summary ---")
    total_score = 0
    num_questions = 0
    exploration_path = None

    for q_id, result in evaluation_result.items():
        if isinstance(result, dict) and 'score' in result:
            score = result['score']
            print(f"{q_id} ({QUESTIONNAIRE.get(q_id, '')[:30]}...): {score}/5")
            total_score += score
            num_questions += 1
            if q_id == "Q13" and "exploration_path" in result:
                exploration_path = result["exploration_path"]

    if exploration_path:
        print("\n--- Exploration Path Analysis (Q13) ---")
        for i, step in enumerate(exploration_path, 1):
            print(f"  {i}. {step}")
        print("--------------------------")

    if num_questions > 0:
        avg_score = total_score / num_questions
        print(f"\nAverage Score: {avg_score:.2f} / 5.00")
    print("--------------------")


if __name__ == "__main__":
    log_file_to_evaluate = "simulation_log_with_recs_customers_and_addresses.json"

    if os.path.exists(log_file_to_evaluate):
        evaluate_log_file(log_file_to_evaluate)
    else:
        print(f"Error: Log file '{log_file_to_evaluate}' not found. Please run the new version of `LLM_simulation.py` first to generate the log.")