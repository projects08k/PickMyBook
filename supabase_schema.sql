-- PickMyBook Database Schema for Supabase
-- Run this in your Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- 1. Reading History Table
CREATE TABLE IF NOT EXISTS reading_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    author TEXT,
    genre TEXT,
    mood TEXT,
    score REAL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- 2. Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    book_title TEXT NOT NULL,
    genre TEXT,
    mood TEXT,
    accepted BOOLEAN DEFAULT FALSE,
    score REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- 3. User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    preferences JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- 4. Enable Row Level Security (RLS)
ALTER TABLE reading_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
-- 5. Create RLS Policies (Users can only access their own data)
CREATE POLICY "Users can view own reading history" ON reading_history FOR
SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own reading history" ON reading_history FOR
INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own reading history" ON reading_history FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Users can view own feedback" ON feedback FOR
SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own feedback" ON feedback FOR
INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view own preferences" ON user_preferences FOR
SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own preferences" ON user_preferences FOR
INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own preferences" ON user_preferences FOR
UPDATE USING (auth.uid() = user_id);
-- 6. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reading_history_user ON reading_history(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_reading_history_created ON reading_history(created_at DESC);
-- 7. RL Model Table (Global Q-Learning State)
-- Stores the Q-table for reinforcement learning across all users
CREATE TABLE IF NOT EXISTS rl_model (
    id TEXT PRIMARY KEY DEFAULT 'global',
    q_table JSONB DEFAULT '{}',
    stats JSONB DEFAULT '{"total_accepts": 0, "total_rejects": 0, "learning_steps": 0}',
    epsilon REAL DEFAULT 0.1,
    learning_rate REAL DEFAULT 0.1,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Insert default global model row
INSERT INTO rl_model (id, q_table, stats)
VALUES (
        'global',
        '{}',
        '{"total_accepts": 0, "total_rejects": 0, "learning_steps": 0}'
    ) ON CONFLICT (id) DO NOTHING;
-- Allow all authenticated users to read/update the global model
ALTER TABLE rl_model ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view rl_model" ON rl_model FOR
SELECT USING (true);
CREATE POLICY "Authenticated users can insert rl_model" ON rl_model FOR
INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY "Authenticated users can update rl_model" ON rl_model FOR
UPDATE USING (auth.uid() IS NOT NULL);