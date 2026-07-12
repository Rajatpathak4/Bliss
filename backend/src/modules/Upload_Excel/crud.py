from io import BytesIO
import sys

from fastapi import Depends, status, FastAPI
from datetime import timedelta, datetime
from sqlalchemy import func, or_, and_
from config import get_setting
from helper import customhelper
import pandas as pd
import openpyxl
from helper.sessionData import getSessionUserId
from modules.Upload_Excel.models import UserExcel
from fastapi import FastAPI
import re
import zipfile


configObj = get_setting()

FIELD_KEYWORDS = [
    ('policy holder', 'policy_holder'),
    ('policy number', 'policy_number'),
    ('policy', 'policy_number'),       
    ('family', 'family_code'),
    ('dob', 'dob'),
    ('mobile', 'phone_number'),
    ('phone', 'phone_number'),
    ('email', 'email'),
    ('address', 'address'),
    ('agency', 'agency_code'),
    ('commecement', 'commecement_date'),  # matches table's existing typo'd column
    ('commencement', 'commecement_date'), # also catch correctly-spelled headers
    ('plan', 'plan'),
    ('term', 'term'),
    ('ppt', 'ppt'),
    ('sum assured', 'sum_assured'),
    ('sum', 'sum_assured'),
    ('assured', 'sum_assured'),
    ('mode', 'mode'),
    ('fup', 'fup_date'),
    ('premium', 'premium'),
    ('nominee', 'nominee'),
]

DATE_FIELDS = ['dob', 'commecement_date', 'fup_date']
REQUIRED_SIGNAL_FIELDS = ['policy_number', 'dob', 'sum_assured', 'premium']
HEADER_MARKER = 'family code'   # word guaranteed only in the real header row


# ---------- small, testable helpers ----------

def fix_missing_sharedstrings(file_bytes: bytes) -> bytes:
    """Some xlsx writers omit sharedStrings.xml when the sheet has no shared
    strings. openpyxl treats that as corrupt — inject an empty one and retry."""
    with zipfile.ZipFile(BytesIO(file_bytes), "r") as zin:
        if "xl/sharedStrings.xml" in zin.namelist():
            return file_bytes

        out = BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, zin.read(item.filename))
            zout.writestr(
                "xl/sharedStrings.xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'count="0" uniqueCount="0"></sst>',
            )
        return out.getvalue()

def find_header_row(data_bytes: bytes, marker: str = HEADER_MARKER, max_scan: int = 10) -> int:
    """Report exports often have 2-4 title rows above the real header.
    Scan the top of the sheet and return the index of the row that actually
    contains the marker column, instead of blindly trusting row 0."""
    preview = pd.read_excel(BytesIO(data_bytes), header=None, nrows=max_scan, engine="openpyxl")
    for idx, row in preview.iterrows():
        cells = [str(v).strip().lower() for v in row.tolist() if pd.notna(v)]
        if any(marker in c for c in cells):
            return idx
    return 0  # marker not found — fall back to old behaviour rather than crash

def extract_report_metadata(data_bytes: bytes, header_row: int):
    """Pulls agent code and the report's date range out of the title block
    (the rows above the header), e.g.:
      'Agent (1216812G) Policies'
      'Date Range: From 01/07/2026 To 31/07/2026'
    These apply to every row in the sheet, not per-row."""
    if header_row == 0:
        return None, None, None

    preview = pd.read_excel(BytesIO(data_bytes), header=None, nrows=header_row, engine="openpyxl")
    agent_code, from_date, to_date = None, None, None

    for _, row in preview.iterrows():
        for val in row.tolist():
            if pd.isna(val):
                continue
            text = str(val)

            if agent_code is None:
                m = re.search(r'agent\s*\(([^)]+)\)', text, re.IGNORECASE)
                if m:
                    agent_code = m.group(1).strip()

            if from_date is None:
                m = re.search(
                    r'from\s+(\d{1,2}/\d{1,2}/\d{4})\s+to\s+(\d{1,2}/\d{1,2}/\d{4})',
                    text, re.IGNORECASE,
                )
                if m:
                    from_date = pd.to_datetime(m.group(1), dayfirst=True).date()
                    to_date = pd.to_datetime(m.group(2), dayfirst=True).date()

    return agent_code, from_date, to_date

