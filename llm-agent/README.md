## LLM-based User Simulation as Judge Evaluation

### Key Components

This project provides a framework for conducting automated, AI-driven user studies on data exploration systems. It leverages Large Language Models (LLMs) in a two-step process:

1.  **Simulation (`LLM_simulation.py`)**: An "LLM Analyst Agent" simulates a data analyst interacting with a backend system, performing a series of exploratory queries based on a defined persona and goal.
2.  **Evaluation (`LLM_evaluation.py`)**: A second "LLM HCI Researcher Agent" analyzes the complete interaction log from the simulation and fills out a detailed user experience questionnaire, providing both quantitative scores and qualitative, evidence-based rationales.

### Simulation: How to test

#### 1. Start the back-end program of the QRec-NLI system

See backend section for details.

#### 2. Path Configuration

##### (1) Backend Service Address

This simulation program needs to connect to a running QRec-NLI backend service. In the `LLM_simulation.py` script, please modify the following variables at the beginning of the file to match your local or server environment.

```python
# --- 1. Configuration ---
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = "5012"
BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"
```

##### (2) Data Configuration

This simulation is configured to analyze a specific database, set by the `DB_ID` variable **on line 14**. The default is `"customers_and_addresses"`, which can be changed to suit your needs.

**Important**: All database interactions are handled by the backend service. Therefore, you must ensure that the database you select here is properly configured and accessible within your QRec-NLI backend system.

##### (3) LLM API Key

Set your LLM API key. You can either set it as an environment variable or directly replace the placeholder in the scripts.

##### Option A: Default Configuration: DeepSeek

By default, the simulation is configured to use the **DeepSeek** model. You just need to get your API key from the [DeepSeek website](https://www.deepseek.com/) and configure it in the code below.

```Python
# Replace with your key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
```

##### Option B: Switching to OpenAI (GPT-4o)

Since our DeepSeek integration uses the OpenAI-compatible format, you only need to replace the code on **lines 18-29** with the OpenAI API-Key configuration as shown below, and also change the code `model="deepseek-chat"`, on **line 186** to `model="gpt-4o"`.

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: Please set your OPENAI_API_KEY as an environment variable.")
    exit()
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    exit()
```

#### 3. Run the Simulation 

Execute the `LLM_simulation.py` script. You can control the simulation mode (`use_recommendations=True` or `False`) and the number of turns inside the `if __name__ == "__main__":` block.

#### 4. Example output structure

This will produce a detailed log file named `simulation_log_with_recs_customers_and_addresses.json`. Alternatively, it is possible to see printed information about similar structures in the terminal.

```JSON
{
  "metadata": {
    "agent_persona": "You are a professional data analyst...",
    "agent_goal": "Analyze the 'customers_and_addresses' database...",
    "simulation_mode": "with_recs",
    "timestamp": "..."
  },
  "interaction_log": [
    {
      "turn": 0,
      "type": "cold_start",
      "decision": {
        "evaluation": "The schema is straightforward and the initial recommendations are very helpful for starting an analysis.",
        "decision_rationale": "The recommendation 'Count customers by city' is an excellent starting point to understand the geographical distribution of the customer base. I will choose this one directly.",
        "first_action_type": "CHOOSE_RECOMMENDATION",
        "first_query_text": "Count customers by city"
      }
    },
    {
      "turn": 1,
      "type": "interaction",
      "system_response": {
        "sql": "SELECT T2.city, count(*) FROM customers AS T1 JOIN addresses AS T2 ON T1.cust_id  =  T2.cust_id GROUP BY T2.city",
        "data": [["New York", 12], ["Los Angeles", 9], ["Chicago", 5]],
        "recommendations": [
            "Show details for customers in New York",
            "What is the average age of customers by city?",
            "List the customers in Los Angeles"
        ]
      },
      "decision": {
        "new_insight": "The data shows that New York has the most customers (12), followed by Los Angeles (9). The customer base is concentrated in a few major cities.",
        "recommendation_evaluation": "The system's recommendations are highly relevant. Suggesting to 'Show details for customers in New York' is a perfect drill-down action after identifying it as the top city.",
        "decision_rationale": "Following the insight that New York is the top city, the logical next step is to examine the customers there in more detail. The first recommendation directly supports this analytical path.",
        "next_action_type": "CHOOSE_RECOMMENDATION",
        "next_query_text": "Show details for customers in New York"
      }
    }
  ]
}
```

### Evaluation: How to test

Once the simulation log is generated, run the evaluation script. Make sure the `log_file_to_evaluate` variable in `LLM_evaluation.py` points to the correct log file. Here, it is also possible to generate your own data for Evaluation following the format of the example output in the simulation section above.

```Python
log_file_to_evaluate = "simulation_log_with_recs_customers_and_addresses.json"
```

```bash
Python LLM_evaluation.py
```

This will call the evaluator LLM and produce a final report named `simulation_log_with_recs_customers_and_addresses_EVALUATION.json`. It will also print a summary to your console.

#### Example output structure

```Json
{
    "Q1": {
        "score": 5,
        "rationale": "The system provided excellent, topically relevant suggestions. In Turn 0, it suggested 'Count customers by city'......"
    },
    "Q2": {
        "score": 5,
        "rationale": "The system excelled at providing context-relevant suggestions. After the agent performed a GROUP BY city query in Turn 0, the system......"
    },
    // ... other questions ...
    "Q9": {
        "score": 5,
        "rationale": "The system made it very easy to review history and results, largely because the provided recommendations served as a clear guide for the next step."
    },
    // ... other questions ...
    "Q13": {
        "score": 5,
        "rationale": "The exploration path is highly logical and coherent. The agent's journey was effectively guided by the system's relevant recommendations......",
        "exploration_path": [
            "Analyze customer distribution by city",
            "Drill-down into details of customers in the top city (New York)"
        ]
    }
}
```


