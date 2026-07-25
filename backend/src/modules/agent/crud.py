from sqlalchemy import func

from helper import customhelper
from modules.Upload_Excel.models import UserExcel
from modules.agent.models import PolicyCommission


def get_family_policies(db, policy_holder: str):
    try:
        search_name = policy_holder.strip()

        policies = (
            db.query(UserExcel)
            .filter(
                func.lower(func.trim(UserExcel.policy_holder)) == search_name.lower(),
                UserExcel.is_deleted == False,  # noqa: E712
            )
            .order_by(UserExcel.policy_number)
            .all()
        )

        if not policies:
            return customhelper.printCustmMsg(200, 'FALSE', "No family policies found")

        total_sum_assured = sum(p.sum_assured or 0 for p in policies)
        total_premium = sum(p.premium or 0 for p in policies)

        result = {
            "policy_holder": policy_holder,
            "member_count": len(policies),
            "total_sum_assured": total_sum_assured,
            "total_premium": total_premium,
            "members": [
                {
                    "id": p.id,
                    "policy_holder": p.policy_holder,
                    "policy_number": p.policy_number,
                    "plan": p.plan,
                    "sum_assured": p.sum_assured,
                    "premium": p.premium,
                    "fup_date": p.fup_date,
                    "relation_hint": p.nominee,
                }
                for p in policies
            ],
        }
        return customhelper.printCustmMsg(200, 'TRUE', "Family policies fetched", result)
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)


def get_commission_summary(db, user_id, agent_code):
    query = db.query(UserExcel).filter(
        UserExcel.is_deleted == False,  # noqa: E712
        UserExcel.user_id == user_id,
    )
    if agent_code:
        query = query.filter(UserExcel.agent_code == agent_code)

    policies = query.all()
    policy_ids = [p.id for p in policies]

    # ek hi query se saari commission rows le lo (N+1 se bachne ke liye)
    commission_rows = (
        db.query(PolicyCommission)
        .filter(PolicyCommission.policy_id.in_(policy_ids))
        .all()
    )
    commission_map = {c.policy_id: c for c in commission_rows}

    total_commission = 0
    pending_commission = 0
    received_commission = 0
    breakdown = []

    for p in policies:
        commission_row = commission_map.get(p.id)
        rate = float(commission_row.commission_rate) if commission_row else 0
        status = commission_row.commission_status if commission_row else "pending"

        premium = float(p.premium or 0)
        earned = round(premium * rate / 100, 2)

        total_commission += earned
        if status == "received":
            received_commission += earned
        else:
            pending_commission += earned

        breakdown.append({
            "policy_id": p.id,
            "policy_holder": p.policy_holder,
            "policy_number": p.policy_number,
            "premium": premium,
            "commission_rate": rate,
            "commission_earned": earned,
            "commission_status": status,
        })

    result = {
        "total_commission": round(total_commission, 2),
        "pending_commission": round(pending_commission, 2),
        "received_commission": round(received_commission, 2),
        "policy_count": len(policies),
        "breakdown": breakdown,
    }
    return customhelper.printCustmMsg(200, "TRUE", "Commission summary fetched", result)


def set_commission_rate(db, policy_id, rate):
    try:
        row = db.query(PolicyCommission).filter(PolicyCommission.policy_id == policy_id).first()
        if not row:
            row = PolicyCommission(policy_id=policy_id, commission_rate=rate)
            db.add(row)
        else:
            row.commission_rate = rate

        db.commit()
        return customhelper.printCustmMsg(200, "TRUE", "Commission rate updated")
    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)


def update_commission_status(db, policy_id, status):
    try:
        row = db.query(PolicyCommission).filter(PolicyCommission.policy_id == policy_id).first()
        if not row:
            return customhelper.printCustmMsg(200, "FALSE", "Commission record not found — set a rate first")

        row.commission_status = status
        db.commit()
        return customhelper.printCustmMsg(200, "TRUE", "Commission status updated")
    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)