def build_column_map(columns) -> dict:
    """Resolve field -> actual Excel column name ONCE, before the row loop
    (old code called find_col_for per field per row — wasteful, and prone
    to matching the wrong column). Each column is claimed by at most one
    field, and once a field is resolved, lower-priority keywords for the
    same field are skipped."""
    norm = {c: str(c).strip().lower() for c in columns}
    claimed = set()
    mapping = {}

    for keyword, field in FIELD_KEYWORDS:
        if field in mapping:
            continue
        for orig, n in norm.items():
            if orig in claimed:
                continue
            if keyword in n:
                mapping[field] = orig
                claimed.add(orig)
                break

    return mapping

def is_real_data_row(data: dict) -> bool:
    """Title/footer lines ('Total Policies:', etc.) slip in as rows with
    only agent_code filled and everything else empty — filter those out."""
    return any(data.get(f) not in (None, '') for f in REQUIRED_SIGNAL_FIELDS)

# ---------- main entrypoint ----------

def upload_excel(file, db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)
        raw_bytes = file.file.read()

        try:
            zipfile.ZipFile(BytesIO(raw_bytes))
        except zipfile.BadZipFile:
            return customhelper.printCustmMsg(
                400, 'FALSE',
                "Uploaded file isn't a valid .xlsx — check if it's an old .xls "
                "or HTML export saved with the wrong extension."
            )

        data_bytes = fix_missing_sharedstrings(raw_bytes)

        header_row = find_header_row(data_bytes)
        df = pd.read_excel(BytesIO(data_bytes), header=header_row, engine="openpyxl")
        df = df.where(pd.notnull(df), None)

        agent_code, from_date, to_date = extract_report_metadata(data_bytes, header_row)
        column_map = build_column_map(df.columns)   # resolved once, not per row

        created = 0
        errors = []

        for index, row in df.iterrows():
            try:
                data = {}
                for field, col in column_map.items():
                    val = row[col]
                    data[field] = None if (val is None or (isinstance(val, float) and pd.isna(val))) else val

                if not is_real_data_row(data):
                    continue

                data['term'] = customhelper.safe_int(data.get('term'))
                data['ppt'] = customhelper.safe_int(data.get('ppt'))
                data['plan'] = customhelper.safe_int(data.get('plan'))
                data['sum_assured'] = customhelper.safe_float(data.get('sum_assured'))
                data['premium'] = customhelper.safe_float(data.get('premium'))

                for f in ['policy_number', 'phone_number', 'family_code', 'agency_code', 'mode']:
                    v = data.get(f)
                    if isinstance(v, float) and pd.notna(v):
                        data[f] = str(int(v))
                    elif v is not None:
                        data[f] = str(v)

                for dfield in DATE_FIELDS:
                    data[dfield] = customhelper.parse_date(data.get(dfield))

                data['agent_code'] = agent_code
                data['from_date'] = from_date
                data['to_date'] = to_date
                data['created_at'] = datetime.now()
                data['created_by'] = None
                data['is_deleted'] = False
                data['user_id'] = user_id

                with db.begin_nested():
                    db.add(UserExcel(**data))
                created += 1

            except Exception as e:
                errors.append({'row': int(index) + 1, 'error': str(e)})

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            return customhelper.print_error_with_linenumebr(e)

        resp = {'created': created, 'errors': errors}
        return customhelper.printCustmMsg(200, 'TRUE', "File uploaded and processed", resp)

    except Exception as err:
        line = sys.exc_info()[-1].tb_lineno
        customhelper.print_error_with_linenumebr(err)
        return customhelper.printCustmMsg(
            500, 'FALSE', f'Something went wrong in Excel--> {err} on line {line}'
        )
    
def get_active_client(db, serviceRequest):
    try:
        ddate = datetime.now().date()
        user_id = getSessionUserId(serviceRequest)

        total = db.query(UserExcel).filter(UserExcel.is_deleted == False, UserExcel.user_id == user_id).count()
        if not total:
            return 0, 0

        active = db.query(UserExcel).filter(UserExcel.to_date >= ddate,UserExcel.is_deleted == False,UserExcel.from_date <= ddate,UserExcel.user_id == user_id).count()

        active_percent = round((active / total) * 100, 2)
        return [ active, active_percent]
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
    
