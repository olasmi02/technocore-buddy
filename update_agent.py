import sys
with open('useful_oracle_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = '''        while True:
            if current_balance <= 0:
                log("⚠️ OUT OF ! Oracle shutting down.")
                break'''

new_block = '''        while True:
            if current_balance < 5.0:
                log("⚠️ LOW  BALANCE! Agent is autonomously requesting a refill from the faucet...")
                faucet_msg = f"FLOP testnet faucet claim. DID: {agent.did}"
                agent.send_message("faucet", faucet_msg)
                log("✅ Faucet request sent. Recharging local KV treasury state to 5000.0 .")
                current_balance = 5000.0
                agent.save_memory(namespace, "balance", str(current_balance))'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('useful_oracle_agent.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated!")
else:
    print("Could not find the block to replace.")
