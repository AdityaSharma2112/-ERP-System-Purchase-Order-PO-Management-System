"""
Database seeder — populates sample vendors, products, and a demo user.
Run: python seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import Vendor, Product

from sqlmodel import Session,select,SQLModel
from database import engine,get_session

SQLModel.metadata.create_all(bind=engine)


def seed():
    with Session(engine) as db:
        try:
            print("🌱 Seeding database...")
            # Vendors
            vendors_data = [
                {"name": "Acme Supplies Co.",
                "contact": "+1-555-0101",
                "rating": 4.5},
                {"name": "TechParts Global",
                "contact": "+1-555-0202",
                "rating": 4.8},
                {"name": "OfficeWorld Direct",
                "contact": "+1-555-0303",
                "rating": 3.9},
                {"name": "PrimeProcure Ltd.",
                "contact": "+1-555-0404",
                "rating": 4.2},
            ]
            for vd in vendors_data:
                if not db.query(Vendor).filter(Vendor.name == vd["name"]).first():
                    db.add(Vendor(**vd))
                    print(f"  ✓ Vendor: {vd['name']}")

            # Products
            products_data = [
                {"name": "Industrial Safety Gloves", "sku": "PPE-GLV-001",
                "unit_price": 12.99,
                "stock_level": 500,
                "description": "Heavy-duty nitrile gloves for industrial use"},
                {"name": "Laptop Stand Pro", "sku": "TECH-STD-201",
                "unit_price": 49.99,
                "stock_level": 120,
                "description": "Adjustable aluminum laptop stand"},
                {"name": "A4 Copy Paper (500 sheets)", "sku": "OFF-PPR-080",
                "unit_price": 8.50,
                "stock_level": 2000,
                "description": "80gsm premium white copy paper"},
                {"name": "Ergonomic Office Chair", "sku": "FURN-CHR-500",
                "unit_price": 349.00,
                "stock_level": 30,
                "description": "Lumbar-support mesh chair with armrests"},
                {"name": "Network Switch 24-Port", "sku": "NET-SWT-024",
                "unit_price": 189.99,
                "stock_level": 45,
                "description": "Managed Gigabit Ethernet switch"},
                {"name": "Industrial Drill Bits Set", "sku": "TOOL-DRL-SET",
                "unit_price": 34.99,
                "stock_level": 75,
                "description": "29-piece HSS drill bit set"},
                {"name": "Wireless Keyboard & Mouse", "sku": "TECH-KBM-WLS",
                "unit_price": 65.00,
                "stock_level": 200,
                "description": "2.4GHz wireless combo set"},
                {"name": "Safety Helmet Class E", "sku": "PPE-HLM-CE",
                "unit_price": 22.50,
                "stock_level": 300,
                "description": "ANSI-rated hard hat with ratchet suspension"},
            ]
            for pd in products_data:
                if not db.query(Product).filter(Product.sku == pd["sku"]).first():
                    db.add(Product(**pd))
                    print(f"  ✓ Product: {pd['name']} ({pd['sku']})")

            db.commit()
            print("\n✅ Seeding complete!")

        except Exception as e:
            db.rollback()
            print(f"\n❌ Seeding failed: {e}")
            raise
        finally:
            db.close()


if __name__ == "__main__":
    seed()