# models/schemas.py — Pydantic schemas for all MongoDB collections
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ─────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────
class EnvironmentEnum(str, Enum):
    UAT        = "UAT"
    Production = "Production"

class MethodEnum(str, Enum):
    Private = "Private"
    Public  = "Public"

class ServiceEnum(str, Enum):
    Topup            = "Topup"
    TransactionQuery = "TransactionQuery"
    Balance          = "Balance"

class DirectionEnum(str, Enum):
    Request  = "Request"
    Response = "Response"

class ApiEnum(str, Enum):
    Pinless = "Pinless"
    Pincode = "Pincode"

class EncodingEnum(str, Enum):
    Base64 = "Base64"
    HEX    = "HEX"


# ─────────────────────────────────────────
# 1. API ENDPOINTS
# ─────────────────────────────────────────
class Endpoint(BaseModel):
    environment : EnvironmentEnum
    method      : MethodEnum
    service     : ServiceEnum
    url         : str

class EndpointCreate(Endpoint):
    pass


# ─────────────────────────────────────────
# 2. API PARAMETERS
# ─────────────────────────────────────────
class Parameter(BaseModel):
    api         : str          # e.g. TopupV2, GetCard, GetTranTopup
    direction   : DirectionEnum
    name        : str
    data_type   : str
    description : str
    required    : bool = True
    example     : Optional[str] = None

class ParameterCreate(Parameter):
    pass


# ─────────────────────────────────────────
# 3. RESPONSE CODES
# ─────────────────────────────────────────
class ResponseCode(BaseModel):
    api             : ApiEnum
    code            : str
    description     : str
    refund_required : bool = False
    action          : Optional[str] = None

class ResponseCodeCreate(ResponseCode):
    pass


# ─────────────────────────────────────────
# 4. TOPUP AMOUNTS
# ─────────────────────────────────────────
class TopupAmount(BaseModel):
    type          : ApiEnum
    operator      : str
    product_code  : Optional[str] = None
    min_amount    : Optional[float] = None   # Pinless only
    max_amount    : Optional[float] = None   # Pinless only
    denominations : Optional[List[float]] = None  # Pincode only

class TopupAmountCreate(TopupAmount):
    pass


# ─────────────────────────────────────────
# 5. SIGNATURE GUIDE
# ─────────────────────────────────────────
class Signature(BaseModel):
    api       : str
    sign_data : str
    encoding  : EncodingEnum
    algorithm : str = "RSA 1024-bit PKCS#1 SHA1withRSA"
    notes     : Optional[str] = None

class SignatureCreate(Signature):
    pass


# ─────────────────────────────────────────
# 6. SOAP SAMPLES
# ─────────────────────────────────────────
class SoapSample(BaseModel):
    api         : str
    soap_action : str
    direction   : DirectionEnum
    xml         : str

class SoapSampleCreate(SoapSample):
    pass


# ─────────────────────────────────────────
# 7. CHAT REQUEST/RESPONSE
# ─────────────────────────────────────────
class ChatMessage(BaseModel):
    role    : str  # "user" or "assistant"
    content : str

class ChatRequest(BaseModel):
    messages    : List[ChatMessage]
    environment : str = "UAT"

class ChatResponse(BaseModel):
    reply : str
