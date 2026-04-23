CREATE OR REPLACE PROCEDURE upsert_contact(p_first VARCHAR, p_last VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_first) THEN
        UPDATE phonebook SET phone = p_phone WHERE first_name = p_first;
    ELSE
        INSERT INTO phonebook(first_name, last_name, phone)
        VALUES(p_first, p_last, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_contacts(p_data TEXT[][])
LANGUAGE plpgsql AS $$
DECLARE
    item TEXT[];
    invalid_data TEXT[] := '{}';
BEGIN
    FOREACH item SLICE 1 IN ARRAY p_data LOOP
        IF item[3] ~ '^\+?[0-9]{7,15}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = item[1]) THEN
                UPDATE phonebook SET phone = item[3] WHERE first_name = item[1];
            ELSE
                INSERT INTO phonebook(first_name, last_name, phone)
                VALUES(item[1], item[2], item[3]);
            END IF;
        ELSE
            invalid_data := array_append(invalid_data, item[1] || ' - ' || item[3]);
        END IF;
    END LOOP;

    IF array_length(invalid_data, 1) > 0 THEN
        RAISE NOTICE 'Некорректные данные: %', array_to_string(invalid_data, ', ');
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_type = 'name' THEN
        DELETE FROM phonebook WHERE first_name = p_value;
    ELSIF p_type = 'phone' THEN
        DELETE FROM phonebook WHERE phone = p_value;
    END IF;
END;
$$;