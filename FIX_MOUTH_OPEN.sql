ALTER TABLE public.stress_scan ALTER COLUMN mouth_open TYPE FLOAT USING CASE WHEN mouth_open::TEXT = 'true' THEN 1.0 WHEN mouth_open::TEXT = 'false' THEN 0.0 ELSE mouth_open::TEXT::FLOAT END;

ALTER TABLE public.stress_scan ALTER COLUMN jaw_clench_score TYPE FLOAT USING CASE WHEN jaw_clench_score::TEXT = 'true' THEN 1.0 WHEN jaw_clench_score::TEXT = 'false' THEN 0.0 ELSE jaw_clench_score::TEXT::FLOAT END;

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'stress_scan' 
  AND column_name IN ('eyebrow_raise', 'mouth_open', 'jaw_clench_score', 'user_id')
ORDER BY column_name;
