-- depends:

CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY,
    current_player INTEGER NOT NULL CHECK (current_player IN (1, 2)),  -- 1: BLACK, 2: WHITE
    status VARCHAR(20) NOT NULL CHECK (status IN ('playing', 'finished')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);