import random

from fastapi import APIRouter, Depends

import modules.login.models as models
import modules.login.schemas as schemas
import authentication.auth as auth

routes = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _rand_delta():
    v = round(random.uniform(-6, 8), 1)
    trend = "up" if v > 0.5 else "down" if v < -0.5 else "flat"
    sign = "+" if v > 0 else ""
    return f"{sign}{v}%", trend


@routes.get("/stats", response_model=schemas.DashboardStats)
def stats(current: models.Users = Depends(auth.get_current_user)):
    """Protected. Returns the cards rendered on the dashboard.
    Values are demo/randomised — wire to real queries in production."""

    def card(title, value, icon, hint):
        delta, trend = _rand_delta()
        return schemas.DashboardCard(
            title=title, value=value, delta=delta, trend=trend, icon=icon, hint=hint
        )

    cards = [
        card("Active Users", f"{random.randint(800, 1500):,}", "users", "Logged in last 24h"),
        card("Grid Load", f"{random.randint(4200, 5200)} MW", "activity", "Current demand"),
        card("Revenue", f"₹{random.randint(40, 90)}.{random.randint(0,9)}L", "wallet", "This month"),
        card("Open Alerts", str(random.randint(0, 12)), "bell", "Needs attention"),
        card("Uptime", f"{round(random.uniform(99.1, 99.99), 2)}%", "shield", "Last 30 days"),
        card("Pending Reports", str(random.randint(2, 20)), "file", "Awaiting review"),
    ]
    return schemas.DashboardStats(
        greeting=f"Welcome back, {current.name.split(' ')[0]}",
        cards=cards,
    )

