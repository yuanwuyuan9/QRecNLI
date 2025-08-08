## LLM-based User Simulation as Judge Evaluation for Baseline-Lux

### Key Components

This project provides a framework for conducting automated, AI-driven user studies on data exploration systems. It leverages Large Language Models (LLMs) in a two-step process:

1.  **Simulation (`LLM_simulation.py`)**: An "LLM Analyst Agent" simulates a data analyst interacting with a backend system, performing a series of exploratory queries based on a defined persona and goal.
2.  **Evaluation (`LLM_evaluation.py`)**: A second "LLM HCI Researcher Agent" analyzes the complete interaction log from the simulation and fills out a detailed user experience questionnaire, providing both quantitative scores and qualitative, evidence-based rationales.

### Simulation: How to test

#### 1. Start the back-end program of the Baseline-Lux system

See backend section  under `baseline-llm branch` for details.

#### 2. Path Configuration

##### (1) Backend Service Address

This simulation program needs to connect to a running Baseline-Lux backend service. In the `LLM_simulation.py` script, please modify the following variables at the beginning of the file to match your local or server environment.

```python
# --- 1. Configuration ---
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = "5012"
BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"
```

##### (2) Data Configuration

This simulation is configured to analyze a specific database, set by the `DB_ID` variable **on line 14**. The default is `"customers_and_addresses"`, which can be changed to suit your needs.

**Important**: All database interactions are handled by the backend service. Therefore, you must ensure that the database you select here is properly configured and accessible within your Baseline-Lux backend system.

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

Since our DeepSeek integration uses the OpenAI-compatible format, you only need to replace the code on **lines 18-29** with the OpenAI API-Key configuration as shown below, and also change the code `model="deepseek-chat" `on **line 186** to `model="gpt-4o"`.

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

Execute the `LLM_simulation.py` script. You can control the simulation mode (`use_lux=True` or `False`) and the number of turns inside the `if __name__ == "__main__":` block.

#### 4. Example output structure

This will produce a detailed log file named `simulation_log_with_lux_customers_and_addresses.json`. Alternatively, it is possible to see printed information about similar structures in the terminal.

```JSON
{
  "metadata": {
    "agent_persona": "You are a professional data analyst......",
    "agent_goal": "Analyze the 'customers_and_addresses' database.....",
    "db_id": "customers_and_addresses",
    "simulation_mode": "with_lux",
    "timestamp": "....."
  },
  "interaction_log": [
    {
      "turn": 0,
      "type": "cold_start",
      "decision": {
        "evaluation": "The database schema provides a comprehensive view......",
        "decision_rationale": "Option A (CHOOSE_RECOMMENDATION) is selected because......",
        "first_action_type": "CHOOSE_RECOMMENDATION",
        "first_query_text": "Show me all the different ways we can contact customers (like email, phone, etc.)."
      }
    },
    {
      "turn": 1,
      "type": "interaction",
      "system_response": {
        "sql": "SELECT DISTINCT channel_code FROM Customer_Contact_Channels;",
        "data": [......],
        "recommendations": [
          "Show me all the order IDs from the list of ordered items.",
          "Show me the quantities of all ordered items.",
          "Get the customer IDs from the customer contact channels.",
           ..........
        ]
      },
      "decision": {
        "new_insight": "The query result revealed that customers can......",
        "recommendation_evaluation": "The system's recommendations are useful......",
        "decision_rationale": "Given the insight gained about customer.....",
        "next_action_type": "FORMULATE_NEW",
        "next_query_text": "Show me the correlation between customer......"
      }
    },
    { "turn":2,
       ......
    },
   ]
 }
```

### Evaluation: How to test

Once the simulation log is generated, run the evaluation script. Make sure the `log_file_to_evaluate` variable in `LLM_evaluation.py` points to the correct log file. Or you can generate your own Json file with a similar structure for testing.

```Python
log_file_to_evaluate = "simulation_log_with_lux_customers_and_addresses.json"
```

```bash
Python LLM_evaluation.py
```

This will call the evaluator LLM and produce a final report named `simulation_log_with_lux_customers_and_addresses_EVALUATION.json`. It will also print a summary to your console.

#### Example output structure

```Json
{
    "Q1": {
        "score": 4,
        "rationale": "The system's suggestions are generally relevant....."
    },
    "Q2": {
        "score": 2,
        "rationale": "The system does not provide context-relevant suggestions......"
    },
    "Q3": {
        "score": 2,
        "rationale": "The system does not assist in deciding next-step explorations....."
    },
    ......
    "Q12": {
        "score": 5,
        "rationale": "The system is easy to use......"
    },
    "Q13": {
        "score": 5,
        "rationale": "The exploration path is logical and coherent......",
        "exploration_path": [
            "Exploration of customer contact methods (e.g., email, phone)",
            "Correlation analysis between contact methods and order statuses",
            "Investigation of delivery rates per contact channel",
            "Examination of correlation between delivery rates and payment methods",
            "Analysis of correlation between delivery rates and product types",
            "Deepened analysis of product type impact on delivery success"
        ]
    }
}
```

