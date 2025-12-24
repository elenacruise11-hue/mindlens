-- Alter habits table to use UUID for user_id
-- This preserves existing data while fixing column types
-- Run this SQL in your Supabase SQL Editor

-- Step 1: Alter user_id column type from TEXT to UUID (if needed)
DO $$ 
BEGIN
    BEGIN
        ALTER TABLE public.habits 
        ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
    EXCEPTION 
        WHEN OTHERS THEN
            RAISE NOTICE 'user_id column already UUID or conversion failed';
    END;
END $$;

-- Step 2: Add foreign key constraint to users table (if not exists)
DO $$ 
BEGIN
    BEGIN
        ALTER TABLE public.habits
        ADD CONSTRAINT habits_user_id_fkey 
        FOREIGN KEY (user_id) 
        REFERENCES public.users(id) 
        ON DELETE CASCADE;
    EXCEPTION 
        WHEN duplicate_object THEN
            RAISE NOTICE 'Foreign key constraint already exists';
    END;
END $$;

-- Step 3: Ensure all columns have correct types

-- Age should be INTEGER
ALTER TABLE public.habits 
ALTER COLUMN age TYPE INTEGER USING age::INTEGER;

-- Hours/amounts should be FLOAT
ALTER TABLE public.habits 
ALTER COLUMN sleep_hours TYPE FLOAT USING sleep_hours::FLOAT;

ALTER TABLE public.habits 
ALTER COLUMN work_hours TYPE FLOAT USING work_hours::FLOAT;

ALTER TABLE public.habits 
ALTER COLUMN screen_time TYPE FLOAT USING screen_time::FLOAT;

ALTER TABLE public.habits 
ALTER COLUMN water_intake TYPE FLOAT USING water_intake::FLOAT;

-- Boolean fields
ALTER TABLE public.habits 
ALTER COLUMN exercise TYPE BOOLEAN USING 
    CASE 
        WHEN exercise::TEXT IN ('true', 't', '1', 'yes') THEN true
        ELSE false
    END;

ALTER TABLE public.habits 
ALTER COLUMN caffeine_intake TYPE BOOLEAN USING 
    CASE 
        WHEN caffeine_intake::TEXT IN ('true', 't', '1', 'yes') THEN true
        ELSE false
    END;

-- Meals should be INTEGER
ALTER TABLE public.habits 
ALTER COLUMN meals_per_day TYPE INTEGER USING meals_per_day::INTEGER;

-- Social interaction should be TEXT
ALTER TABLE public.habits 
ALTER COLUMN social_interaction TYPE TEXT;

-- Ensure created_at has default
ALTER TABLE public.habits 
ALTER COLUMN created_at SET DEFAULT NOW();

-- Step 4: Verify the schema
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'habits' 
ORDER BY ordinal_position;

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE '✅ habits table schema updated successfully!';
END $$;
