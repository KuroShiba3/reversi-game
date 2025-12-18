-- depends: create_games_table

CREATE TABLE IF NOT EXISTS board_cells (
    id SERIAL PRIMARY KEY,
    game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    row INTEGER NOT NULL CHECK (row BETWEEN 0 AND 7),
    col INTEGER NOT NULL CHECK (col BETWEEN 0 AND 7),
    disc INTEGER NOT NULL CHECK (disc IN (0, 1, 2)),  -- 0: EMPTY, 1: BLACK, 2: WHITE
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, row, col)
);

CREATE INDEX IF NOT EXISTS idx_board_cells_game_id ON board_cells(game_id);