def get_premium_stats(db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)

        today = datetime.now().date()
        due_cutoff = today + timedelta(days=45)

        premium_due = db.query(UserExcel).filter(UserExcel.user_id == user_id,UserExcel.is_deleted == False,UserExcel.fup_date >= today,UserExcel.fup_date <= due_cutoff).count()

        return {"premium_due": premium_due, "premium_done": 0}

    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
    
def get_user_table_data(page_no, limit, db, serviceRequest, search=None):
    try:
        user_id = getSessionUserId(serviceRequest)

        query = (
            db.query(
                UserExcel.id,
                UserExcel.policy_holder,
                UserExcel.email,
                UserExcel.phone_number,
                UserExcel.policy_number,
                UserExcel.mode,
                UserExcel.address
            )
            .filter(
                UserExcel.is_deleted == False,
                UserExcel.user_id == user_id
            )
        )

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    UserExcel.policy_holder.ilike(search_term),
                    UserExcel.email.ilike(search_term),
                    UserExcel.phone_number.ilike(search_term),
                    UserExcel.policy_number.ilike(search_term),
                    UserExcel.mode.ilike(search_term),
                )
            )

        query = query.order_by(UserExcel.id.desc())

        result = customhelper.pagination(
            query=query,
            page_no=page_no,
            limit=limit
        )

        data = []

        for user in result["db_data"]:
            data.append({
                "id": user.id,
                "policy_holder": user.policy_holder,
                "email": user.email,
                "phone_number": user.phone_number,
                "policy_number": user.policy_number,
                "mode": user.mode,
                "address": user.address
            })

        return customhelper.printCustmMsg(
            200,
            "TRUE",
            "User data fetched successfully",
            {
                "table_data": data,
                "pagination": result["pagination"]
            }
        )

    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
    
def user_modal_data(userID, db, serviceRequest):
    try:
        logged_in_user = getSessionUserId(serviceRequest)

        modal_data = (
            db.query(
                UserExcel.id,
                UserExcel.family_code,
                UserExcel.email,
                UserExcel.phone_number,
                UserExcel.policy_number,
                UserExcel.mode,
                UserExcel.address,
                UserExcel.plan,
                UserExcel.sum_assured,
                UserExcel.fup_date,
                UserExcel.premium,
                UserExcel.dob,
                UserExcel.agency_code,
                UserExcel.commecement_date,
                UserExcel.term,
                UserExcel.ppt,
                UserExcel.nominee,
                UserExcel.policy_holder
            )
            .filter(
                UserExcel.is_deleted == False,
                UserExcel.id == userID,
                UserExcel.user_id == logged_in_user
            )
            .first()
        )

        if not modal_data:
            return False

        final_data = {
            "id":modal_data.id,
            "policy_holder": modal_data.policy_holder,
            "email": modal_data.email,
            "phone_number": modal_data.phone_number,
            "address": modal_data.address,
            "mode": modal_data.mode,
            "dob": modal_data.dob,
            "family_code": modal_data.family_code,
            "policy_number": modal_data.policy_number,
            "agency_code": modal_data.agency_code,
            "commecement_date": modal_data.commecement_date,
            "plan": modal_data.plan,
            "term": modal_data.term,
            "ppt": modal_data.ppt,
            "sum_assured": modal_data.sum_assured,
            "fup_date": modal_data.fup_date,
            "premium": modal_data.premium,
            "nominee": modal_data.nominee,
        }

        return final_data
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
       
def add_user_data(userData, db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)
        existing = db.query(UserExcel).filter(
            UserExcel.phone_number == userData.phone_number,
            UserExcel.policy_holder == userData.policy_holder,
            UserExcel.email == userData.email,
            UserExcel.is_deleted == False,
            UserExcel.user_id == user_id
        ).first()

        if existing:
            return customhelper.printCustmMsg(200, 'FALSE',f'Record already exists for user {userData.policy_holder}')

        new_user =UserExcel(
            agent_code=userData.agent_code,
            from_date=userData.from_date,
            to_date=userData.to_date,
            family_code=userData.family_code,
            policy_holder=userData.policy_holder,
            policy_number=userData.policy_number,
            dob=userData.dob,
            phone_number=userData.phone_number,
            email=userData.email,
            address=userData.address,
            agency_code=userData.agency_code,
            commecement_date=userData.commecement_date,
            plan=userData.plan,
            term=userData.term,
            ppt=userData.ppt,
            sum_assured=userData.sum_assured,
            mode=userData.mode,
            fup_date=userData.fup_date,
            premium=userData.premium,
            nominee=userData.nominee,
            created_at=datetime.now(),
            created_by=user_id,
            is_deleted=False,
            user_id=user_id,

        )
        db.add(new_user)
        db.commit()

        return customhelper.printCustmMsg(200, 'TRUE', f'Record added successfully for user {userData.policy_holder}')
    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)
    
