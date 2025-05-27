import os, json, datetime, base64, re, html
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI
import markdown2

LABEL = "news"
MAX_EMAILS = 50
MODEL = "gpt-4o"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
TO_EMAIL = os.environ["TO_EMAIL"]

def gmail_authenticate():
    creds_data = json.loads(os.environ["GMAIL_CREDS_JSON"])
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    return build("gmail", "v1", credentials=creds)

def plain_text_body(msg):
    parts = msg["payload"].get("parts", [msg["payload"]])
    for p in parts:
        if p["mimeType"].startswith("text/plain"):
            data = base64.urlsafe_b64decode(p["body"]["data"])
            return data.decode("utf-8", "ignore")
    data = base64.urlsafe_b64decode(parts[0]["body"]["data"])
    return re.sub(r"\s+", " ", html.unescape(data.decode("utf-8", "ignore")))

def split_chunks(text, size=10000):
    for i in range(0, len(text), size):
        yield text[i:i+size]

def map_reduce_summarize(text):
    chunks = list(split_chunks(text))
    partials = []
    for c in chunks:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": "Summarize the text into short bullets. Keep every number, name, and fact."},
                {"role": "user", "content": c}
            ]
        )
        partials.append(resp.choices[0].message.content)
    merged = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "Merge and deduplicate the following partial summaries."},
            {"role": "user", "content": "\n\n".join(partials)}
        ]
    )
    return merged.choices[0].message.content

def collect_email_facts(service):
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    query = f"label:{LABEL} after:{today}"
    res = service.users().messages().list(userId="me", q=query, maxResults=MAX_EMAILS).execute()
    messages = res.get("messages", [])
    facts = []
    for m in messages:
        full = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        subject = next((h["value"] for h in full["payload"]["headers"] if h["name"] == "Subject"), "(No subject)")
        body = plain_text_body(full)
        summary = map_reduce_summarize(body)
        facts.append({"subject": subject, "facts": summary})
    return facts

def final_digest(fact_packs):
    system_msg = (
        "You are writing a lunchtime news digest for a busy professional.\n"
        "Group the following into 2–6 themed sections.\n"
        "Merge topics that belong to the same sector (e.g. finance, AI, markets, health).\n\n"
        "For each theme, return:\n"
        "• A short **headline** (emoji + 2–5 word noun phrase)\n"
        "• 3–5 bullet points (≤25 words, no fluff, keep all numbers and names)\n"
        "• A **Sources** line (comma-separated subject lines)\n"
        "You must preserve every factually meaningful point.\n\n"
        "Return clean Markdown with:\n"
        "• Bold theme titles\n"
        "• Indented bullets\n"
        "• 1 blank line between themes\n"
    )
    user_input = json.dumps(fact_packs, ensure_ascii=False)
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        max_tokens=2000,
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_input}]
    )
    return resp.choices[0].message.content

def send_digest(service, summary_md, to_email):
    html = markdown2.markdown(summary_md)
    message = MIMEText(html, "html")
    message["to"] = to_email
    message["from"] = to_email
    message["subject"] = f"News at midi – {datetime.date.today():%d %b %Y}"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()

def main(request):
    gmail = gmail_authenticate()
    facts = collect_email_facts(gmail)
    if not facts:
        return "No emails today."
    digest = final_digest(facts)
    send_digest(gmail, digest, TO_EMAIL)
    return "Digest sent."
