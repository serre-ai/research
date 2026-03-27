-- Add 'blocked' to projects.status CHECK constraint.
-- 'blocked' = waiting on external action (e.g. LaTeX install, human review).
-- Distinct from 'paused' (deliberately stopped by user).

ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_status_check;
ALTER TABLE projects ADD CONSTRAINT projects_status_check
  CHECK (status IN ('active', 'paused', 'blocked', 'review', 'completed'));
