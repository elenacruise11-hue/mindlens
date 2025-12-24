#!/usr/bin/env python3
"""
Database Migration Script
Fixes stress_scan and habits table schemas
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def run_migration():
    """Run database migration to fix table schemas"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Supabase credentials not found in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Migration SQL for stress_scan table
        stress_scan_migration = """
        -- Fix stress_scan table schema
        
        -- Alter eyebrow_raise from BOOLEAN to FLOAT
        ALTER TABLE public.stress_scan 
        ALTER COLUMN eyebrow_raise TYPE FLOAT USING 
            CASE 
                WHEN eyebrow_raise::TEXT = 'true' THEN 1.0
                WHEN eyebrow_raise::TEXT = 'false' THEN 0.0
                ELSE eyebrow_raise::TEXT::FLOAT
            END;
        
        -- Alter user_id to UUID if needed
        ALTER TABLE public.stress_scan 
        ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
        
        -- Ensure all numeric fields are FLOAT
        ALTER TABLE public.stress_scan ALTER COLUMN emotion_confidence TYPE FLOAT USING emotion_confidence::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN mouth_open TYPE FLOAT USING mouth_open::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN jaw_clench_score TYPE FLOAT USING jaw_clench_score::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN slouch_score TYPE FLOAT USING slouch_score::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN head_tilt_angle TYPE FLOAT USING head_tilt_angle::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN shoulder_alignment_diff TYPE FLOAT USING shoulder_alignment_diff::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN spine_curve_ratio TYPE FLOAT USING spine_curve_ratio::FLOAT;
        ALTER TABLE public.stress_scan ALTER COLUMN pose_confidence TYPE FLOAT USING pose_confidence::FLOAT;
        """
        
        habits_migration = """
        -- Fix habits table schema
        
        -- Alter user_id to UUID
        ALTER TABLE public.habits 
        ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
        
        -- Ensure correct types
        ALTER TABLE public.habits ALTER COLUMN age TYPE INTEGER USING age::INTEGER;
        ALTER TABLE public.habits ALTER COLUMN sleep_hours TYPE FLOAT USING sleep_hours::FLOAT;
        ALTER TABLE public.habits ALTER COLUMN work_hours TYPE FLOAT USING work_hours::FLOAT;
        ALTER TABLE public.habits ALTER COLUMN screen_time TYPE FLOAT USING screen_time::FLOAT;
        ALTER TABLE public.habits ALTER COLUMN water_intake TYPE FLOAT USING water_intake::FLOAT;
        ALTER TABLE public.habits ALTER COLUMN meals_per_day TYPE INTEGER USING meals_per_day::INTEGER;
        """
        
        print("\n🔧 Running stress_scan table migration...")
        try:
            # Execute stress_scan migration
            result = supabase.rpc('exec_sql', {'query': stress_scan_migration}).execute()
            print("✅ stress_scan table migrated successfully")
        except Exception as e:
            print(f"⚠️  stress_scan migration: {e}")
            print("\n📋 Please run this SQL manually in Supabase SQL Editor:")
            print(stress_scan_migration)
        
        print("\n🔧 Running habits table migration...")
        try:
            # Execute habits migration
            result = supabase.rpc('exec_sql', {'query': habits_migration}).execute()
            print("✅ habits table migrated successfully")
        except Exception as e:
            print(f"⚠️  habits migration: {e}")
            print("\n📋 Please run this SQL manually in Supabase SQL Editor:")
            print(habits_migration)
        
        print("\n" + "="*60)
        print("🎉 Migration complete!")
        print("="*60)
        print("\n📝 Manual Steps Required:")
        print("1. Go to Supabase Dashboard → SQL Editor")
        print("2. Copy the SQL from above (if automatic migration failed)")
        print("3. Run the SQL queries")
        print("4. Test your app again")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📋 MANUAL MIGRATION REQUIRED:")
        print("\nGo to Supabase SQL Editor and run:")
        print("\n--- FOR stress_scan TABLE ---")
        print("""
ALTER TABLE public.stress_scan 
ALTER COLUMN eyebrow_raise TYPE FLOAT USING 
    CASE 
        WHEN eyebrow_raise::TEXT = 'true' THEN 1.0
        WHEN eyebrow_raise::TEXT = 'false' THEN 0.0
        ELSE eyebrow_raise::TEXT::FLOAT
    END;

ALTER TABLE public.stress_scan ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
        """)
        
        print("\n--- FOR habits TABLE ---")
        print("""
ALTER TABLE public.habits ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
        """)
        return False

if __name__ == "__main__":
    print("🚀 MindLens AI - Database Migration")
    print("="*60)
    run_migration()
