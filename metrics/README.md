## Metrics: Coverage and Cohesion

### Modular Components

This functionality evaluates **Coverage** and **Cohesion** metrics using three core modules:

* `coverage_metrics.py`: Measures recommendation breadth using **Table, Column, Aggregation, and Clause Coverage**.
* `cohesion_metrics.py`: Evaluates the logical flow of a user's session with **Edit, Jaccard, Cosine, Common Fragments, and Common Tables Indices**.
* `main_evaluator.py`: The main script to orchestrate the evaluation and generate reports.

### Usage

#### 1. Path Configuration

Before running the evaluation, open the `main_evaluator.py` file and modify the path configuration section located at **lines 77-80**.

##### Configuration Code (in `main_evaluator.py`):
```python
# 1. Path to the directory containing user interaction data (session.json).
#    See section "2. Data Preparation" below for how to obtain this data.
USER_JSON_DIR = "./sample-data"

# 2. The name of the specific database schema folder to be analyzed.
DEFAULT_SCHEMA_FOLDER = "customers_and_addresses"

# 3. The base directory where all database schemas are stored.
SCHEMA_BASE_DIR = "../backend/app/data/dataset/spider/database"
```

#### 2. Data preparation

The data required for the **"USER_JSON_DIR"** variable can be obtained in one of two ways:

##### Option 1: Generate Data by Running the System

* **Run and Interact**: Launch and interact with our QRecNLI system.
* **Locate the Data**: The system will automatically save the complete interaction log as a `session.json file` in a specific directory (e.g., `backend/app/data/user/`).
* **Configure the Path**: Set the **"USER_JSON_DIR"** variable to the directory path containing the session.json file.

##### Option 2: Prepare Data Manually or Use the Sample

* **Manual Creation**: You can create your own `session.json` file by following the structure outlined in the **"Data Format Requirements"** section below.
* **Using the Sample Data**: For a quick start, we provide a ready-to-use sample in the `sample-data/` directory. **Simply set the USER_JSON_DIR path to `./sample-data`**.

#### 3. Data Format Requirements

Regardless of the method used, the final `session.json` file provided to the script must adhere to the following JSON structure.

```json
{
  "userdata": {
    "//": "Initial list of recommended queries at the start of the interaction",
    "origQuerySugg": {
      "sql": [
        "SELECT column1 FROM tableA;",
        "SELECT COUNT(*) FROM tableB;",
        "SELECT column2, column3 FROM tableA;"
      ]
    },
    "//": "List of user interaction steps",
    "suerQueryData": [
      {
        "//": "The query the user [selected] in this step",
        "SQL": {
          "sql": "SELECT column1 FROM tableA;"
        },
        "//": "New recommendations [generated] by the system after this step",
        "QuerySugg": {
          "sql": [
            "SELECT COUNT(column1) FROM tableA;",
            "SELECT column1 FROM tableA WHERE column1 = 'some_value';",
            "SELECT T1.column1, T2.column_other FROM tableA AS T1 JOIN tableB AS T2 ON T1.id = T2.id;"
          ]
        }
      },
      {
        "//": "Second step...",
        "SQL": {
          "sql": "SELECT T1.column1, T2.column_other FROM tableA AS T1 JOIN tableB AS T2 ON T1.id = T2.id;"
        },
        "QuerySugg": {
          "sql": []
        }
      }
    ]
  }
}
```

#### 4. Run metrics evaluation

```python
python main_evaluator.py
```

#### 5. Example output structure

After the evaluation script runs successfully, the results will be saved in the `results/` folder, which is created in your current working directory. The output format is as follows:

```text
============================================================
          Comprehensive Objective Metrics Evaluation Results
============================================================

--- Coverage Metrics ---
Table Coverage                     : 1.0000
Column Coverage                    : 0.8462
Aggregation Coverage               : 0.2000
Clause Coverage                    : 0.3333

--- Session Cohesion Metrics ---
Edit Index                         : 0.6000
Jaccard Index                      : 0.2500
Cosine Index                       : 0.8873
Common Fragments Index             : 0.1000
Common Tables Index                : 0.5000
============================================================
```