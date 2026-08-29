import sys
import time
import urllib.request
from pathlib import Path

try:
    import technocore_agent
except ImportError:
    print("❌ Error: technocore_agent.py not found.")
    print("Please place this script in the same folder as technocore_agent.py")
    sys.exit(1)

def print_banner():
    print("\n" + "=" * 65)
    print("🤖 TECHNOCORE BUDDY 🤖".center(65))
    print("The ultimate Swiss Army Knife for the Technocore Network".center(65))
    print("=" * 65)

def menu():
    print_banner()
    print("1. 💬 Chat Mode (Read and send messages in a room)")
    print("2. 📊 Room Analytics (Extract stats and active users)")
    print("3. 🚀 Airdrop Contribution Logger (Automate your submission)")
    print("4. ❌ Exit")
    print()
    return input("Select an option (1-4): ").strip()

def show_rooms_list():
    print("\n📡 Fetching currently active rooms from Technocore...")
    try:
        req = urllib.request.Request('https://technocore.chat/rooms', headers={'User-Agent': 'technocore-did-starter/1.0.0'})
        data = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        lines = [line.strip() for line in data.split('\n') if line.strip() and not line.startswith('#')]
        
        print("\n--- 🌟 Top Active Rooms 🌟 ---")
        for line in lines[:15]:  # Show top 15 rooms
            parts = line.split()
            if not parts: continue
            room_path = parts[0]
            if room_path.startswith("/r/"):
                room_name = room_path[3:]
                # Try to extract the topic if it exists
                topic = line.split(' - ', 1)[1] if ' - ' in line else ''
                topic_str = f" - {topic}" if topic else ""
                print(f" • {room_name}{topic_str}")
    except Exception as e:
        print(f"⚠️ Could not fetch room list right now: {e}")

def chat_mode(identity_path):
    show_rooms_list()
    
    print("\n(💡 To CREATE a room, simply type a brand new name. It's created automatically!)")
    print("(Leave blank and press Enter to return to main menu)")
    room = input("Enter room name: ").strip()
    if not room: return
    
    print(f"\n--- Joining {room} ---")
    print("Type your message and press Enter.")
    print("Commands: /back to return to main menu | /refresh to pull new messages")
    
    # Load identity if they want to chat
    try:
        priv_key = technocore_agent.load_identity(Path(identity_path))
        did = technocore_agent.did_from_private_key(priv_key)
        print(f"Logged in as: {did[:16]}...")
    except Exception as e:
        print(f"Could not load identity (read-only mode): {e}")
        priv_key = None

    last_seq = 0
    
    def fetch_messages():
        nonlocal last_seq
        try:
            kwargs = {"limit": 15}
            if last_seq > 0:
                kwargs["since"] = last_seq
            
            resp = technocore_agent.read_room(room, **kwargs)
            msgs = resp.get("messages", [])
            for m in msgs:
                seq = m.get("seq")
                sender = m.get("from", "unknown")
                text = m.get("text", "")
                if seq is not None and seq > last_seq:
                    print(f"[{seq}] {sender[:12]}...: {text}")
                    last_seq = seq
        except Exception as e:
            print(f"⚠️ Error reading room (Server might be busy): {e}")

    # Initial fetch
    fetch_messages()
    
    while True:
        try:
            msg = input("\n[You]: ").strip()
            if not msg:
                continue
            if msg.lower() in ["/quit", "/back", "/exit", "/menu"]:
                print("Leaving room...")
                break
            elif msg.lower() == "/refresh":
                fetch_messages()
            else:
                if not priv_key:
                    print("Cannot send message: no identity loaded.")
                    continue
                # Send message
                try:
                    resp = technocore_agent.post_signed_message(priv_key, room, msg)
                    posted_seq = resp.get("posted", {}).get("seq", "unknown")
                    print(f"✅ Sent! (Sequence: {posted_seq})")
                    fetch_messages()
                except Exception as e:
                    print(f"❌ Failed to send message: {e}")
                    print("💡 Tip: The Technocore server often gets overloaded and returns HTTP 503. Just wait a few seconds and try again!")
        except KeyboardInterrupt:
            break

