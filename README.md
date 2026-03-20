# SIIRH / SIHMADA Recovery Workspace

This repository contains the current SIIRH application under recovery and controlled expansion.

## Current Status

- existing payroll module preserved
- backend: FastAPI monolith in `siirh-backend`
- frontend: React/Vite app in `siirh-frontend`
- recovery documentation added for audit, protection, migration, RBAC, and tests

## Read First

- `EXISTING_SYSTEM_AUDIT.md`
- `PAYROLL_PROTECTION_MAP.md`
- `DATA_MODEL_GAP_ANALYSIS.md`
- `RECOVERY_PLAN.md`
- `MIGRATION_PLAN.md`
- `RBAC_GAP_REPORT.md`

## Key Principle

Do not break payroll. New RH, inspection, alert, and compliance capabilities must be integrated around the existing payroll backend through controlled migrations and adapters.

## Local Run

### Backend

1. create a `.env` from `.env.example`
2. install backend requirements
3. run `python start_server.py` from `siirh-backend`

### Frontend

1. create a `.env` from `.env.example`
2. run `npm install`
3. run `npm run dev` in `siirh-frontend`
