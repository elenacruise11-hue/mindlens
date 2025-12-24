-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (already exists in your auth system)
-- This is a reference to your existing users table
-- CREATE TABLE IF NOT EXISTS users (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     email TEXT UNIQUE NOT NULL,
--     full_name TEXT,
--     created_at TIMESTAMPTZ DEFAULT NOW(),
--     updated_at TIMESTAMPTZ DEFAULT NOW()
-- );

-- Stress Scans table
CREATE TABLE IF NOT EXISTS stress_scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    scanned_at TIMESTAMPTZ DEFAULT NOW(),
    emotion TEXT,
    emotion_confidence FLOAT,
    jaw_tension FLOAT,
    posture_quality TEXT CHECK (posture_quality IN ('poor', 'fair', 'good')),
    overall_stress FLOAT,
    raw_metrics JSONB,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index for faster lookups by user_id
CREATE INDEX IF NOT EXISTS idx_stress_scans_user_id ON stress_scans(user_id);
CREATE INDEX IF NOT EXISTS idx_stress_scans_scanned_at ON stress_scans(scanned_at);

-- Health Metrics table
CREATE TABLE IF NOT EXISTS health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    blood_pressure_category TEXT,
    heart_rate INTEGER,
    cholesterol INTEGER,
    glucose INTEGER,
    insulin FLOAT,
    stress_level FLOAT,
    mental_health_score INTEGER,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index for faster lookups by user_id
CREATE INDEX IF NOT EXISTS idx_health_metrics_user_id ON health_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_health_metrics_recorded_at ON health_metrics(recorded_at);

-- User Preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'system')),
    notifications_enabled BOOLEAN DEFAULT true,
    data_sharing BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index for user preferences lookup
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Enable Row Level Security on all tables
ALTER TABLE stress_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for stress_scans
CREATE POLICY "Users can view their own stress scans" 
ON stress_scans FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own stress scans" 
ON stress_scans FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for health_metrics
CREATE POLICY "Users can view their own health metrics" 
ON health_metrics FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own health metrics" 
ON health_metrics FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for user_preferences
CREATE POLICY "Users can view their own preferences" 
ON user_preferences FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences" 
ON user_preferences FOR UPDATE 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences" 
ON user_preferences FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Create a function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to update updated_at column
CREATE TRIGGER update_stress_scans_updated_at
BEFORE UPDATE ON stress_scans
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_health_metrics_updated_at
BEFORE UPDATE ON health_metrics
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add comments to tables and columns
COMMENT ON TABLE stress_scans IS 'Stores stress scan results from facial and posture analysis';
COMMENT ON COLUMN stress_scans.emotion IS 'Detected emotion from facial analysis';
COMMENT ON COLUMN stress_scans.posture_quality IS 'Overall posture quality rating';
COMMENT ON COLUMN stress_scans.overall_stress IS 'Calculated stress level from 0-10';

COMMENT ON TABLE health_metrics IS 'Stores health metrics and predictions';
COMMENT ON COLUMN health_metrics.blood_pressure_category IS 'Category based on systolic/diastolic values';

COMMENT ON TABLE user_preferences IS 'Stores user preferences for the application';

-- Create a view for dashboard metrics
CREATE OR REPLACE VIEW user_dashboard_metrics AS
WITH latest_health AS (
    SELECT 
        user_id,
        recorded_at,
        blood_pressure_systolic,
        blood_pressure_diastolic,
        heart_rate,
        stress_level,
        mental_health_score,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY recorded_at DESC) as rn
    FROM health_metrics
),
latest_stress AS (
    SELECT 
        user_id,
        scanned_at,
        emotion,
        overall_stress,
        posture_quality,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY scanned_at DESC) as rn
    FROM stress_scans
)
SELECT 
    u.id as user_id,
    u.email,
    lh.recorded_at as last_health_check,
    lh.blood_pressure_systolic,
    lh.blood_pressure_diastolic,
    lh.heart_rate,
    lh.stress_level as health_stress_level,
    lh.mental_health_score,
    ls.scanned_at as last_stress_scan,
    ls.emotion,
    ls.overall_stress as stress_scan_score,
    ls.posture_quality
FROM 
    auth.users u
LEFT JOIN latest_health lh ON u.id = lh.user_id AND lh.rn = 1
LEFT JOIN latest_stress ls ON u.id = ls.user_id AND ls.rn = 1;

-- Create a function to get user's stress trend
CREATE OR REPLACE FUNCTION get_stress_trend(p_user_id UUID, p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    date DATE,
    avg_stress FLOAT,
    scan_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        scanned_at::DATE as date,
        AVG(overall_stress) as avg_stress,
        COUNT(*) as scan_count
    FROM 
        stress_scans
    WHERE 
        user_id = p_user_id
        AND scanned_at >= (CURRENT_DATE - (p_days || ' days')::INTERVAL)
    GROUP BY 
        scanned_at::DATE
    ORDER BY 
        date DESC;
END;
$$ LANGUAGE plpgsql;