def delete_user(policy_number, db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)
        user = db.query(UserExcel).filter(
            UserExcel.policy_number == policy_number,
            UserExcel.is_deleted == False,
        ).first()

        if not user:
            return customhelper.printCustmMsg(200, 'FALSE', f'No record found for policy number {policy_number}')

        user.is_deleted = True
        db.commit()

        return customhelper.printCustmMsg(200, 'TRUE', f'Record deleted successfully for policy number {policy_number}')
    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)
    
def update_user_data(userData, db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)

        user = (
            db.query(UserExcel)
            .filter(
                UserExcel.id == userData.id,
                UserExcel.is_deleted == False
            )
            .first()
        )

        if not user:
            return customhelper.printCustmMsg(
                200,
                'FALSE',
                f'No record found for {userData.policy_holder}'
            )

        if userData.agent_code is not None:
            user.agent_code = userData.agent_code

        if userData.from_date is not None:
            user.from_date = userData.from_date

        if userData.to_date is not None:
            user.to_date = userData.to_date

        if userData.family_code is not None:
            user.family_code = userData.family_code

        if userData.policy_holder is not None:
            user.policy_holder = userData.policy_holder

        if userData.policy_number is not None:
            user.policy_number = userData.policy_number

        if userData.dob is not None:
            user.dob = userData.dob

        if userData.phone_number is not None:
            user.phone_number = userData.phone_number

        if userData.email is not None:
            user.email = userData.email

        if userData.address is not None:
            user.address = userData.address

        if userData.agency_code is not None:
            user.agency_code = userData.agency_code

        if userData.commecement_date is not None:
            user.commecement_date = userData.commecement_date

        if userData.plan is not None:
            user.plan = userData.plan

        if userData.term is not None:
            user.term = userData.term

        if userData.ppt is not None:
            user.ppt = userData.ppt

        if userData.sum_assured is not None:
            user.sum_assured = userData.sum_assured

        if userData.mode is not None:
            user.mode = userData.mode

        if userData.fup_date is not None:
            user.fup_date = userData.fup_date

        if userData.premium is not None:
            user.premium = userData.premium

        if userData.nominee is not None:
            user.nominee = userData.nominee

        db.commit()
        db.refresh(user)

        return customhelper.printCustmMsg(
            200,
            'TRUE',
            f'Record updated successfully for {user.policy_holder}'
        )

    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)
      
def get_premium_stats(db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)

        today = datetime.now().date()
        due_cutoff = today + timedelta(days=45)     # next 45 days
        done_cutoff = today - timedelta(days=45)    # last 45 days

        premium_due = db.query(UserExcel).filter(
            UserExcel.user_id == user_id,
            UserExcel.is_deleted == False,
            UserExcel.fup_date >= today,
            UserExcel.fup_date <= due_cutoff
        ).count()

        premium_done = db.query(UserExcel).filter(
            UserExcel.user_id == user_id,
            UserExcel.is_deleted == False,
            UserExcel.fup_date >= done_cutoff,
            UserExcel.fup_date < today
        ).count()

        return {"premium_due": premium_due, "premium_done": premium_done, "revenue": 0}

    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
    
def _last_n_months(n=6):
    """List of first-of-month datetimes for last n months, oldest first."""
    seq = []
    d = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for _ in range(n):
        seq.append(d)
        d = (d - timedelta(days=1)).replace(day=1)   # jump to prev month
    seq.reverse()
    return seq

