-- create bell_alert
-- depends: 


CREATE TABLE public.bell_alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_excel_id INTEGER NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    notification_date TIMESTAMP NOT NULL,
    expiry_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    CONSTRAINT fk_bell_alert_user
        FOREIGN KEY (user_id)
        REFERENCES public.users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_bell_alert_user_excel
        FOREIGN KEY (user_excel_id)
        REFERENCES public.user_excel(id)
        ON DELETE CASCADE
);