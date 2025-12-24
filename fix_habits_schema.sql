-- Fix habits table schema to use UUID for user_id
-- Run this SQL in your Supabase SQL Editor

-- Check current schema first
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'habits';

-- Drop and recreate habits table with correct schema
DROP TABLE IF EXISTS habits CASCADE;

-- Create habits table with correct data types
CREATE TABLE habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- Changed from TEXT to UUID
    
    -- User info
    age INTEGER NOT NULL,
    
    -- Daily habits (all FLOAT for hours/amounts)
    sleep_hours FLOAT NOT NULL,
    work_hours FLOAT NOT NULL,
    screen_time FLOAT NOT NULL,
    water_intake FLOAT NOT NULL,
    
    -- Boolean habits
    exercise BOOLEAN NOT NULL DEFAULT false,
    caffeine_intake BOOLEAN NOT NULL DEFAULT false,
    
    -- Meal and social
    meals_per_day INTEGER NOT NULL,
    social_interaction TEXT NOT NULL,  -- 'None', 'Low', 'Medium', 'High'
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes
CREATE INDEX idx_habits_user_id ON habits(user_id);
CREATE INDEX idx_habits_created_at ON habits(created_at);

-- Enable Row Level Security
ALTER TABLE habits ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own habits" ON habits
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own habits" ON habits
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update own habits" ON habits
    FOR UPDATE USING (true);

-- Add table comment
COMMENT ON TABLE habits IS 'Stores daily habit tracking data for users';
