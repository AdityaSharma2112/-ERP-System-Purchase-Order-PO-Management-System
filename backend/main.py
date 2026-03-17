from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from model import *
from sqlmodel import Session,select,SQLModel
from database import engine,get_session
from sqlalchemy.orm import selectinload 

from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
from datetime import datetime, timedelta

from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from mongoDB import ai_logging_collection

load_dotenv()
GOOGLE_CLIENT_ID = "886045176737-1kmfr9bed4q0uivjbvhe10t7mrpjr8vt.apps.googleusercontent.com"
SECRET_KEY = "adityasharma"
client = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.getenv("GEMINI_API"))

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

security = HTTPBearer()
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms='HS256')
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid Token")

@app.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return user

@app.get('/vendors')
def vendors(session: Session=Depends(get_session)):
    return session.exec(select(Vendor)).all()

@app.get('/products')
def products(session: Session=Depends(get_session)):
    return session.exec(select(Product)).all()

@app.get('/dashboard')
def dashboard(session: Session = Depends(get_session), user=Depends(get_current_user)):
    purchaseOrders = session.exec(select(PurchaseOrder).options(selectinload(PurchaseOrder.vendor))).all()
    result = []

    for po in purchaseOrders:
        result.append({
            "id": po.id,
            "reference_no": po.reference_no,
            "vendor_name": po.vendor.name if po.vendor else None,
            "total_amount": po.total_amount,
            "status": po.status
        })

    return result

@app.post('/create-purchase-order')
def create_po(po_in:PurchaseOrderCreate, session: Session = Depends(get_session), user=Depends(get_current_user)):
    po = PurchaseOrder(
        reference_no=po_in.reference_no,
        vendor_id=po_in.vendor_id,
        status=po_in.status
    )
    sub_amount = 0
    items = []
    for item in po_in.items:
        sub_amount += item.price*item.quantity
        items.append(
            PurchaseOrderItem(
                product_id=item.product_id,
                price=item.price,
                quantity=item.quantity
        ))
    po.total_amount = round(sub_amount + round(sub_amount*0.05,2),2)
    po.items = items
    session.add(po)
    session.commit()
    session.refresh(po)
    notify_node(po_in.reference_no)
    return po

@app.post("/create-vendor")
def create_vendor(cv: Vendor, session: Session = Depends(get_session), user=Depends(get_current_user)):
    session.add(cv)
    session.commit()
    session.refresh(cv)
    return cv

@app.post('/create-product')
def create_product(cp: Product, session: Session = Depends(get_session), user=Depends(get_current_user)):
    session.add(cp)
    session.commit()
    session.refresh(cp)
    return cp

@app.post('/auto-description')
def create_description(ad: AutoDescription, user=Depends(get_current_user)):
    product_name = ad.product
    prompt = f"Generate a professional marketing description for a product. The description should be exactly 2 sentences, engaging, and highlight the product's benefits. Use the product name below: {product_name}"
    result = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    parsed_result = result.choices[0].message.content

    log_entry = {
        "user_id": user["email"],
        "product_name": product_name,
        "prompt": prompt,
        "model": "gemini-2.5-flash",
        "generated_description": parsed_result,
        "created_at": datetime.utcnow()
    }
    ai_logging_collection.insert_one(log_entry)

    return {"generated": parsed_result}

@app.post("/auth/google")
async def google_auth(data: dict):
    token = data["token"]
    idinfo = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )
    print(idinfo)
    email = idinfo["email"]
    name = idinfo["name"]
    payload = {
        "name":name,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    user_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )
    return {
        "token": user_jwt,
    }

def notify_node(po_rn):
    import requests
    print(po_rn)
    try:
        res = requests.post("http://localhost:3000/notify", json={
            "poRn": po_rn
        })
    except:
        print("Notification server not reachable")


