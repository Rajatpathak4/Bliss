from sqlalchemy import func

from helper import customhelper
from modules.Upload_Excel.models import UserExcel


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