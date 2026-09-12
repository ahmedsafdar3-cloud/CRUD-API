CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT,
    done BOOLEAN
);

INSERT INTO tasks (title, done)
SELECT *
FROM (
    VALUES
        ('Buy milk', FALSE),
        ('Walk the dog', FALSE),
        ('Finish assignment', TRUE)
) AS seed(title, done)
WHERE NOT EXISTS (
    SELECT 1 FROM tasks
);