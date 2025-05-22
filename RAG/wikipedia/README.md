## RAG for Wikipedia Q&A (Zinedine Zidane)  

This project implements a **Retrieval-Augmented Generation (RAG) system** that scrapes **Wikipedia's "Zinedine Zidane" page** and allows users to ask questions about him. 

![Zidane World Cup 1998](https://cdn-s-www.dna.fr/images/10C48DB2-FD73-4432-82D0-2B1D09931117/MF_contenu/france-98-le-pere-de-zinedine-zidane-n-a-pas-vu-la-finale-1487178993.jpg)

The system retrieves relevant information from the Wikipedia article and generates responses using OpenAI's **GPT-4o-mini**.

---

## How It Works  

**Web Scraping**: Loads Zidane's Wikipedia page and extracts the main content.  
**Text Processing**: Splits the content into chunks for better indexing.  
**Vector Storage**: Stores processed text using OpenAI embeddings.  
**Retrieval-Augmented Generation**:  
  - Retrieves relevant text chunks based on the user's question.  
  - Uses GPT-4o-mini to generate answers from the retrieved content.  
**Interactive Chat**: Users can ask multiple questions and receive real-time responses.  

---

## Setup & Installation  

### 1. Install Dependencies  
Ensure you have Python and the required packages installed:  

```bash
pip install langchain langchain_openai langchain_core langchain_community bs4
```

### 2. Set Your OpenAI API Key  
Before running, set your OpenAI API key:  

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```
-> you can copy/paste it in a chat-box style.

### 3. Run the Script  
Start the interactive Q&A system:  

```bash
python script.py
```

---

## Usage Example  

```bash
Give us your question! I am stronger if we talk about Zidane ⚽️.

❓ Your question: Why did Zidane retire?
💡 Answer: Too painful to answer...
```

To exit, simply type **"exit"**.

---

## Notes  

- If the context does not contain the answer, GPT-4 will respond:
  *"I don't know based on the provided documents."*  
- This system is optimized for questions about Zidane, but can be modified for other topics.  

---

## Resources  

The main basis for the work was:
- **LangChain RAG Guide**: [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)

The useful resources were:
- **Wikipedia API**: [LangChain Wikipedia Loaders](https://python.langchain.com/docs/integrations/document_loaders/wikipedia/)  
- **Vector Stores**: [LangChain VectorStores](https://python.langchain.com/docs/concepts/vectorstores/)  

---

## Future Improvements  

- **Expand to multiple football players**  
- **Enhance document retrieval accuracy**  
- **Multi-language support**  

---

Zizou.

Worked with: ChatGPT, MistralAI
