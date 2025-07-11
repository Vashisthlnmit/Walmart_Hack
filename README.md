# 🧠 UnifiedBot – Intelligent Assistant for Budgeting, Inventory & Recipes
**UnifiedBot** is an intelligent, multi-functional assistant powered by **LangChain**, **LangGraph**, and LLM tools. It integrates three powerful agents:

- 🛒 **Budget-Friendly Shopping Assistant**
- 📦 **Stock & Inventory Analyzer**
- 🍳 **Recipe Generator using RAG and MealDB**

---

## 🚀 Features

| Bot                   | Functionality                                                                 |
|-----------------------|-------------------------------------------------------------------------------|
| 🛒 Budget Bot          | Suggests grocery items within your budget from inventory                     |
| 📦 Stock Analyzer Bot | Checks store inventory, performs stock updates, and generates invoices       |
| 🍳 Recipe Generator   | Recommends recipes using ingredients via MealDB API and vector store retrieval |

---
Each bot is built with LangGraph's state machine pattern and tool-aware agent execution.
## 🧩 Tech Stack

- **LangGraph** for multi-agent state management
- **LangChain** for LLM chaining and memory
- **Groq/OpenAI LLM** (via `LLM1`)
- **MealDB API** for recipe search
- **Vector Store** for RAG-based context
- **Fast API** for Server and Api Purpose
- **Custom Server** for simulating the inventory data stored on backend
---


