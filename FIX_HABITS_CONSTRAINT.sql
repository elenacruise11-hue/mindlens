ALTER TABLE public.habits 
DROP CONSTRAINT IF EXISTS habits_social_interaction_check;

ALTER TABLE public.habits 
ADD CONSTRAINT habits_social_interaction_check 
CHECK (social_interaction IN ('None', 'Low', 'Medium', 'High'));

SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'public.habits'::regclass
  AND conname LIKE '%social%';
