-- 1. add_phone ────────────────────────────────────────────────
--    Adds a phone number to an existing contact looked up by name.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Resolve contact by first_name (or "first last" composite)
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(first_name || COALESCE(' ' || last_name, '')) = LOWER(TRIM(p_contact_name))
       OR LOWER(first_name) = LOWER(TRIM(p_contact_name))
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Must be home, work, or mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- 2. move_to_group ───────────────────────────────────────────
--    Moves a contact to the specified group, creating the group
--    if it does not already exist.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(first_name || COALESCE(' ' || last_name, '')) = LOWER(TRIM(p_contact_name))
       OR LOWER(first_name) = LOWER(TRIM(p_contact_name))
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Upsert group
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- 3. search_contacts ─────────────────────────────────────────
--    Full-field search: first/last name, email, and ALL phones
--    in the phones table.  Returns a result set.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_pattern TEXT := '%' || LOWER(TRIM(p_query)) || '%';
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name AS group_name
    FROM contacts c
    LEFT JOIN groups g  ON g.id  = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE
        LOWER(c.first_name)                          LIKE v_pattern
        OR LOWER(COALESCE(c.last_name,  ''))         LIKE v_pattern
        OR LOWER(COALESCE(c.email,      ''))         LIKE v_pattern
        OR LOWER(COALESCE(ph.phone,     ''))         LIKE v_pattern
    ORDER BY c.first_name, c.last_name;
END;
$$;
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_id   INTEGER,
    created_at TIMESTAMP
) 
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM contacts
    ORDER BY first_name, last_name
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;