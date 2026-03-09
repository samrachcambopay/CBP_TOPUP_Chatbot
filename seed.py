# seed.py — Populate MongoDB Atlas with all Cambopay TOPUP API V2 data
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGODB_URI)
db = client["cambopay_chatbot"]


async def seed():
    print("🔗 Connecting to MongoDB Atlas...")

    # Clear all collections
    collections = ["endpoints", "parameters", "response_codes",
                   "topup_amounts", "signatures", "soap_samples"]
    for col in collections:
        await db[col].delete_many({})
    print("🗑️  Cleared old data")

    # ── 1. ENDPOINTS ──────────────────────────────────────────────
    await db["endpoints"].insert_many([
        # Topup
        {"environment": "UAT",        "method": "Private", "service": "Topup",            "url": "http://10.22.18.99/CambopayBank_T/CambopaySrv.asmx"},
        {"environment": "UAT",        "method": "Public",  "service": "Topup",            "url": "https://topuptestcam.vnpaytest.vn/CambopayBank_T/CambopaySrv.asmx"},
        {"environment": "Production", "method": "Private", "service": "Topup",            "url": "http://10.245.6.16/CambopayBank/CambopaySrv.asmx"},
        {"environment": "Production", "method": "Public",  "service": "Topup",            "url": "https://topup.cambopay.com.kh/CambopayBank/CambopaySrv.asmx"},
        # Transaction Status Query
        {"environment": "UAT",        "method": "Private", "service": "TransactionQuery", "url": "http://10.22.18.99/CambopayTranService_T/CambopaySrv.asmx"},
        {"environment": "UAT",        "method": "Public",  "service": "TransactionQuery", "url": "https://topuptestcam.vnpaytest.vn/CambopayTranService_T/CambopaySrv.asmx"},
        {"environment": "Production", "method": "Private", "service": "TransactionQuery", "url": "http://10.245.6.16/CambopayTranService/CambopaySrv.asmx"},
        {"environment": "Production", "method": "Public",  "service": "TransactionQuery", "url": "https://topup.cambopay.com.kh/CambopayTranService/CambopaySrv.asmx"},
        # Balance (same URLs as TransactionQuery)
        {"environment": "UAT",        "method": "Private", "service": "Balance",          "url": "http://10.22.18.99/CambopayTranService_T/CambopaySrv.asmx"},
        {"environment": "UAT",        "method": "Public",  "service": "Balance",          "url": "https://topuptestcam.vnpaytest.vn/CambopayTranService_T/CambopaySrv.asmx"},
        {"environment": "Production", "method": "Private", "service": "Balance",          "url": "http://10.245.6.16/CambopayTranService/CambopaySrv.asmx"},
        {"environment": "Production", "method": "Public",  "service": "Balance",          "url": "https://topup.cambopay.com.kh/CambopayTranService/CambopaySrv.asmx"},
    ])
    print("✅ Endpoints seeded (12 records)")

    # ── 2. PARAMETERS ──────────────────────────────────────────────
    await db["parameters"].insert_many([
        # ── TopupV2 Request ──
        {"api": "TopupV2", "direction": "Request",  "name": "Trace",               "data_type": "String",          "description": "Unique number (1-99999999), zero-pad to 8 chars",              "required": True,  "example": "00000001"},
        {"api": "TopupV2", "direction": "Request",  "name": "MobileNo",            "data_type": "String",          "description": "Customer mobile phone number",                                 "required": True,  "example": "012345678"},
        {"api": "TopupV2", "direction": "Request",  "name": "Amount",              "data_type": "Integer/Decimal", "description": "USD 1,2,5,6,10,20,50 or decimals e.g. 1.25, 1.5, 2.5",      "required": True,  "example": "10.5"},
        {"api": "TopupV2", "direction": "Request",  "name": "BankCode",            "data_type": "String",          "description": "Partner code provided by Cambopay",                           "required": True,  "example": "970418"},
        {"api": "TopupV2", "direction": "Request",  "name": "AccountNo",           "data_type": "String",          "description": "Bank or user account ID for reconciliation",                  "required": True,  "example": "123456789"},
        {"api": "TopupV2", "direction": "Request",  "name": "Channel",             "data_type": "String",          "description": "6011=ATM | 6012=TELLER | 6013=SMS | 6014=INTERNET | 6015=MOBILE", "required": True, "example": "6015"},
        {"api": "TopupV2", "direction": "Request",  "name": "LocalDateTime",       "data_type": "String",          "description": "Transaction datetime format yyyyMMddHHmmss",                   "required": True,  "example": "20250516100439"},
        {"api": "TopupV2", "direction": "Request",  "name": "Sign",                "data_type": "String",          "description": "RSA 1024-bit PKCS#1 SHA1withRSA BASE64 encoded signature",    "required": True,  "example": "BASE64_SIGNATURE"},
        # ── TopupV2 Response ──
        {"api": "TopupV2", "direction": "Response", "name": "RespCode",            "data_type": "String",          "description": "00=success, see response codes for others",                   "required": True},
        {"api": "TopupV2", "direction": "Response", "name": "MobileNo",            "data_type": "String",          "description": "Customer mobile phone number",                                 "required": True},
        {"api": "TopupV2", "direction": "Response", "name": "Trace",               "data_type": "String",          "description": "Trace number from request",                                    "required": True},
        {"api": "TopupV2", "direction": "Response", "name": "CambopayDateTime",    "data_type": "String",          "description": "Cambopay transaction datetime yyyyMMddHHmmss",                 "required": True},
        {"api": "TopupV2", "direction": "Response", "name": "LocalDateTime",       "data_type": "String",          "description": "Partner transaction datetime yyyyMMddHHmmss",                  "required": True},
        {"api": "TopupV2", "direction": "Response", "name": "Sign",                "data_type": "String",          "description": "RSA signature of response data",                               "required": True},
        # ── GetCard Request ──
        {"api": "GetCard", "direction": "Request",  "name": "Trace",               "data_type": "String",          "description": "Unique number (1-999999), zero-pad to 8 chars",                "required": True,  "example": "00000001"},
        {"api": "GetCard", "direction": "Request",  "name": "PartnerCode",         "data_type": "String",          "description": "Partner code provided by Cambopay",                           "required": True,  "example": "970418"},
        {"api": "GetCard", "direction": "Request",  "name": "ProductCode",         "data_type": "String",          "description": "MT=METFONE | ST=SEATEL | SM=SMART | MB=CELLCARD",             "required": True,  "example": "MT"},
        {"api": "GetCard", "direction": "Request",  "name": "Quantity",            "data_type": "Integer",         "description": "Number of pin cards to purchase",                              "required": True,  "example": "2"},
        {"api": "GetCard", "direction": "Request",  "name": "Amount",              "data_type": "Decimal",         "description": "Fixed denominations: USD 1,2,5,6,10,20,50",                   "required": True,  "example": "5"},
        {"api": "GetCard", "direction": "Request",  "name": "AccountNo",           "data_type": "String",          "description": "Reconciliation account",                                       "required": True,  "example": "123456789"},
        {"api": "GetCard", "direction": "Request",  "name": "Channel",             "data_type": "String",          "description": "6011=ATM | 6012=TELLER | 6013=SMS | 6014=INTERNET | 6015=MOBILE", "required": True, "example": "6015"},
        {"api": "GetCard", "direction": "Request",  "name": "LocalDateTime",       "data_type": "String",          "description": "Format yyyyMMddHHmmss",                                        "required": True,  "example": "20250516100439"},
        {"api": "GetCard", "direction": "Request",  "name": "Sign",                "data_type": "String",          "description": "RSA BASE64 signature",                                         "required": True},
        # ── GetTranTopup Request ──
        {"api": "GetTranTopup", "direction": "Request", "name": "Trace",           "data_type": "String",          "description": "Unique number (1-99999999), pad to 8 chars",                   "required": True},
        {"api": "GetTranTopup", "direction": "Request", "name": "MobileNo",        "data_type": "String",          "description": "Customer mobile number",                                       "required": True},
        {"api": "GetTranTopup", "direction": "Request", "name": "Amount",          "data_type": "Integer/Decimal", "description": "Transaction amount",                                           "required": True},
        {"api": "GetTranTopup", "direction": "Request", "name": "BankCode",        "data_type": "String",          "description": "Partner code",                                                 "required": True},
        {"api": "GetTranTopup", "direction": "Request", "name": "LocalDate",       "data_type": "String",          "description": "Date ONLY in yyyyMMdd format (NOT full timestamp!)",           "required": True,  "example": "20220727"},
        {"api": "GetTranTopup", "direction": "Request", "name": "Sign",            "data_type": "String",          "description": "RSA HEX encoded signature (NOT Base64!)",                     "required": True},
        # ── GetTranCard Request ──
        {"api": "GetTranCard", "direction": "Request",  "name": "Trace",           "data_type": "String",          "description": "Unique number, pad to 8 chars",                                "required": True},
        {"api": "GetTranCard", "direction": "Request",  "name": "PartnerCode",     "data_type": "String",          "description": "Partner code",                                                 "required": True},
        {"api": "GetTranCard", "direction": "Request",  "name": "ProductCode",     "data_type": "String",          "description": "MT | ST | SM | MB",                                            "required": True},
        {"api": "GetTranCard", "direction": "Request",  "name": "Quantity",        "data_type": "Integer",         "description": "Quantity of pins queried",                                     "required": True},
        {"api": "GetTranCard", "direction": "Request",  "name": "Amount",          "data_type": "Decimal",         "description": "Transaction amount",                                           "required": True},
        {"api": "GetTranCard", "direction": "Request",  "name": "LocalDate",       "data_type": "String",          "description": "Date ONLY yyyyMMdd (NOT full timestamp)",                      "required": True},
        {"api": "GetTranCard", "direction": "Request",  "name": "Sign",            "data_type": "String",          "description": "RSA HEX encoded signature",                                    "required": True},
        # ── GetBalance Request ──
        {"api": "GetBalance", "direction": "Request",   "name": "BankCode",        "data_type": "String",          "description": "Partner code provided by Cambopay",                           "required": True,  "example": "970418"},
        {"api": "GetBalance", "direction": "Request",   "name": "LocalDateTime",   "data_type": "String",          "description": "Format yyyyMMddHHmmss",                                        "required": True,  "example": "20250516100439"},
        {"api": "GetBalance", "direction": "Request",   "name": "Sign",            "data_type": "String",          "description": "RSA HEX of BankCode-LocalDateTime",                           "required": True},
        # ── GetBalance Response ──
        {"api": "GetBalance", "direction": "Response",  "name": "RespCode",        "data_type": "String",          "description": "00=success",                                                   "required": True},
        {"api": "GetBalance", "direction": "Response",  "name": "BankCode",        "data_type": "Number",          "description": "Partner code",                                                 "required": True},
        {"api": "GetBalance", "direction": "Response",  "name": "Balance",         "data_type": "Decimal",         "description": "Current partner balance in USD",                               "required": True},
        {"api": "GetBalance", "direction": "Response",  "name": "CambopayDateTime","data_type": "String",          "description": "Cambopay datetime yyyyMMddHHmmss",                             "required": True},
        {"api": "GetBalance", "direction": "Response",  "name": "LocalDateTime",   "data_type": "String",          "description": "Partner datetime yyyyMMddHHmmss",                              "required": True},
        {"api": "GetBalance", "direction": "Response",  "name": "Sign",            "data_type": "String",          "description": "RSA signature of response",                                    "required": True},
    ])
    print("✅ Parameters seeded")

    # ── 3. RESPONSE CODES ──────────────────────────────────────────
    await db["response_codes"].insert_many([
        # Pinless
        {"api": "Pinless", "code": "00", "description": "Transaction successful",                                         "refund_required": False, "action": "No action needed"},
        {"api": "Pinless", "code": "01", "description": "Provider system under maintenance",                              "refund_required": True,  "action": "Retry later and issue refund"},
        {"api": "Pinless", "code": "03", "description": "IP address is invalid",                                          "refund_required": True,  "action": "Whitelist your server IP with Cambopay"},
        {"api": "Pinless", "code": "05", "description": "Connection between Cambopay and partner/provider disconnected",  "refund_required": True,  "action": "Check network connectivity and retry"},
        {"api": "Pinless", "code": "06", "description": "Invalid LocalDateTime value",                                    "refund_required": True,  "action": "Ensure format is yyyyMMddHHmmss"},
        {"api": "Pinless", "code": "08", "description": "Transaction timed out — will be processed during reconciliation","refund_required": True,  "action": "Wait 60+ minutes then query transaction status"},
        {"api": "Pinless", "code": "09", "description": "Duplicate system trace detected",                                "refund_required": True,  "action": "Always use a unique Trace number per request"},
        {"api": "Pinless", "code": "12", "description": "Phone number invalid, restricted, or inactive",                  "refund_required": True,  "action": "Verify the customer mobile number"},
        {"api": "Pinless", "code": "13", "description": "Transaction amount is invalid",                                  "refund_required": True,  "action": "Check allowed amounts for the operator"},
        {"api": "Pinless", "code": "14", "description": "Transaction amount is invalid",                                  "refund_required": True,  "action": "Check allowed amounts for the operator"},
        {"api": "Pinless", "code": "20", "description": "Partner/bank code is invalid",                                   "refund_required": True,  "action": "Verify BankCode value with Cambopay"},
        {"api": "Pinless", "code": "79", "description": "RSA Signature is invalid",                                       "refund_required": True,  "action": "Check sign data format and Base64 encoding"},
        {"api": "Pinless", "code": "96", "description": "System error / exception case",                                  "refund_required": True,  "action": "Contact Cambopay support"},
        # Pincode
        {"api": "Pincode", "code": "00", "description": "Transaction successful",                                         "refund_required": False, "action": "No action needed"},
        {"api": "Pincode", "code": "01", "description": "Error from telecom provider",                                    "refund_required": True,  "action": "Retry later"},
        {"api": "Pincode", "code": "03", "description": "Invalid IP address",                                             "refund_required": True,  "action": "Whitelist your server IP with Cambopay"},
        {"api": "Pincode", "code": "05", "description": "System under maintenance",                                       "refund_required": True,  "action": "Retry later"},
        {"api": "Pincode", "code": "06", "description": "Invalid LocalDateTime value",                                    "refund_required": True,  "action": "Ensure format is yyyyMMddHHmmss"},
        {"api": "Pincode", "code": "08", "description": "Transaction timed out",                                          "refund_required": True,  "action": "Wait 60+ minutes then query transaction status"},
        {"api": "Pincode", "code": "09", "description": "Trace already exists or in invalid format",                      "refund_required": True,  "action": "Use a unique Trace number per request"},
        {"api": "Pincode", "code": "13", "description": "Invalid transaction amount",                                     "refund_required": True,  "action": "Use fixed denominations only: 1,2,5,6,10,20,50"},
        {"api": "Pincode", "code": "20", "description": "Invalid partner code",                                           "refund_required": True,  "action": "Verify PartnerCode with Cambopay"},
        {"api": "Pincode", "code": "62", "description": "Insufficient pin stock quantity",                                "refund_required": True,  "action": "Contact Cambopay to restock inventory"},
        {"api": "Pincode", "code": "79", "description": "Invalid RSA signature",                                          "refund_required": True,  "action": "Check sign data format and Base64 encoding"},
    ])
    print("✅ Response codes seeded")

    # ── 4. TOPUP AMOUNTS ──────────────────────────────────────────
    await db["topup_amounts"].insert_many([
        # Pinless
        {"type": "Pinless", "operator": "Cellcard", "product_code": "MB", "min_amount": 1, "max_amount": 999},
        {"type": "Pinless", "operator": "Metfone",  "product_code": "MT", "min_amount": 1, "max_amount": 100},
        {"type": "Pinless", "operator": "Seatel",   "product_code": "ST", "min_amount": 1, "max_amount": 500},
        {"type": "Pinless", "operator": "Smart",    "product_code": "SM", "min_amount": 1, "max_amount": 100},
        # Pincode
        {"type": "Pincode", "operator": "Smart",    "product_code": "SM", "denominations": [1, 2, 5, 10, 20]},
        {"type": "Pincode", "operator": "Seatel",   "product_code": "ST", "denominations": [1, 2, 5, 10, 20, 50]},
        {"type": "Pincode", "operator": "Metfone",  "product_code": "MT", "denominations": [1, 2, 5, 10, 20, 50]},
        {"type": "Pincode", "operator": "Cellcard", "product_code": "MB", "denominations": [1, 2, 5, 10, 20, 50]},
    ])
    print("✅ Topup amounts seeded")

    # ── 5. SIGNATURE GUIDE ──────────────────────────────────────────
    await db["signatures"].insert_many([
        {"api": "TopupV2",      "sign_data": "Trace-MobileNo-Amount-BankCode-AccountNo-Channel-LocalDateTime",                "encoding": "Base64", "algorithm": "RSA 1024-bit PKCS#1 SHA1withRSA", "notes": "Pinless topup request — Base64 output"},
        {"api": "GetCard",      "sign_data": "Trace-PartnerCode-ProductCode-Quantity-Amount-AccountNo-Channel-LocalDateTime", "encoding": "Base64", "algorithm": "RSA 1024-bit PKCS#1 SHA1withRSA", "notes": "Pincode topup request — Base64 output"},
        {"api": "GetTranTopup", "sign_data": "Trace-MobileNo-Amount-BankCode-LocalDate",                                     "encoding": "HEX",    "algorithm": "RSA 1024-bit PKCS#1 SHA1withRSA", "notes": "CRITICAL: LocalDate is yyyyMMdd only, NOT full timestamp. HEX output"},
        {"api": "GetTranCard",  "sign_data": "Trace-PartnerCode-ProductCode-Amount-LocalDate",                               "encoding": "HEX",    "algorithm": "RSA 1024-bit PKCS#1 SHA1withRSA", "notes": "CRITICAL: LocalDate is yyyyMMdd only. HEX output"},
        {"api": "GetBalance",   "sign_data": "BankCode-LocalDateTime",                                                       "encoding": "HEX",    "algorithm": "RSA 1024-bit PKCS#1 SHA1withRSA", "notes": "Balance query — HEX output"},
    ])
    print("✅ Signature guide seeded")

    # ── 6. SOAP SAMPLES ──────────────────────────────────────────
    await db["soap_samples"].insert_many([
        {
            "api": "TopupV2", "soap_action": "http://vnpay.vn/TopupV2", "direction": "Request",
            "xml": """POST /CambopayBank/CambopaySrv.asmx HTTP/1.1
Host: topup.cambopay.com.kh
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://vnpay.vn/TopupV2"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TopupV2 xmlns="http://vnpay.vn/">
      <Trace>00000001</Trace>
      <MobileNo>012345678</MobileNo>
      <Amount>10.5</Amount>
      <BankCode>970418</BankCode>
      <AccountNo>123456789</AccountNo>
      <Channel>6015</Channel>
      <LocalDateTime>20250516100439</LocalDateTime>
      <Sign>BASE64_SIGNATURE_HERE</Sign>
    </TopupV2>
  </soap:Body>
</soap:Envelope>"""
        },
        {
            "api": "GetCard", "soap_action": "http://vnpay.vn/GetCard", "direction": "Request",
            "xml": """POST /CambopayBank/CambopaySrv.asmx HTTP/1.1
Host: topup.cambopay.com.kh
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://vnpay.vn/GetCard"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetCard xmlns="http://vnpay.vn/">
      <Trace>00000001</Trace>
      <PartnerCode>970418</PartnerCode>
      <ProductCode>MT</ProductCode>
      <Quantity>2</Quantity>
      <Amount>5</Amount>
      <AccountNo>123456789</AccountNo>
      <Channel>6015</Channel>
      <LocalDateTime>20250516100439</LocalDateTime>
      <Sign>BASE64_SIGNATURE_HERE</Sign>
    </GetCard>
  </soap:Body>
</soap:Envelope>"""
        },
        {
            "api": "GetTranTopup", "soap_action": "http://vnpay.vn/GetTranTopup", "direction": "Request",
            "xml": """POST /CambopayTranService/CambopaySrv.asmx HTTP/1.1
Host: topup.cambopay.com.kh
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://vnpay.vn/GetTranTopup"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetTranTopup xmlns="http://vnpay.vn/">
      <Trace>00000001</Trace>
      <MobileNo>012345678</MobileNo>
      <Amount>10.5</Amount>
      <BankCode>970418</BankCode>
      <LocalDate>20220727</LocalDate>
      <Sign>HEX_SIGNATURE_HERE</Sign>
    </GetTranTopup>
  </soap:Body>
</soap:Envelope>"""
        },
        {
            "api": "GetBalance", "soap_action": "http://vnpay.vn/GetBalance", "direction": "Request",
            "xml": """POST /CambopayTranService/CambopaySrv.asmx HTTP/1.1
Host: topup.cambopay.com.kh
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://vnpay.vn/GetBalance"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBalance xmlns="http://vnpay.vn/">
      <BankCode>970418</BankCode>
      <LocalDateTime>20250516100439</LocalDateTime>
      <Sign>HEX_SIGNATURE_HERE</Sign>
    </GetBalance>
  </soap:Body>
</soap:Envelope>"""
        },
    ])
    print("✅ SOAP samples seeded")

    print("\n🎉 All data seeded into MongoDB Atlas successfully!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
