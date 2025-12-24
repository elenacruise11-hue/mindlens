-- Alter stress_scan table to match the required schema
-- This preserves existing data while fixing column types
-- Run this SQL in your Supabase SQL Editor

-- Step 1: Alter user_id column type from TEXT to UUID (if needed)
-- First check if conversion is needed
DO $$ 
BEGIN
    -- Try to alter the column type
    BEGIN
        ALTER TABLE public.stress_scan 
        ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
    EXCEPTION 
        WHEN OTHERS THEN
            RAISE NOTICE 'user_id column already UUID or conversion failed';
    END;
END $$;

-- Step 2: Alter eyebrow_raise from BOOLEAN to FLOAT (if needed)
DO $$ 
BEGIN
    BEGIN
        ALTER TABLE public.stress_scan 
        ALTER COLUMN eyebrow_raise TYPE FLOAT USING 
            CASE 
                WHEN eyebrow_raise::TEXT = 'true' THEN 1.0
                WHEN eyebrow_raise::TEXT = 'false' THEN 0.0
                ELSE eyebrow_raise::TEXT::FLOAT
            END;
    EXCEPTION 
        WHEN OTHERS THEN
            RAISE NOTICE 'eyebrow_raise column already FLOAT or conversion failed';
    END;
END $$;

-- Step 3: Add foreign key constraint to users table (if not exists)
DO $$ 
BEGIN
    BEGIN
        ALTER TABLE public.stress_scan
        ADD CONSTRAINT stress_scan_user_id_fkey 
        FOREIGN KEY (user_id) 
        REFERENCES public.users(id) 
        ON DELETE CASCADE;
    EXCEPTION 
        WHEN duplicate_object THEN
            RAISE NOTICE 'Foreign key constraint already exists';
    END;
END $$;

-- Step 4: Ensure all other columns have correct types
-- These should already be correct, but we'll verify

-- Ensure emotion is TEXT
ALTER TABLE public.stress_scan 
ALTER COLUMN emotion TYPE TEXT;

-- Ensure all numeric fields are FLOAT
ALTER TABLE public.stress_scan 
ALTER COLUMN emotion_confidence TYPE FLOAT USING emotion_confidence::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN mouth_open TYPE FLOAT USING mouth_open::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN jaw_clench_score TYPE FLOAT USING jaw_clench_score::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN slouch_score TYPE FLOAT USING slouch_score::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN head_tilt_angle TYPE FLOAT USING head_tilt_angle::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN shoulder_alignment_diff TYPE FLOAT USING shoulder_alignment_diff::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN spine_curve_ratio TYPE FLOAT USING spine_curve_ratio::FLOAT;

ALTER TABLE public.stress_scan 
ALTER COLUMN pose_confidence TYPE FLOAT USING pose_confidence::FLOAT;

-- Ensure posture_quality is TEXT
ALTER TABLE public.stress_scan 
ALTER COLUMN posture_quality TYPE TEXT;

-- Ensure image_url is TEXT
ALTER TABLE public.stress_scan 
ALTER COLUMN image_url TYPE TEXT;

-- Ensure scanned_at is TIMESTAMPTZ with default
ALTER TABLE public.stress_scan 
ALTER COLUMN scanned_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.stress_scan 
ALTER COLUMN scanned_at SET DEFAULT NOW();

-- Step 5: Verify the schema
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'stress_scan' 
ORDER BY ordinal_position;

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE '✅ stress_scan table schema updated successfully!';
END $$;