def get_dashboard_chart_data(db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)

        months = _last_n_months(6)
        labels = [m.strftime('%b') for m in months]
        keys = [m.strftime('%Y-%m') for m in months]
        start = months[0].date()
        today = datetime.now().date()

        commence_expr = func.to_char(UserExcel.commecement_date, 'YYYY-MM')
        fup_expr = func.to_char(UserExcel.fup_date, 'YYYY-MM')

        # ---- New clients: count by commencement month ----
        commence_rows = (
            db.query(commence_expr.label('m'), func.count(UserExcel.id).label('cnt'))
            .filter(
                UserExcel.is_deleted == False,
                UserExcel.user_id == user_id,
                UserExcel.commecement_date >= start,
            )
            .group_by(commence_expr)
            .all()
        )
        commence_map = {r.m: r.cnt for r in commence_rows}
        new_clients = [commence_map.get(k, 0) for k in keys]

        # ---- Revenue: SUM(premium) by commencement month ----
        rev_rows = (
            db.query(commence_expr.label('m'),
                     func.coalesce(func.sum(UserExcel.premium), 0).label('amt'))
            .filter(
                UserExcel.is_deleted == False,
                UserExcel.user_id == user_id,
                UserExcel.commecement_date >= start,
            )
            .group_by(commence_expr)
            .all()
        )
        rev_map = {r.m: float(r.amt) for r in rev_rows}
        revenue = [round(rev_map.get(k, 0)) for k in keys]
        revenue_total = sum(revenue)

        # ---- Premium due tracker (chart): count fup_date by month ----
        due_rows = (
            db.query(fup_expr.label('m'), func.count(UserExcel.id).label('cnt'))
            .filter(
                UserExcel.is_deleted == False,
                UserExcel.user_id == user_id,
                UserExcel.fup_date >= start,
            )
            .group_by(fup_expr)
            .all()
        )
        due_map = {r.m: r.cnt for r in due_rows}
        premium_due_tracker = [due_map.get(k, 0) for k in keys]

        # ---- Active users (chart): policies active at each month-end ----
        active_users = []
        for m in months:
            month_end = (m + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            cnt = (
                db.query(UserExcel)
                .filter(
                    UserExcel.is_deleted == False,
                    UserExcel.user_id == user_id,
                    UserExcel.from_date <= month_end,
                    UserExcel.to_date >= month_end,
                )
                .count()
            )
            active_users.append(cnt)

        # ---- CARD numbers ----
        # active client + percent (same logic as get_active_client)
        total = db.query(UserExcel).filter(
            UserExcel.is_deleted == False,
            UserExcel.user_id == user_id,
        ).count()
        active_now = db.query(UserExcel).filter(
            UserExcel.is_deleted == False,
            UserExcel.user_id == user_id,
            UserExcel.from_date <= today,
            UserExcel.to_date >= today,
        ).count()
        active_percent = round((active_now / total) * 100, 2) if total else 0

        # premium due (next 45 days) + done (last 45 days)
        due_cutoff = today + timedelta(days=45)
        done_cutoff = today - timedelta(days=45)
        premium_due = db.query(UserExcel).filter(
            UserExcel.is_deleted == False,
            UserExcel.user_id == user_id,
            UserExcel.fup_date >= today,
            UserExcel.fup_date <= due_cutoff,
        ).count()
        premium_done = db.query(UserExcel).filter(
            UserExcel.is_deleted == False,
            UserExcel.user_id == user_id,
            UserExcel.fup_date >= done_cutoff,
            UserExcel.fup_date < today,
        ).count()

        stats = [
            {"label": "Active Users",      "value": f"{active_now} clients",     "icon": "users",  "accent": "indigo", "trend": "up",   "hint": f"{active_percent}% active"},
            {"label": "Premium Due (45D)", "value": f"{premium_due} renewals",   "icon": "clock",  "accent": "amber",  "trend": "flat", "hint": "Needs attention"},
            {"label": "Premium Done",      "value": f"{premium_done} completed", "icon": "card",   "accent": "green",  "trend": "up",   "hint": "Last 45 days"},
            {"label": "Revenue",           "value": f"${revenue_total:,}",       "icon": "dollar", "accent": "purple", "trend": "up",   "hint": "Last 6 months"},
        ]

        return {
            "months": labels,
            "revenue": revenue,
            "active_users": active_users,
            "premium_due_tracker": premium_due_tracker,
            "new_clients": new_clients,
            "stats": stats,
        }

    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)