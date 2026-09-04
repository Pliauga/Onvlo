import json
import random
import uuid
from datetime import datetime, timedelta

def generate_dataset(num_records, output_file):
    features = ["customer_support_agent", "code_reviewer", "invoice_parser"]
    
    # Define models with their dynamic pricing rates (per 1k tokens)
    models = {
        "gpt-4o": {"prompt_rate": 0.005, "completion_rate": 0.015},
        "claude-3-5-sonnet": {"prompt_rate": 0.003, "completion_rate": 0.015},
        "gpt-4o-mini": {"prompt_rate": 0.00015, "completion_rate": 0.0006},
    }
    model_names = list(models.keys())
    
    # 50 regular customers, 3 enterprise customers
    regular_customers = [f"CUST-{str(i).zfill(4)}" for i in range(1, 51)]
    enterprise_customers = ["ENT-0001", "ENT-0002", "ENT-0003"]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    records = []
    
    while len(records) < num_records:
        trace_id = str(uuid.uuid4())
        
        # Pick customer (enterprise customers have a higher chance of being picked to reflect high volume)
        is_enterprise = random.random() < 0.2
        customer_id = random.choice(enterprise_customers) if is_enterprise else random.choice(regular_customers)
        
        feature = random.choice(features)
        
        # Determine if this trace is an infinite loop (e.g. 2% chance)
        is_infinite_loop = random.random() < 0.02
        num_steps = random.randint(20, 35) if is_infinite_loop else random.randint(1, 8)
        
        # Base time for this trace
        trace_start_time = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
        
        for step in range(1, num_steps + 1):
            if len(records) >= num_records:
                break
                
            model_name = random.choice(model_names)
            rates = models[model_name]
            
            # Base tokens
            prompt_tokens = random.randint(50, 1000)
            completion_tokens = random.randint(10, 500)
            
            # Enterprise multiplier for massive token usage
            if customer_id in enterprise_customers:
                prompt_tokens *= random.randint(5, 25)
                completion_tokens *= random.randint(5, 25)
                
            # Infinite loop token spikes (agent context gets huge as steps increase)
            if is_infinite_loop:
                prompt_tokens += (step * random.randint(1000, 3000))
                
            execution_time_ms = completion_tokens * random.randint(10, 50) + random.randint(100, 500)
            
            # Dynamic pricing cost calculation
            cost_usd = (prompt_tokens / 1000.0) * rates["prompt_rate"] + (completion_tokens / 1000.0) * rates["completion_rate"]
            
            # Step timestamp
            step_timestamp = trace_start_time + timedelta(seconds=step * random.uniform(1, 10))
            
            record = {
                "trace_id": trace_id,
                "customer_id": customer_id,
                "feature_name": feature,
                "model_name": model_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "execution_time_ms": execution_time_ms,
                "agent_step_number": step,
                "cost_usd": round(cost_usd, 6),
                "timestamp": step_timestamp.isoformat() + "Z"
            }
            records.append(record)

    # Sort by timestamp to simulate realistic sequential logging
    records.sort(key=lambda x: x["timestamp"])
    
    with open(output_file, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')
            
    print(f"Generated {num_records} synthetic logs to {output_file}")

if __name__ == "__main__":
    generate_dataset(10000, "raw_llm_traces.json")
