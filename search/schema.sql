CREATE TABLE apartments(
    id CHAR(32) PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
CREATE TABLE reservations(
    id CHAR(32) PRIMARY KEY,
    app_id CHAR(32) NOT NULL REFERENCES apartments(id) ON DELETE CASCADE,
    start INT(8) NOT NULL,
    end INT(8) NOT NULL
);