def analytics_mode():
    show_rooms_list()
    print("\n(Leave blank and press Enter to return to main menu)")
    room = input("Enter room name to analyze: ").strip()
    if not room: return
    
    print(f"\nFetching all messages for '{room}' (this might take a moment)...")
    
    all_messages = []
    last_seq = 0
    while True:
        try:
            resp = technocore_agent.read_room(room, since=last_seq, limit=100)
            msgs = resp.get("messages", [])
            if not msgs:
                break
            
            new_msgs = [m for m in msgs if m.get("seq", 0) > last_seq]
            if not new_msgs:
                break
                
            all_messages.extend(new_msgs)
            last_seq = max(m.get("seq", 0) for m in new_msgs)
            print(f"... loaded {len(all_messages)} messages so far", end="\r")
            time.sleep(0.5) # rate limit respect
        except Exception as e:
            print(f"\n⚠️ Error reading room (Server might be busy): {e}")
            print("Stopping fetch here. Displaying analytics for what was gathered so far.")
            break
            
    print(f"\n\n--- Analytics for {room} ---")
    print(f"Total Messages: {len(all_messages)}")
    
    if not all_messages:
        return
        
    senders = {}
    for m in all_messages:
        did = m.get("from", "unknown")
        senders[did] = senders.get(did, 0) + 1
        
    print(f"Unique Participants: {len(senders)}")
    print("\nTop 5 Most Active DIDs:")
    sorted_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)
    for i, (did, count) in enumerate(sorted_senders[:5], 1):
        print(f"  {i}. {did[:16]}... : {count} messages")
    print("-" * 30)

def logger_mode(identity_path):
    print("\n🚀 Automated Airdrop Contribution Logger 🚀")
    print("This will post your contribution URL to a room and generate your X (Twitter) post.\n")
    print("(Leave URL blank and press Enter to return to main menu)")
    
    url = input("Enter the public URL of your contribution (e.g. https://x.com/...): ").strip()
    if not url: return
    
    show_rooms_list()
    room = input("Enter the Technocore room to log this in (e.g. flop-alpha): ").strip()
    if not room: return
    
    try:
        priv_key = technocore_agent.load_identity(Path(identity_path))
        did = technocore_agent.did_from_private_key(priv_key)
    except Exception as e:
        print(f"Error loading identity: {e}")
        return
        
    print("\nSigning and publishing your contribution...")
    try:
        text = f"My $FLOP contribution: {url}"
        resp = technocore_agent.post_signed_message(priv_key, room, text)
        seq = resp.get("posted", {}).get("seq", "UNKNOWN")
        print(f"✅ Successfully published! Your sequence number is: {seq}")
        
        print("\n" + "="*55)
        print("🎉 YOUR X (TWITTER) POST TEMPLATE 🎉")
        print("Copy and paste the exact text below to claim your airdrop:")
        print("="*55)
        
        tweet = f"I just submitted my contribution for the $FLOP airdrop! 🤖\n\n"
        tweet += f"🔗 Contribution: {url}\n"
        tweet += f"🪪 DID: {did}\n"
        tweet += f"🏠 Room: {room}\n"
        tweet += f"🔢 Sequence: {seq}\n\n"
        tweet += f"@FlopLabs #Technocore #AI"
        
        print(tweet)
        print("="*55)
        
    except Exception as e:
        print(f"❌ Error publishing message: {e}")
        print("💡 Tip: The Technocore server is likely busy (HTTP 503). Try logging again in a minute!")

def main():
    # Assuming identity is stored in the default location
    identity_path = "identity.pem"
    while True:
        choice = menu()
        if choice == '1':
            chat_mode(identity_path)
        elif choice == '2':
            analytics_mode()
        elif choice == '3':
            logger_mode(identity_path)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")
        
        print() # visual padding

if __name__ == "__main__":
    main()
