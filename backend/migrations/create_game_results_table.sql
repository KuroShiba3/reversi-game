-- depends: create_games_table

CREATE TABLE IF NOT EXISTS game_results (
    game_id UUID PRIMARY KEY REFERENCES games(id) ON DELETE CASCADE,
    winner INTEGER NOT NULL CHECK (winner IN (1, 2, 3)),  -- 1: BLACK, 2: WHITE, 3: DRAW
    black_score INTEGER NOT NULL CHECK (black_score >= 0 AND black_score <= 64),
    white_score INTEGER NOT NULL CHECK (white_score >= 0 AND white_score <= 64),
    finished_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_game_id ON game_results(game_id);
