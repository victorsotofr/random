# A light version of my outreach assistant 

I have a deployed version of this outreach assistant that you can find on this [GitHub Repository](https://github.com/victorsotofr/uiform-outreach-assistant).

Here, you will find my "light" outreach assitant version = 3 files (watch + download + send in the `backend/scripts` folder) that I used to run from my terminal. I completed those 3 by a main.py which is a simple streamlit UI to orchestrate the whole thing.

- **GOAL**: automate and industrialize my personal outbound flow. 

Thing is, I was using classic tools to reach out to potential clients and drive growth — LinkedIn, Lusha, Attio, GoogleSheet, etc. etc.
However, the outbound strategy and process is quite personal: I found it a bit painful to use CRM tools that offered some flexibility but not up to the point that they could be perfectly integrated in the flow that I developed (especially because I was partly using my —Zimbra...— student email adress to do outboound aha).
That's why, with a few lines of code, I was able to create this light outreach assistant and reach out to thousands of people, get apointments and demos, and drive growth.

The principle:
1. I created an automation with **[uiform.com](https://uiform.com/)** — the automation is defined by 
    - an **Entry point** (in my case, a "bucket folder" that is my Downloads folder where the Screenshots of my profiles of interests were uploaded when taken)
    - an **Extraction schema** (that I defined in the Playground of uiform's website. It represents the main fields of information I wanted to get from the screens, e.g. first_name, last_name, email_adress, etc.)
    - an **Endpoint** (in my case, a GoogleSheet where all the extracted and structured data was uploaded).

    Note:
        - You need an **OPENAI_API_KEY** (or a key from your favorite model provider) to run your automation with uiform! 
        - You will get a **UIFORM_API_KEY** and a **UIFORM_API_ENDPOINT** to put in your .env

2. I start "watching" my bucker folder — each Screenshot that arrives in this folder will be processed by uiform, and the structured information taken from them will be sent to my endpoint (a GoogleSheet in my case).

3. I can review and then download my contact_list, that is "integrated" in my system and ready to trigger the sending.

4. I send the emails to my reviewed contact list, and tadam!

That's it for the flow. Maybe you have yours. The game is to personalize, improve, industrialize, grow grow grow.

---

## Security

- I stored my secrets in a classical `.env`. Here are the main stuff:
    - UIFORM_API_KEY
    - UIFORM_API_ENDPOINT
    - SMTP configuration (SMTP_USERNAME, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT) — that where my student email adress was involved

---



