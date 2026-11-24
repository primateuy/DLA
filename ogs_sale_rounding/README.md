# Sale Order Rounding

## Overview
This module brings **Cash Rounding** support to Sale Orders in Odoo 17,
mirroring the behaviour already present on Customer Invoices (`account.move`).

## What it does
| Feature | Details |
|---|---|
| Cash Rounding field | Added to the **Other Info** tab of the Sale Order |
| Rounding row | Shown in the **totals block** (hidden when no rounding is selected) |
| Rounded Total row | Displayed below the rounding row |
| Invoice carry-over | Selected rounding method is **automatically copied** to the generated invoice |

## Installation
1. Copy the `sale_order_rounding` folder into your Odoo `addons` path.
2. Restart the Odoo service.
3. Go to **Apps**, search for **Sale Order Rounding**, and click **Install**.

## Usage
1. Open a **Sale Order**.
2. Go to the **Other Info** tab.
3. Select a **Cash Rounding** method (configured under Accounting → Configuration → Cash Roundings).
4. The **Rounding** and **Total (Rounded)** rows will appear in the totals section.
5. When you create an invoice from the sale order, the rounding method carries over automatically.

## Dependencies
- `sale_management`
- `account`

## Odoo Version
Tested on **Odoo 17.0**
