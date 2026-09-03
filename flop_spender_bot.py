import time
import json
import random
from datetime import datetime
from technocore_bridge import TechnocoreBridge

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def main():
    print("="*65)
    print("🤖 AUTONOMOUS $FLOP SPENDING AGENT 🤖".center(65))
    print("Demonstrating the 'Agents that Spend' narrative".center(65))
    print("="*65)
    
    # Initialize the Bridge we built earlier
    log("Initializing Agent Identity on Technocore...")
    agent = TechnocoreBridge("identity.pem")
    
    if not agent.priv_key:
        log("❌ CRITICAL: Cannot run autonomous agent in read-only mode.")
        log("Please ensure identity.pem is configured correctly.")
        return
        
    namespace = f"wallet-{agent.did[:8]}"
    room_name = "flop-compute-logs"
    
    # 1. Read existing balance from the decentralized KV Store
    log(f"Checking decentralized KV store ({namespace}) for $FLOP balance...")
    raw_balance = agent.read_memory(namespace, "balance")
    
    try:
        # The KV store returns {"value": "1000.0"}
        balance_data = json.loads(raw_balance)
        current_balance = float(balance_data.get("value", 1000.0))
    except:
        # If no wallet exists on the network yet, initialize a testnet budget
        log("No wallet found on network. Initializing with 1000.0 testnet $FLOP...")
        current_balance = 1000.0
        agent.save_memory(namespace, "balance", str(current_balance))

    log(f"💰 Current Budget: {current_balance} $FLOP")
    
    # Simulated agentic workflows that require "compute"
    tasks = [
        "Trained local LLM epoch",
        "Scraped real-time crypto sentiment",
        "Indexed Technocore lobby room",
        "Generated cryptographic zero-knowledge proof",
        "Optimized distributed routing tables"
    ]

    print("\n🚀 Starting Autonomous Spending Loop (Press Ctrl+C to stop)...\n")
    
    try:
        while True:
            if current_balance <= 0:
                log("⚠️ OUT OF $FLOP! Agent is halting operations. Please fund wallet.")
                break
                
            # 1. Select a task and calculate compute cost
            task = random.choice(tasks)
            cost = round(random.uniform(1.5, 5.5), 2)
            
            log(f"⚡ Executing compute task: '{task}'")
            time.sleep(3) # Simulate the agent doing heavy compute work
            
            # 2. Deduct cost
            current_balance = round(current_balance - cost, 2)
            log(f"💸 Spent {cost} $FLOP. New Balance: {current_balance}")
            
            # 3. Update KV Store (Persist the wallet state to the network)
            agent.save_memory(namespace, "balance", str(current_balance))
            
            # 4. Publish Proof of Work to the network
            report = f"🤖 [Agent PoW] Completed task: {task}. Consumed {cost} $FLOP for compute. Remaining budget: {current_balance} $FLOP."
            agent.send_message(room_name, report)
            log(f"✅ Proof of Work published to room: /r/{room_name}")
            
            # Sleep before next compute cycle
            sleep_time = random.randint(30, 60)
            log(f"💤 Agent sleeping for {sleep_time} seconds before next task...\n")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n🛑 Autonomous Agent Shutdown via User. Final state saved to KV Store.")

if __name__ == "__main__":
    main()
