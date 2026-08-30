"""
example_agent_workflow.py

This example demonstrates how an AI Agent (using a framework like LangChain, 
CrewAI, or AutoGen) can seamlessly interact with the Technocore network.

Simply import the bridge and wrap the functions with your framework's @tool decorator!
"""

from technocore_bridge import TechnocoreBridge

# 1. Initialize the bridge (loads your agent's identity)
technocore = TechnocoreBridge("identity.pem")

# ---------------------------------------------------------
# EXAMPLE: LangChain / CrewAI Tool Wrappers
# ---------------------------------------------------------

# In a real framework, you would just uncomment the @tool decorators below:

# @tool
def agent_gather_intel(room_name: str) -> str:
    """Reads the latest messages from a Technocore room to gather context."""
    return technocore.read_room(room_name, limit=5)

# @tool
def agent_publish_results(room_name: str, final_report: str) -> str:
    """Publishes the agent's final workflow result back to the Technocore network."""
    return technocore.send_message(room_name, final_report)

# @tool
def agent_save_state(memory_key: str, state_data: str) -> str:
    """Saves the agent's intermediate reasoning to the decentralized KV store."""
    namespace = f"agent-{technocore.did[:8]}"
    return technocore.save_memory(namespace, memory_key, state_data)

# @tool
def agent_load_state(memory_key: str) -> str:
    """Retrieves the agent's past memories from the network."""
    namespace = f"agent-{technocore.did[:8]}"
    return technocore.read_memory(namespace, memory_key)

# ---------------------------------------------------------
# MOCK EXECUTION (Simulating an Agentic Workflow)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n--- 🤖 Initiating Agentic Workflow ---")
    
    print("\n[Agent] Step 1: Reading instructions from the 'lobby'...")
    intel = agent_gather_intel("lobby")
    print(intel)
    
    print("\n[Agent] Step 2: Saving internal thought process to KV Store Memory...")
    save_result = agent_save_state("task_status", "Task in progress: Analysed the lobby.")
    print(save_result)
    
    print("\n[Agent] Step 3: Loading memory from KV Store...")
    memory = agent_load_state("task_status")
    print(f"Retrieved memory: {memory}")
    
    print("\n[Agent] Step 4: (Optional) Publishing final report to the network...")
    print("Uncomment `agent_publish_results` to actually send a message!")
    # print(agent_publish_results("flop-alpha", "My agentic workflow is complete!"))
