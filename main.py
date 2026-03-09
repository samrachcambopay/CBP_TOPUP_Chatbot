# main.py — Cambopay Chatbot FastAPI Backend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import httpx, os

from database import connect_db, close_db, get_db
from models.schemas import ChatRequest, ChatResponse

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FRONTEND_URL      = os.getenv("FRONTEND_URL", "*")


# ─────────────────────────────────────────
# LIFESPAN (startup / shutdown)
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(title="Cambopay TOPUP Chatbot API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# HELPER: Build system prompt from MongoDB
# ─────────────────────────────────────────
async def build_system_prompt() -> str:
    db = get_db()

    endpoints     = await db["endpoints"].find({}, {"_id": 0}).to_list(100)
    parameters    = await db["parameters"].find({}, {"_id": 0}).to_list(200)
    resp_codes    = await db["response_codes"].find({}, {"_id": 0}).to_list(100)
    topup_amounts = await db["topup_amounts"].find({}, {"_id": 0}).to_list(50)
    signatures    = await db["signatures"].find({}, {"_id": 0}).to_list(20)
    soap_samples  = await db["soap_samples"].find({}, {"_id": 0}).to_list(20)

    # Format endpoints by service
    def fmt_endpoints(service):
        eps = [e for e in endpoints if e["service"] == service]
        return "\n".join(f"  {e['environment']} {e['method']}: {e['url']}" for e in eps)

    endpoint_text = f"""TOPUP:
{fmt_endpoints('Topup')}

TRANSACTION STATUS QUERY:
{fmt_endpoints('TransactionQuery')}

BALANCE QUERY:
{fmt_endpoints('Balance')}"""

    # Format parameters by API
    apis = list(dict.fromkeys(p["api"] for p in parameters))
    param_sections = []
    for api in apis:
        req = [p for p in parameters if p["api"] == api and p["direction"] == "Request"]
        res = [p for p in parameters if p["api"] == api and p["direction"] == "Response"]
        lines = [f"\n{api} REQUEST:"]
        for p in req:
            ex = f" | Example: {p['example']}" if p.get("example") else ""
            lines.append(f"  - {p['name']} ({p['data_type']}): {p['description']}{ex}")
        if res:
            lines.append(f"{api} RESPONSE:")
            for p in res:
                lines.append(f"  - {p['name']} ({p['data_type']}): {p['description']}")
        param_sections.append("\n".join(lines))
    param_text = "\n".join(param_sections)

    # Format response codes
    def fmt_codes(api):
        codes = [r for r in resp_codes if r["api"] == api]
        return "\n".join(
            f"  {r['code']} - {r['description']} | Refund: {'YES ⚠️' if r['refund_required'] else 'NO'} | Action: {r.get('action','')}"
            for r in codes
        )

    # Format topup amounts
    pinless_amt = "\n".join(
        f"  {t['operator']} ({t['product_code']}): ${t['min_amount']} – ${t['max_amount']}"
        for t in topup_amounts if t["type"] == "Pinless"
    )
    pincode_amt = "\n".join(
        f"  {t['operator']} ({t['product_code']}): ${', $'.join(str(int(d)) for d in t['denominations'])}"
        for t in topup_amounts if t["type"] == "Pincode"
    )

    # Format signatures
    sig_text = "\n".join(
        f"  {s['api']}: \"{s['sign_data']}\" → {s['encoding']} | {s.get('notes','')}"
        for s in signatures
    )

    # Format SOAP samples
    soap_text = "\n\n---\n\n".join(
        f"{s['api']} {s['direction']} (SOAPAction: \"{s['soap_action']}\"):\n{s['xml']}"
        for s in soap_samples
    )

    return f"""You are an expert AI assistant for Cambopay TOPUP Service SOAP API V2.
Help developers integrate with Cambopay's mobile top-up platform in Cambodia.
All knowledge below is fetched live from MongoDB Atlas.

=== API ENDPOINTS ===
{endpoint_text}

=== API PARAMETERS ===
{param_text}

=== RESPONSE CODES ===
PINLESS:
{fmt_codes('Pinless')}

PINCODE:
{fmt_codes('Pincode')}

=== TOPUP AMOUNTS ===
PINLESS (min / max, decimals supported):
{pinless_amt}

PINCODE (fixed denominations only):
{pincode_amt}

=== RSA SIGNATURE GUIDE ===
Algorithm: RSA 1024-bit, PKCS#1, SHA1withRSA
CRITICAL RULE: Topup APIs → BASE64 | Status & Balance APIs → HEX
{sig_text}

=== SOAP XML SAMPLES ===
{soap_text}

=== DATETIME FORMATS ===
- Topup LocalDateTime:       yyyyMMddHHmmss  (14 digits, full timestamp)
- Status query LocalDate:    yyyyMMdd        (8 digits, date ONLY — field is named "LocalDate" not "LocalDateTime")
- Balance LocalDateTime:     yyyyMMddHHmmss  (14 digits)

=== TRANSACTION CHANNELS ===
6011=ATM | 6012=TELLER | 6013=SMS | 6014=INTERNET | 6015=MOBILE

=== PYTHON SIGNATURE SAMPLE ===
import base64, datetime
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

def load_private_key(key_b64):
    return serialization.load_der_private_key(
        base64.b64decode(key_b64), password=None, backend=default_backend()
    )

def sign_base64(data: str, private_key_b64: str) -> str:
    \"\"\"Use for TopupV2 and GetCard (Topup requests)\"\"\"
    pk  = load_private_key(private_key_b64)
    sig = pk.sign(data.encode(), padding.PKCS1v15(), hashes.SHA1())
    return base64.b64encode(sig).decode()

def sign_hex(data: str, private_key_b64: str) -> str:
    \"\"\"Use for GetTranTopup, GetTranCard, GetBalance (Status/Balance)\"\"\"
    pk  = load_private_key(private_key_b64)
    sig = pk.sign(data.encode(), padding.PKCS1v15(), hashes.SHA1())
    return sig.hex()

# Example — Pinless TOPUP (BASE64):
ts        = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
plaintext = f"00000001-012345678-10.5-970418-123456789-6015-{{ts}}"
signature = sign_base64(plaintext, "YOUR_PRIVATE_KEY_BASE64")

# Example — Status Query (HEX):
local_date     = datetime.datetime.now().strftime("%Y%m%d")
status_plain   = f"00000001-012345678-10.5-970418-{{local_date}}"
signature_hex  = sign_hex(status_plain, "YOUR_PRIVATE_KEY_BASE64")

=== JAVA SIGNATURE SAMPLE ===
// SHA1withRSA — same algorithm as Python
Signature sig = Signature.getInstance("SHA1withRSA");
sig.initSign(privateKey);
sig.update(dataToSign.getBytes());
byte[] signed = sig.sign();

// For topup (BASE64):
String base64Sig = Base64.getEncoder().encodeToString(signed);

// For status/balance (HEX):
StringBuilder hex = new StringBuilder();
for (byte b : signed) hex.append(String.format("%02x", b));
String hexSig = hex.toString();

=== CONNECTION FLOW ERRORS ===
Error 1: Cambopay unreachable → Partner HTTP Timeout → Customer Timeout
Error 2: Telco unreachable from Cambopay → Cambopay Fail → Customer Fail
Error 3: Telco RC≠00 → Cambopay Fail Status → Customer Fail
Error 4: Telco OK but Cambopay can't receive response → Timeout to Partner
Error 5: Cambopay OK but Partner can't receive → Customer Timeout

FORMATTING RULES:
- Use tables for parameter lists
- Use code blocks with language labels for all code and XML
- Always clarify Base64 vs HEX when discussing signatures
- Always state refund requirement for every error code
- Distinguish LocalDate (yyyyMMdd) vs LocalDateTime (yyyyMMddHHmmss) clearly"""


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "message": "Cambopay TOPUP Chatbot API is running"}


