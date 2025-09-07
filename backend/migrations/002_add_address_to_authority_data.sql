-- Add address column to authoritative_contacts table
ALTER TABLE authoritative_contacts 
ADD COLUMN IF NOT EXISTS address VARCHAR(500);

-- Update existing records with empty address if needed
UPDATE authoritative_contacts 
SET address = '' 
WHERE address IS NULL;