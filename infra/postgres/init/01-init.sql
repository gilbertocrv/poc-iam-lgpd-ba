CREATE TABLE IF NOT EXISTS audit_access_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(120) NOT NULL,
    user_role VARCHAR(60) NOT NULL,
    route VARCHAR(120) NOT NULL,
    action VARCHAR(30) NOT NULL DEFAULT 'READ',
    ip_address INET,
    user_agent TEXT,
    legal_basis VARCHAR(120) NOT NULL,
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    correlation_id UUID NOT NULL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_access_logs_route_time
    ON audit_access_logs (route, accessed_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_access_logs_user_time
    ON audit_access_logs (user_id, accessed_at DESC);
