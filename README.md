# NexaERP

A professional Django mini ERP system for managing products, customers, sales orders, and stock movements — built with a clean service layer architecture, class-based views, and Bootstrap 5 templates.

## Live Demo

🚀 Try NexaERP online:

🌐 [NexaERP Live Demo](https://mmy.pythonanywhere.com/)

### Demo Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Sales | `sales` | `sales123` |

> ⚠️ Demo data resets periodically.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Default Credentials](#default-credentials)
- [Modules](#modules)
- [Architecture](#architecture)
- [Screenshots](#screenshots)

---

## Overview

NexaERP is a fully functional ERP system designed for small to medium businesses in retail, wholesale, and distribution. It provides a clean, validated workflow for managing your product catalog, customer records, sales orders, and inventory — all from a single, fast interface.

Every write operation is wrapped in `@transaction.atomic`, business logic lives in dedicated service classes (never in views), and every stock change is automatically logged with a full audit trail.

---

## Features

- **Role-Based Access Control** — Admin and Sales roles with fine-grained permissions. Admins manage products and users; sales staff handle orders and customers.
- **Product Catalog** — Full CRUD with image upload, SKU management, category filtering, cost/selling price tracking, and automatic profit margin calculation.
- **Customer Management** — Auto-generated customer codes, contact details, opening balance tracking, and per-customer order history.
- **Sales Order Lifecycle** — Pending → Confirmed → Cancelled workflow with dynamic formsets, live total calculation, and stock validation at confirmation.
- **Automatic Stock Tracking** — Every confirmed order deducts stock; cancellations restore it. Every movement is logged with user, reference, and timestamp.
- **Real-Time Dashboard** — Live stats including today's sales, pending orders, low-stock alerts, recent activity, and quick actions.
- **Excel Export** — Export products, customers, orders, and stock movements to formatted `.xlsx` files with one click.
- **Duplicate Image Detection** — SHA-256 hashing prevents storing duplicate product images.
- **Soft Deletes** — Customers and products are deactivated, never hard-deleted, preserving historical data integrity.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 6 |
| Database | SQLite (development) |
| Frontend | Bootstrap 5, Bootstrap Icons |
| Templates | Django Template Language |
| Excel Export | openpyxl |
| Image Handling | Pillow |
| Architecture | Service Layer Pattern, Class-Based Views |

---

## Project Structure

```
nexaerp/
├── accounts/               # Authentication, dashboard, login/logout views
│   ├── services/
│   │   └── dashboard_service.py
│   ├── views/
│   │   ├── auth_views.py
│   │   └── dashboard_views.py
│   └── templates/
├── core/                   # Shared mixins, export utilities, management commands
│   ├── exports.py          # Excel workbook builder
│   ├── mixins.py           # AdminRequiredMixin, SalesOrAdminMixin
│   └── management/commands/seed_data.py
├── products/               # Product catalog module
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── templates/
├── customers/              # Customer management module
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── templates/
├── orders/                 # Sales order module
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── templates/
├── movements/              # Stock movement log module
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── templates/
├── home/                   # Public landing page
├── templates/              # Global base templates
├── static/                 # CSS, JS, favicon
├── media/                  # Uploaded product images
├── erp/                    # Project settings, URL config
└── manage.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourname/nexaerp.git
cd nexaerp

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Seed demo data (creates users, products, and customers)
python manage.py seed_data

# 6. Run the development server
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Default Credentials

After running `seed_data`, the following accounts are available:

| Role | Username | Password | Access |
|---|---|---|---|
| Admin | `admin` | `admin123` | Full access — products, customers, orders, admin panel |
| Sales | `sales` | `sales123` | Customers, orders, stock movements (read-only on products) |

> ⚠️ Change these credentials before deploying to production.

---

## Modules

### Dashboard
Live overview of the business: today's confirmed sales, pending order count, low-stock alerts, and a quick-action panel. Powered by `DashboardService`.

### Products
Full CRUD for the product catalog. Admins can create, edit, and delete products. All users can browse and search. Features include:
- SKU and category management
- Cost price, selling price, and profit margin tracking
- Product image upload with SHA-256 deduplication
- Low-stock indicator (≤ 10 units)
- Per-product stock movement history

### Customers
Manage your customer base with auto-generated codes, contact info, and opening balance. Each customer profile shows total orders, total spent, and current balance (opening balance minus confirmed order totals).

### Sales Orders
Create orders with a dynamic multi-item formset. Live total calculation updates as you type. The order lifecycle:

```
Pending → Confirmed → (Stock deducted, movement logged)
       ↘ Cancelled → (Stock restored if was Confirmed)
```

Stock availability and customer balance are both validated before confirmation.

### Stock Movements
A complete, immutable audit log of every inventory change. Each entry records the product, quantity delta, movement type (`sale`, `return`, `adjustment`, `purchase`), order reference, user, and timestamp. Exportable to Excel.

---

## Architecture

NexaERP follows the **Service Layer Pattern** — all business logic lives in `services.py` files, keeping views thin and logic testable.

```
View  →  Service  →  Model
          ↓
      Validation
      DB Writes (atomic)
      Side Effects (stock log, etc.)
```

Key design decisions:

- **`@transaction.atomic`** on every mutating service method — partial writes never persist.
- **Soft deletes** on `Customer` and `Product` — `is_active = False` instead of `DELETE`.
- **`AdminRequiredMixin` / `SalesOrAdminMixin`** — permission checks at the view layer, separate from business logic.
- **`StockMovementService.log()`** — called automatically by `OrderService` on confirm/cancel; never called from views directly.
- **Image deduplication** — `ProductService` hashes each uploaded image and reuses the file path if an identical image already exists.

---

## Excel Exports

All major modules support one-click Excel export:

| URL | File |
|---|---|
| `/products/export/` | `products_YYYYMMDD_HHMMSS.xlsx` |
| `/customers/export/` | `customers_YYYYMMDD_HHMMSS.xlsx` |
| `/orders/export/` | `orders_YYYYMMDD_HHMMSS.xlsx` (2 sheets: Orders + Items) |
| `/movements/export/` | `stock_movements_YYYYMMDD_HHMMSS.xlsx` |

Exports are styled with a dark header row, alternating row fills, column auto-widths, frozen header row, and auto-filters — powered by `core/exports.py`.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

> The `SECRET_KEY` in `settings.py` is for development only. Always override it in production via environment variables.

---

## Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set a strong `SECRET_KEY` via environment variable
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Switch to PostgreSQL or another production database
- [ ] Set up static file serving (`collectstatic` + whitenoise or nginx)
- [ ] Configure media file storage (S3 or similar)
- [ ] Change default admin/sales passwords

---

## License

MIT License — free to use, modify, and distribute.

---

> Built with Django & ♥