# ── MAIN CHAT ENDPOINT ──
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages list is required")

    system_prompt = await build_system_prompt()
    env_note = f" (User is in {req.environment} mode — prefer {req.environment} URLs in examples.)"

    # Append env note to first user message
    messages = [
        {"role": m.role, "content": m.content + (env_note if i == 0 else "")}
        for i, m in enumerate(req.messages)
    ]

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "system": system_prompt,
                "messages": messages,
            },
        )

    data = response.json()
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"]["message"])

    reply = "".join(b["text"] for b in data["content"] if b["type"] == "text")
    return ChatResponse(reply=reply)


# ── ENDPOINTS ──
@app.get("/api/endpoints")
async def get_endpoints(environment: str = None, service: str = None):
    db = get_db()
    query = {}
    if environment: query["environment"] = environment
    if service:     query["service"]     = service
    data = await db["endpoints"].find(query, {"_id": 0}).to_list(100)
    return data


# ── PARAMETERS ──
@app.get("/api/parameters/{api}")
async def get_parameters(api: str, direction: str = None):
    db = get_db()
    query = {"api": api}
    if direction: query["direction"] = direction
    data = await db["parameters"].find(query, {"_id": 0}).to_list(100)
    return data


# ── RESPONSE CODES ──
@app.get("/api/response-codes")
async def get_response_codes(api: str = None, code: str = None):
    db = get_db()
    query = {}
    if api:  query["api"]  = api
    if code: query["code"] = code
    data = await db["response_codes"].find(query, {"_id": 0}).to_list(100)
    return data


# ── TOPUP AMOUNTS ──
@app.get("/api/topup-amounts")
async def get_topup_amounts(type: str = None, operator: str = None):
    db = get_db()
    query = {}
    if type:     query["type"]     = type
    if operator: query["operator"] = operator
    data = await db["topup_amounts"].find(query, {"_id": 0}).to_list(50)
    return data


# ── SIGNATURES ──
@app.get("/api/signatures")
async def get_signatures(api: str = None):
    db = get_db()
    query = {"api": api} if api else {}
    data = await db["signatures"].find(query, {"_id": 0}).to_list(20)
    return data


# ── SOAP SAMPLES ──
@app.get("/api/soap-samples/{api}")
async def get_soap_samples(api: str, direction: str = None):
    db = get_db()
    query = {"api": api}
    if direction: query["direction"] = direction
    data = await db["soap_samples"].find(query, {"_id": 0}).to_list(10)
    return data
