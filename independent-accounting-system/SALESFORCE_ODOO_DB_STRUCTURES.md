# Salesforce & Odoo ERP Database Structures
## Comprehensive Integration Reference Guide

**Last Updated:** 2025-10-26
**Purpose:** Complete database schema reference for NERDX Independent Accounting System integration

---

## Table of Contents
1. [Salesforce Database Structure](#salesforce-database-structure)
2. [Odoo ERP Database Structure](#odoo-erp-database-structure)
3. [Integration Mapping](#integration-mapping)
4. [Best Practices](#best-practices)

---

## Salesforce Database Structure

### 1. Core Standard Objects

Salesforce organizes data using a relational model with standard objects (pre-built) and custom objects. The core CRM objects include:

- **Account**: Companies or individuals in business relationships
- **Contact**: Individuals within accounts
- **Opportunity**: Potential sales linked to accounts
- **Lead**: Unqualified sales prospects
- **Case**: Customer issues or inquiries
- **Product2**: Products in the catalog
- **Pricebook2**: Price books for products
- **PricebookEntry**: Junction between Product2 and Pricebook2
- **OpportunityLineItem**: Junction between Opportunity and PricebookEntry

---

### 2. Opportunity Object (Standard Fields)

**API Name:** `Opportunity`
**Purpose:** Represents potential sales transactions

#### Core Identification Fields
| Field API Name | Data Type | Description | Required |
|---|---|---|---|
| `Id` | ID | Unique identifier (18-char) | System |
| `Name` | String(120) | Opportunity name | Yes |
| `AccountId` | Reference | Related Account ID | Recommended |
| `OwnerId` | Reference | User who owns the opportunity | Yes |
| `RecordTypeId` | Reference | Record type for customization | No |

#### Sales Process Fields
| Field API Name | Data Type | Description | Critical |
|---|---|---|---|
| `StageName` | Picklist | Current sales stage | Yes |
| `CloseDate` | Date | Expected close date | Yes |
| `Probability` | Percentage | Likelihood of closing (0-100) | Auto-calc |
| `ForecastCategoryName` | String | Forecast category | Auto |
| `IsClosed` | Boolean | Whether opportunity is closed | Auto |
| `IsWon` | Boolean | Whether opportunity was won | Auto |

#### Financial Fields
| Field API Name | Data Type | Description | Key |
|---|---|---|---|
| `Amount` | Currency | Total opportunity amount | Recommended |
| `ExpectedRevenue` | Currency | Probability * Amount | Auto-calc |
| `TotalOpportunityQuantity` | Double | Total quantity across line items | No |

#### Classification Fields
| Field API Name | Data Type | Description |
|---|---|---|
| `Type` | Picklist | Opportunity type (New Business, Existing, etc.) |
| `LeadSource` | Picklist | How opportunity originated |
| `NextStep` | String(255) | Next action to take |
| `FiscalYear` | Integer | Fiscal year of close date |
| `FiscalQuarter` | Integer | Fiscal quarter (1-4) |

#### Campaign & Source Tracking
| Field API Name | Data Type | Description |
|---|---|---|
| `CampaignId` | Reference | Primary campaign source |
| `LeadSource` | Picklist | Original lead source |

#### System Fields
| Field API Name | Data Type | Description |
|---|---|---|
| `CreatedDate` | DateTime | When created |
| `CreatedById` | Reference | Who created |
| `LastModifiedDate` | DateTime | Last modification time |
| `LastModifiedById` | Reference | Who last modified |
| `SystemModstamp` | DateTime | System modification timestamp |
| `LastActivityDate` | Date | Date of last logged activity |
| `LastStageChangeDate` | Date | When stage last changed |

#### Relationship Fields
| Field API Name | Data Type | Relationship | Description |
|---|---|---|---|
| `AccountId` | Lookup | Account | Parent account |
| `Pricebook2Id` | Lookup | Pricebook2 | Price book for products |
| `ContactId` | Lookup | Contact | Primary contact (rarely used) |

---

### 3. OpportunityLineItem Object (Opportunity Products)

**API Name:** `OpportunityLineItem`
**Purpose:** Individual products/services on an opportunity
**Note:** Junction object between Opportunity and PricebookEntry

#### Core Fields
| Field API Name | Data Type | Description | Required |
|---|---|---|---|
| `Id` | ID | Unique identifier | System |
| `OpportunityId` | Reference | Parent opportunity | Yes |
| `PricebookEntryId` | Reference | Price book entry (includes product) | Yes |
| `Product2Id` | Reference | Product (read-only in API v30+) | Read-only |
| `Name` | String(255) | Line item name | Auto from Product |

#### Quantity & Pricing Fields
| Field API Name | Data Type | Description | Calculation |
|---|---|---|---|
| `Quantity` | Double | Quantity of product | Required |
| `UnitPrice` | Currency | Sales price per unit | User-entered |
| `TotalPrice` | Currency | Total line amount | Quantity × UnitPrice |
| `ListPrice` | Currency | List price from pricebook | Auto from PBE |
| `Discount` | Percentage | Discount percentage | Optional |

**Important Constraints:**
- Cannot update both `UnitPrice` and `TotalPrice` simultaneously
- If revenue schedule exists, `Quantity` and `TotalPrice` are read-only
- Updating `UnitPrice` recalculates `TotalPrice` = UnitPrice × Quantity
- Updating `TotalPrice` recalculates `UnitPrice` = TotalPrice / Quantity

#### Product Information
| Field API Name | Data Type | Description |
|---|---|---|
| `ProductCode` | String(255) | Product code from Product2 |
| `Description` | Text | Line item description |

#### Service & Schedule Fields
| Field API Name | Data Type | Description |
|---|---|---|
| `ServiceDate` | Date | Service/delivery date |
| `SortOrder` | Integer | Display order |

#### System Fields
| Field API Name | Data Type | Description |
|---|---|---|
| `CreatedDate` | DateTime | Creation timestamp |
| `CreatedById` | Reference | Creator user |
| `LastModifiedDate` | DateTime | Last modified timestamp |
| `LastModifiedById` | Reference | Last modifier user |
| `SystemModstamp` | DateTime | System modification |

---

### 4. Account Object

**API Name:** `Account`
**Purpose:** Companies or individuals (B2B or B2C)

#### Essential Fields for Revenue Tracking
| Field API Name | Data Type | Description |
|---|---|---|
| `Id` | ID | Unique identifier |
| `Name` | String(255) | Account name |
| `Type` | Picklist | Account type (Prospect, Customer, Partner) |
| `Industry` | Picklist | Industry classification |
| `AnnualRevenue` | Currency | Annual revenue |
| `NumberOfEmployees` | Integer | Employee count |
| `OwnerId` | Reference | Account owner |
| `ParentId` | Reference | Parent account (for hierarchies) |

---

### 5. Product2 Object

**API Name:** `Product2`
**Purpose:** Products and services catalog

#### Key Fields
| Field API Name | Data Type | Description |
|---|---|---|
| `Id` | ID | Unique identifier |
| `Name` | String(255) | Product name |
| `ProductCode` | String(255) | SKU or product code |
| `Description` | Text | Product description |
| `Family` | Picklist | Product family/category |
| `IsActive` | Boolean | Whether active for sale |

---

### 6. Salesforce Relationships & Data Flow

```
Account (1) ────→ (Many) Opportunity
                         ↓
                         ├──→ OpportunityLineItem (Many)
                         │              ↓
                         │         PricebookEntry (1)
                         │              ↓
                         │         Product2 (1)
                         │
                         └──→ CloseDate, Amount, StageName
```

**Key Integration Points for Revenue Tracking:**
1. **Opportunity.Amount** = Sum of all OpportunityLineItem.TotalPrice
2. **Opportunity.CloseDate** = Revenue recognition date
3. **Opportunity.StageName** = "Closed Won" indicates realized revenue
4. **OpportunityLineItem** provides detailed product-level revenue breakdown

---

## Odoo ERP Database Structure

### 1. Core Accounting Models

Odoo uses a double-entry bookkeeping system with these core models:

- **account.move**: Journal entries (invoices, bills, payments)
- **account.move.line**: Individual journal items (debits/credits)
- **account.account**: Chart of accounts
- **account.analytic.account**: Cost/revenue centers (for cell tracking)
- **account.analytic.line**: Analytic entries
- **res.partner**: Customers and vendors
- **product.product**: Products and services

---

### 2. account.move (Journal Entry / Invoice)

**Model Name:** `account.move`
**Purpose:** Represents accounting documents (invoices, bills, payments, journal entries)

#### Core Fields
| Field Name | Data Type | Description | Required |
|---|---|---|---|
| `id` | Integer | Primary key | System |
| `name` | String | Document number (auto-sequence) | Auto |
| `move_type` | Selection | Document type | Yes |
| `date` | Date | Accounting date | Yes |
| `invoice_date` | Date | Invoice date | For invoices |
| `invoice_date_due` | Date | Due date | For invoices |
| `state` | Selection | Draft/Posted/Cancel | System |

#### Move Types (move_type)
- `entry`: Journal entry
- `out_invoice`: Customer invoice
- `out_refund`: Customer credit note
- `in_invoice`: Vendor bill
- `in_refund`: Vendor refund
- `out_receipt`: Sales receipt
- `in_receipt`: Purchase receipt

#### Partner & Account Fields
| Field Name | Data Type | Description |
|---|---|---|
| `partner_id` | Many2one(res.partner) | Customer or vendor |
| `journal_id` | Many2one(account.journal) | Journal (sales, purchase, bank, etc.) |
| `currency_id` | Many2one(res.currency) | Transaction currency |
| `company_id` | Many2one(res.company) | Company (multi-company) |

#### Financial Fields
| Field Name | Data Type | Description |
|---|---|---|
| `amount_untaxed` | Monetary | Subtotal before tax |
| `amount_tax` | Monetary | Total tax amount |
| `amount_total` | Monetary | Grand total |
| `amount_residual` | Monetary | Remaining balance (for payments) |

#### Line Items
| Field Name | Data Type | Description |
|---|---|---|
| `line_ids` | One2many(account.move.line) | Journal items (debits/credits) |
| `invoice_line_ids` | Computed | Subset of line_ids for invoice lines |

#### System Fields
| Field Name | Data Type | Description |
|---|---|---|
| `create_date` | DateTime | Creation timestamp |
| `create_uid` | Many2one(res.users) | Creator |
| `write_date` | DateTime | Last modification |
| `write_uid` | Many2one(res.users) | Last modifier |

---

### 3. account.move.line (Journal Item / Invoice Line)

**Model Name:** `account.move.line`
**Purpose:** Individual debit/credit entries within a journal entry
**Inherits:** `analytic.mixin` (provides analytic account support)

#### Core Fields
| Field Name | Data Type | Description | Required |
|---|---|---|---|
| `id` | Integer | Primary key | System |
| `move_id` | Many2one(account.move) | Parent journal entry | Yes |
| `name` | Text | Description/label | Yes |
| `date` | Date | Effective date (from move_id) | Related |
| `account_id` | Many2one(account.account) | General ledger account | Yes |
| `partner_id` | Many2one(res.partner) | Customer/vendor | Optional |

#### Debit/Credit Fields
| Field Name | Data Type | Description |
|---|---|---|
| `debit` | Monetary | Debit amount |
| `credit` | Monetary | Credit amount |
| `balance` | Monetary | Computed: debit - credit |
| `amount_currency` | Monetary | Amount in foreign currency |
| `currency_id` | Many2one(res.currency) | Foreign currency |

#### Product & Tax Fields
| Field Name | Data Type | Description |
|---|---|---|
| `product_id` | Many2one(product.product) | Related product |
| `product_uom_id` | Many2one(uom.uom) | Unit of measure |
| `quantity` | Float | Quantity |
| `price_unit` | Monetary | Unit price |
| `price_subtotal` | Monetary | Subtotal before tax |
| `price_total` | Monetary | Total including tax |
| `tax_ids` | Many2many(account.tax) | Applied taxes |
| `tax_line_id` | Many2one(account.tax) | If this is a tax line |

#### Analytic Fields (Critical for Cell Tracking)
| Field Name | Data Type | Description | Key for Cells |
|---|---|---|---|
| `analytic_account_id` | Many2one(account.analytic.account) | Analytic account | **YES** |
| `analytic_tag_ids` | Many2many(account.analytic.tag) | Analytic tags | Optional |
| `analytic_line_ids` | One2many(account.analytic.line) | Related analytic entries | System |

**Note:** In Odoo 16+, analytic accounts use "Analytic Plans" with domain rules for mandatory/optional settings.

#### Reconciliation Fields
| Field Name | Data Type | Description |
|---|---|---|
| `reconciled` | Boolean | Fully reconciled |
| `full_reconcile_id` | Many2one(account.full.reconcile) | Reconciliation group |
| `matched_debit_ids` | One2many | Partial reconciliation (debit side) |
| `matched_credit_ids` | One2many | Partial reconciliation (credit side) |

#### System Fields
| Field Name | Data Type | Description |
|---|---|---|
| `create_date` | DateTime | Creation timestamp |
| `create_uid` | Many2one(res.users) | Creator |
| `write_date` | DateTime | Last modification |
| `write_uid` | Many2one(res.users) | Last modifier |
| `company_id` | Many2one(res.company) | Company |

---

### 4. account.analytic.account (Analytic Account)

**Model Name:** `account.analytic.account`
**Purpose:** Cost centers, projects, departments (for NERDX: Cells)

#### Core Fields
| Field Name | Data Type | Description | Cell Mapping |
|---|---|---|---|
| `id` | Integer | Primary key | **cell.odoo_analytic_account_id** |
| `name` | String | Analytic account name | Cell name |
| `code` | String | Account code | **cell.odoo_analytic_account_code** |
| `active` | Boolean | Active status | Yes |
| `company_id` | Many2one(res.company) | Company | Single or multi |
| `partner_id` | Many2one(res.partner) | Related partner | Optional |

---

### 5. account.analytic.line (Analytic Entry)

**Model Name:** `account.analytic.line`
**Purpose:** Detailed analytic tracking entries (auto-created from account.move.line)

#### Core Fields
| Field Name | Data Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | Description |
| `date` | Date | Entry date |
| `account_id` | Many2one(account.analytic.account) | Analytic account |
| `move_line_id` | Many2one(account.move.line) | Source journal item (renamed from move_id in v16+) |
| `general_account_id` | Many2one(account.account) | General ledger account |
| `amount` | Monetary | Amount (credit - debit) |
| `unit_amount` | Float | Quantity/hours |
| `product_id` | Many2one(product.product) | Related product |
| `company_id` | Many2one(res.company) | Company |

---

### 6. res.partner (Customer / Vendor)

**Model Name:** `res.partner`
**Purpose:** Customers, vendors, contacts, companies

#### Core Fields
| Field Name | Data Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | Partner name |
| `company_type` | Selection | 'person' or 'company' |
| `is_company` | Boolean | Whether it's a company |
| `parent_id` | Many2one(res.partner) | Parent company |
| `child_ids` | One2many(res.partner) | Contacts |

#### Accounting Fields
| Field Name | Data Type | Description |
|---|---|---|
| `property_account_receivable_id` | Many2one(account.account) | Receivable account |
| `property_account_payable_id` | Many2one(account.account) | Payable account |
| `property_payment_term_id` | Many2one(account.payment.term) | Payment terms |
| `property_supplier_payment_term_id` | Many2one(account.payment.term) | Supplier payment terms |

---

### 7. product.product (Product Variant)

**Model Name:** `product.product`
**Purpose:** Individual product variants (SKU level)

#### Core Fields
| Field Name | Data Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | Product variant name |
| `default_code` | String | Internal reference (SKU) |
| `product_tmpl_id` | Many2one(product.template) | Product template |
| `list_price` | Float | Sales price |
| `standard_price` | Float | Cost price |
| `categ_id` | Many2one(product.category) | Product category |
| `type` | Selection | 'product', 'consu', 'service' |
| `active` | Boolean | Active status |

---

### 8. Odoo Relationships & Data Flow for Cost Tracking

```
res.partner (Vendor)
         ↓
account.move (Vendor Bill)
         ↓
account.move.line (Invoice Line Items)
         ├──→ product_id (Product)
         ├──→ debit/credit (Amounts)
         ├──→ account_id (GL Account - COGS, OpEx, etc.)
         └──→ analytic_account_id (Cell Assignment) ← **CRITICAL**
                     ↓
         account.analytic.line (Auto-created analytic entry)
                     ↓
         account.analytic.account (Cell)
```

**Key Integration Points for Cost Tracking:**
1. **account.move** with `move_type='in_invoice'` = Vendor bill
2. **account.move.line.analytic_account_id** = Cell assignment
3. **account.move.line.debit** = Cost amount (vendor bills have debit entries)
4. **account.move.line.account_id** = GL account determines category (COGS vs OpEx)
5. **account.move.line.product_id** = Product details for cost analysis

---

## Integration Mapping

### Revenue Flow: Salesforce → NERDX System

| Source (Salesforce) | Destination (NERDX DB) | Mapping Logic |
|---|---|---|
| `Opportunity.Id` | `revenue_records.salesforce_opportunity_id` | Direct |
| `Opportunity.AccountId` | `revenue_records.salesforce_account_id` | Direct |
| `Opportunity.Name` | `revenue_records.opportunity_name` | **NEW FIELD** |
| `Opportunity.StageName` | `revenue_records.stage` | **NEW FIELD** |
| `Opportunity.Probability` | `revenue_records.probability` | **NEW FIELD** |
| `Opportunity.Type` | `revenue_records.opportunity_type` | **NEW FIELD** |
| `Opportunity.CloseDate` | `revenue_records.revenue_date` | Direct |
| `Opportunity.Amount` | `revenue_records.revenue_amount` | Direct |
| `OpportunityLineItem.Product2Id` (via PBE) | `revenue_records.product_name` | Custom field |
| `OpportunityLineItem.Quantity` | `revenue_records.quantity` | Custom field |
| `OpportunityLineItem.UnitPrice` | `revenue_records.unit_price` | Custom field |

**Filter Criteria:**
- `Opportunity.StageName = 'Closed Won'` for realized revenue
- `Opportunity.AccountId IN (cell.salesforce_account_ids)` for cell assignment
- `Opportunity.CloseDate = target_date` for daily revenue

---

### Cost Flow: Odoo → NERDX System

| Source (Odoo) | Destination (NERDX DB) | Mapping Logic |
|---|---|---|
| `account.move.id` | `cost_records.odoo_invoice_id` | Direct |
| `account.move.line.id` | `cost_records.odoo_invoice_line_id` | **NEW FIELD** |
| `account.move.line.analytic_account_id` | `cell_id` (via cell.odoo_analytic_account_id) | **CRITICAL** |
| `account.move.line.product_id` | `cost_records.odoo_product_id` | **NEW FIELD** |
| `account.move.line.partner_id` | `cost_records.odoo_partner_id` | **NEW FIELD** |
| `account.move.line.date` | `cost_records.cost_date` | Direct |
| `account.move.line.debit` | `cost_records.cost_amount` | Vendor bill uses debit |
| `account.move.line.account_id` GL account code | `cost_records.category` | Logic: 5xxxx = COGS, 6xxxx = OpEx |
| `account.move.line.product_id.name` | `cost_records.product_name` | **NEW FIELD** |
| `account.move.line.partner_id.name` | `cost_records.vendor_name` | Direct |
| `account.move.name` | `cost_records.invoice_number` | Invoice number |
| `account.move.line.name` | `cost_records.description` | Line description |

**Filter Criteria:**
- `account.move.move_type = 'in_invoice'` for vendor bills
- `account.move.state = 'posted'` for confirmed bills
- `account.move.line.analytic_account_id = cell.odoo_analytic_account_id` for cell assignment
- `account.move.line.date = target_date` for daily costs
- `account.move.line.debit > 0` (skip credit entries and tax lines)

---

## Best Practices

### 1. Standard vs Custom Fields Strategy

**Current Issue:**
- Original SQLAlchemy models depended heavily on custom Salesforce fields (Product__c, Quantity__c, UnitPrice__c)
- This prevents integration with standard Salesforce instances

**Solution Implemented:**
- **Priority 1:** Standard fields (opportunity_name, stage, probability, opportunity_type)
- **Priority 2:** Custom fields marked as optional (product_name, product_category, quantity, unit_price)
- **Fallback:** If custom fields don't exist, use OpportunityLineItem for product details

### 2. Salesforce SOQL Query Strategy

**Option A: Standard Fields Only (Recommended)**
```sql
SELECT Id, Name, AccountId, Amount, CloseDate, StageName,
       Probability, Type, OwnerId, ForecastCategoryName
FROM Opportunity
WHERE AccountId IN :accountIds
  AND CloseDate = :targetDate
  AND StageName = 'Closed Won'
```

**Option B: With Custom Fields (If Available)**
```sql
SELECT Id, Name, AccountId, Amount, CloseDate, StageName,
       Probability, Type, Product__c, Quantity__c, UnitPrice__c
FROM Opportunity
WHERE AccountId IN :accountIds
  AND CloseDate = :targetDate
  AND StageName = 'Closed Won'
```

**Option C: Use OpportunityLineItem (Most Flexible)**
```sql
-- First query: Get opportunities
SELECT Id, Name, AccountId, Amount, CloseDate, StageName, Probability, Type
FROM Opportunity
WHERE AccountId IN :accountIds
  AND CloseDate = :targetDate
  AND StageName = 'Closed Won'

-- Second query: Get product details
SELECT Id, OpportunityId, PricebookEntry.Product2.Name,
       ProductCode, Quantity, UnitPrice, TotalPrice
FROM OpportunityLineItem
WHERE OpportunityId IN :opportunityIds
```

### 3. Odoo XML-RPC Query Strategy

**Recommended Query for Cost Records:**
```python
# Search vendor bills for a specific date and analytic account
invoice_line_ids = models.execute_kw(
    db, uid, password,
    'account.move.line', 'search_read',
    [[
        ('move_id.move_type', '=', 'in_invoice'),
        ('move_id.state', '=', 'posted'),
        ('analytic_account_id', '=', analytic_account_id),
        ('date', '=', target_date_str),
        ('debit', '>', 0)  # Exclude tax lines and credits
    ]],
    {
        'fields': [
            'id', 'move_id', 'name', 'date', 'debit',
            'account_id', 'analytic_account_id',
            'product_id', 'partner_id', 'quantity',
            'price_unit', 'price_subtotal'
        ]
    }
)
```

### 4. Category Determination Logic

**Odoo Account Code → Cost Category Mapping:**
```python
def determine_cost_category(account_code):
    """Map Odoo GL account to cost category"""
    if account_code.startswith('5'):
        return 'COGS'  # Cost of Goods Sold
    elif account_code.startswith('6'):
        # Subdivide operating expenses
        if account_code.startswith('60'):
            return 'Rent'
        elif account_code.startswith('61'):
            return 'Salaries'
        elif account_code.startswith('62'):
            return 'Marketing'
        elif account_code.startswith('63'):
            return 'Travel'
        else:
            return 'OpEx'  # General operating expense
    elif account_code.startswith('2'):
        return 'CapEx'  # Capital expenditure (assets)
    else:
        return 'Other'
```

### 5. Error Handling & Fallbacks

**Salesforce Integration:**
- If custom fields don't exist → Query OpportunityLineItem
- If OpportunityLineItem has no data → Use Opportunity.Amount only
- Store both opportunity-level and line-item-level data when available

**Odoo Integration:**
- If analytic_account_id is missing → Log warning, skip record
- If product_id is null → Use line description as product_name
- If partner_id is null → Use 'Unknown Vendor'

### 6. Data Consistency Checks

**Daily Synchronization Validation:**
```python
# After sync, validate:
1. Sum of revenue_records.revenue_amount == Salesforce Opportunity.Amount
2. Each cost_record has valid analytic_account_id (cell assignment)
3. No duplicate salesforce_opportunity_id for same revenue_date
4. No duplicate odoo_invoice_line_id for same cost_date
```

---

## Summary: Key Improvements

### Database Schema Updates Completed

✅ **RevenueRecordDB** (database.py:58-87):
- Added: `opportunity_name`, `stage`, `probability`, `opportunity_type` (standard fields)
- Made custom fields optional: `product_name`, `product_category`, `quantity`, `unit_price`

✅ **CostRecordDB** (database.py:90-119):
- Added: `odoo_invoice_line_id`, `odoo_product_id`, `odoo_partner_id` (standard fields)
- Added: `product_name` for display
- Added: `source` to track data origin (odoo, manual, etc.)
- Renamed: `metadata` → `extra_data` (avoided SQLAlchemy reserved word)

✅ **financial_service.py** (services/financial_tracker/financial_service.py:58-154):
- Updated revenue sync to populate new standard fields
- Updated cost sync to populate new Odoo standard fields
- Improved data mapping for better integration

### Next Steps Required

1. **Update PostgreSQL Schema on Railway** ← PENDING
2. **Test with Real Salesforce/Odoo Data** ← PENDING
3. **Generate & Send Daily Reports** ← PENDING

---

**Document Version:** 1.0
**Author:** Claude Code
**Integration Target:** NERDX Independent Accounting System v1.0
