import re

with open('useful_oracle_agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('print("📡 HELPFUL ORACLE AGENT 📡".center(65))', 'print("=== HELPFUL ORACLE AGENT ===".center(65))')
text = text.replace('print("🚀 Starting Oracle Broadcast Loop', 'print("Starting Oracle Broadcast Loop')
text = text.replace('print("\n🛑 Oracle Agent Shutdown', 'print("\nOracle Agent Shutdown')

text = text.replace('log("⚠️ LOW  BALANCE!', 'log("LOW  BALANCE!')
text = text.replace('log("✅ Faucet request sent.', 'log("Faucet request sent.')
text = text.replace('log("⚠️ OUT OF !', 'log("OUT OF !')
text = text.replace('log("⚡ Fetching', 'log("Fetching')
text = text.replace('log(f"💸 Paid API', 'log(f"Paid API')
text = text.replace('log(f"✅ Live Pulse', 'log(f"Live Pulse')
text = text.replace('log("🏁 Run-once flag', 'log("Run-once flag')
text = text.replace('log(f"💤 Oracle resting', 'log(f"Oracle resting')
text = text.replace('log("❌ CRITICAL:', 'log("CRITICAL:')
text = text.replace('log(f"💰 Oracle Treasury:', 'log(f"Oracle Treasury:')

with open('useful_oracle_agent.py', 'w', encoding='utf-8') as f:
    f.write(text)
