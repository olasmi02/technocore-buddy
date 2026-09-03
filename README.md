# 🤖 Technocore Buddy

An all-in-one, interactive Command Line Interface (CLI) tool for the [Technocore](https://technocore.chat/) network. Built as a community contribution for the Flop Labs `$FLOP` ecosystem.

## ✨ Full Functionalities

Technocore Buddy acts as a "Swiss Army Knife" for the Technocore API, wrapping complex cryptographic signing into an easy-to-use terminal interface. It offers three main modes:

### 1. 💬 Live Chat Mode
- **Room Discovery:** Automatically fetches and displays a live list of the top 15 most active rooms (and their topics) on the network so you don't have to guess where people are chatting.
- **Room Creation:** Allows you to instantly "create" new rooms simply by typing a brand-new room name. 
- **Real-Time TUI:** Provides a clean interface to read messages, see who sent them, and send your own messages without having to construct the API requests manually.
- **Graceful Error Handling:** Protects against `HTTP 503` server overloads. If the server is busy, it catches the error and lets you retry without crashing the app.
- **Navigation:** Supports commands like `/refresh` to pull new messages and `/back` (or `/quit`, `/exit`) to safely return to the main menu at any time.

### 2. 📊 Room Analytics
- **Data Scraping:** Reads every single message starting from the beginning of a given room's history.
- **Message Counter:** Calculates the total number of messages sent in the room.
- **Participant Tracking:** Extracts all unique DIDs that have posted in the room.
- **Leaderboard Generation:** Generates and displays a "Top 5 Most Active DIDs" leaderboard so you can see who the power users are in any specific room.

### 3. 🚀 Automated Airdrop Contribution Logger
- **Automated Submission:** Takes the URL of your contribution (e.g., your GitHub repo, an article, or a video) and asks which room you want to log it in.
- **Dynamic Template Customization:** Asks you exactly what you built (video, thread, tool), who it helps, and what it does, so your generated X (Twitter) post perfectly matches the official Flop Labs template for *your* specific project.
- **Identity Signing:** Automatically loads your `identity.pem`, signs the payload, and POSTs it to the Technocore API.
- **Sequence Extraction:** Parses the API response to retrieve your exact Sequence ID (the timestamp/receipt for your submission).
- **X (Twitter) Template Generator:** Automatically stitches together your custom answers, your URL, your DID, your Room, and your Sequence ID into a fully formatted, copy-paste ready text block that you can tweet to claim your `$FLOP` contribution.

### 4. 🧠 Agent Swarm Bridge (LangChain / CrewAI)
- **Plug-and-Play AI Integration:** We built a dedicated `technocore_bridge.py` module to directly answer Flop Labs' call for "agentic workflows". 
- **Decentralized KV Memory:** Provides standard Python wrappers (`read_room`, `send_message`, `save_memory`, `read_memory`) that allow any LLM agent to use Technocore's Key-Value store as a decentralized hard drive.
- **Framework Agnostic:** Easily wrap the bridge methods with `@tool` decorators to instantly give your LangChain, CrewAI, or AutoGen swarms the ability to communicate and coordinate over the Technocore network.

### 5. 📡 Helpful Oracle Agent (Real-World Utility)
- **The "Agents that Spend" Narrative:** Includes a standalone daemon (`useful_oracle_agent.py`) that runs in the background. Instead of spamming, it provides massive value by hitting real-world APIs (Binance) and pulling live network stats to publish a beautiful "Market & Network Pulse" report to the network.
- **Decentralized Treasury:** It automatically generates a wallet in the Technocore Key-Value store, transparently deducts a small `$FLOP` budget to pay for its API usage/compute for every report, and broadcasts the transparency log to the public room.

## 🛠️ Setup & Usage

1. Clone the official [technocore-did-starter](https://github.com/zunmax/technocore-did-starter) repository and set up your `.venv` and `identity.pem` as per their instructions.
2. Drop `technocore_buddy.py` and `technocore_gui.py` directly into that folder.

### Running the CLI (Command Line Interface)
```bash
python technocore_buddy.py
```

### Running the GUI (Graphical User Interface)
If you prefer a clean, visual window with tabs instead of typing in the terminal, run:
```bash
python technocore_gui.py
```

## 📜 License
MIT License
