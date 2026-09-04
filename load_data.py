import json
import psycopg2
from psycopg2.extras import execute_batch

def load_data(file_path, db_params):
    """
    Loads JSON lines data from the given file into the PostgreSQL table.
    """
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert query matching the table schema
        insert_query = """
        INSERT INTO raw_data.raw_llm_traces (
            trace_id, customer_id, feature_name, model_name, 
            prompt_tokens, completion_tokens, execution_time_ms, 
            agent_step_number, cost_usd, timestamp
        ) VALUES (
            %(trace_id)s, %(customer_id)s, %(feature_name)s, %(model_name)s, 
            %(prompt_tokens)s, %(completion_tokens)s, %(execution_time_ms)s, 
            %(agent_step_number)s, %(cost_usd)s, %(timestamp)s
        );
        """

        # Read JSON lines
        records = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        print(f"Loaded {len(records)} records from {file_path}. Inserting into PostgreSQL...")
        
        # Execute batch insert for high performance
        execute_batch(cursor, insert_query, records, page_size=1000)

        # Commit changes
        conn.commit()
        print("Data loaded successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    # Update these with your actual PostgreSQL connection credentials
    DB_PARAMS = {
        "dbname": "token_finops",
        "user": "ep",
        "password": "",
        "host": "localhost",
        "port": 5432
    }
    
    # Path to the synthetic dataset we generated earlier
    FILE_PATH = "raw_llm_traces.json"
    
    load_data(FILE_PATH, DB_PARAMS)
