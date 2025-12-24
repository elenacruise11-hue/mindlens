-- Fix stress_scan table schema to match the data types we're sending
-- Run this SQL in your Supabase SQL Editor

-- First, let's see the current schema
-- You can check it with: SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'stress_scan';

-- Drop the table and recreate with correct schema
DROP TABLE IF EXISTS stress_scan CASCADE;

-- Create stress_scan table with correct data types
CREATE TABLE stress_scan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- Changed from TEXT to UUID
    scanned_at TIMESTAMPTZ DEFAULT now(),
    
    -- Emotion fields
    emotion TEXT,
    emotion_confidence FLOAT,
    
    -- Facial feature fields (all FLOAT, not BOOLEAN)
    mouth_open FLOAT,
    eyebrow_raise FLOAT,  -- Changed from BOOLEAN to FLOAT
    jaw_clench_score FLOAT,
    
    -- Posture fields
    posture_quality TEXT,
    slouch_score FLOAT,
    head_tilt_angle FLOAT,
    shoulder_alignment_diff FLOAT,
    spine_curve_ratio FLOAT,
    pose_confidence FLOAT,
    
    -- Optional fields
    image_url TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX idx_stress_scan_user_id ON stress_scan(user_id);
CREATE INDEX idx_stress_scan_scanned_at ON stress_scan(scanned_at);
CREATE INDEX idx_stress_scan_created_at ON stress_scan(created_at);

-- Enable Row Level Security
ALTER TABLE stress_scan ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own scans" ON stress_scan
    FOR SELECT USING (true);  -- Allow all for now, adjust based on your auth

CREATE POLICY "Users can insert own scans" ON stress_scan
    FOR INSERT WITH CHECK (true);  -- Allow all for now, adjust based on your auth

CREATE POLICY "Users can update own scans" ON stress_scan
    FOR UPDATE USING (true);  -- Allow all for now, adjust based on your auth

-- Add comment to table
COMMENT ON TABLE stress_scan IS 'Stores stress analysis results from facial and posture detection';

-- Add comments to important columns
COMMENT ON COLUMN stress_scan.eyebrow_raise IS 'Float value 0.0-1.0 indicating eyebrow raise level';
COMMENT ON COLUMN stress_scan.user_id IS 'UUID reference to users table';
