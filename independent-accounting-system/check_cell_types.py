#!/usr/bin/env python3
"""Check actual cell types in database"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:GRRydiOlZsvNALSMpDVkmtDJuhbVQbCS@ballast.proxy.rlwy.net:38243/railway"
os.environ["DATABASE_URL"] = DATABASE_URL

engine = create_engine(DATABASE_URL)

print("Checking cell types in database...")
print("="*60)

with engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT cell_type FROM cells"))
    cell_types = [row[0] for row in result]

    print(f"\nFound {len(cell_types)} cell types:")
    for ct in cell_types:
        print(f"  - {ct}")

    print("\n" + "="*60)
    print("Add these to CellType enum in models/cell_models.py:")
    print()
    for ct in cell_types:
        enum_name = ct.upper().replace('-', '_')
        print(f'    {enum_name} = "{ct}"')
