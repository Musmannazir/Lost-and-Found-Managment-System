-- DROP existing tables for reset (if needed)
-- DROP TABLE IF EXISTS claims, deleted_claims, items, deleted_items, locations, admins, deleted_users, users, admin_actions CASCADE;

-- USERS
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL CHECK (name ~ '^[A-Za-z\s]+$'),
    email VARCHAR(100) UNIQUE NOT NULL CHECK (email ~ '^[A-Za-z0-9._%+-]+@gmail\.com$'),
    phone VARCHAR(15) CHECK (phone ~ '^03\d{9}$'),
    role VARCHAR(20) CHECK (role IN ('Student', 'Staff', 'Guest')) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- DELETED USERS
CREATE TABLE deleted_users (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(20),
    password VARCHAR(255),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADMINS
CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- LOCATIONS
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL
);

-- ITEMS
CREATE TABLE items (
    item_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    date_reported DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Lost' CHECK (status IN ('Lost', 'Found', 'Returned')),
    image_path TEXT,
    location_id INTEGER REFERENCES locations(location_id) ON DELETE CASCADE,
    reported_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

-- DELETED ITEMS
CREATE TABLE deleted_items (
    deleted_item_id SERIAL PRIMARY KEY,
    item_id INTEGER,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    date_reported DATE NOT NULL,
    status VARCHAR(20),
    image_path TEXT,
    location_id INTEGER REFERENCES locations(location_id) ON DELETE CASCADE,
    reported_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CLAIMS
CREATE TABLE claims (
    claim_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(item_id) ON DELETE CASCADE,
    claimed_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    claim_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    approved_by INTEGER REFERENCES admins(admin_id) ON DELETE SET NULL,
    loss_location TEXT,
    loss_date DATE
);

-- DELETED CLAIMS
CREATE TABLE deleted_claims (
    claim_id INTEGER PRIMARY KEY,
    item_id INTEGER,
    claimed_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    claim_date DATE,
    status VARCHAR(20),
    approved_by INTEGER,
    loss_location TEXT,
    loss_date DATE,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADMIN ACTIONS
CREATE TABLE admin_actions (
    action_id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admins(admin_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('Create', 'Update', 'Delete')),
    action_description TEXT,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_items_reported_by ON items(reported_by);
CREATE INDEX idx_claims_item_id ON claims(item_id);
CREATE INDEX idx_claims_claimed_by ON claims(claimed_by);
CREATE INDEX idx_deleted_items_reported_by ON deleted_items(reported_by);
CREATE INDEX idx_deleted_claims_claimed_by ON deleted_claims(claimed_by);

-- TRIGGERS FOR ADMIN ACTIONS
-- Trigger for deleted_items: Logs deletion of items
CREATE OR REPLACE FUNCTION log_deleted_item_action()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO admin_actions (admin_id, action_type, action_description)
    VALUES (1, 'Delete', 'Deleted item ID ' || COALESCE(NEW.item_id::TEXT, 'unknown') || ': ' || COALESCE(NEW.title, 'unknown'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER deleted_item_trigger
AFTER INSERT ON deleted_items
FOR EACH ROW
EXECUTE FUNCTION log_deleted_item_action();

-- Trigger for deleted_users: Logs deletion of users
CREATE OR REPLACE FUNCTION log_deleted_user_action()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO admin_actions (admin_id, action_type, action_description)
    VALUES (1, 'Delete', 'Deleted user ID ' || COALESCE(NEW.user_id::TEXT, 'unknown') || ': ' || COALESCE(NEW.name, 'unknown'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER deleted_user_trigger
AFTER INSERT ON deleted_users
FOR EACH ROW
EXECUTE FUNCTION log_deleted_user_action();

-- Trigger for deleted_claims: Logs deletion of claims
CREATE OR REPLACE FUNCTION log_deleted_claim_action()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO admin_actions (admin_id, action_type, action_description)
    VALUES (1, 'Delete', 'Deleted claim ID ' || COALESCE(NEW.claim_id::TEXT, 'unknown') || ' for item ID ' || COALESCE(NEW.item_id::TEXT, 'unknown'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER deleted_claim_trigger
AFTER INSERT ON deleted_claims
FOR EACH ROW
EXECUTE FUNCTION log_deleted_claim_action();

-- DEMO DATA INSERTIONS
-- USERS
INSERT INTO users (name, email, phone, role, password) VALUES
('Alice Smith', 'alice@gmail.com', '03987643210', 'Student', '0987'),
('Bob Johnson', 'bob@gmail.com', '03912345680', 'Staff', '0987'),
('Charlie Brown', 'charlie@gmail.com', '03955556677', 'Student', '0987'),
('Diana Prince', 'diana@gmail.com', '03977778899', 'Guest', '0987');

-- ADMINS
INSERT INTO admins (name, email, username, password) VALUES
('Usman', 'usman@gmail.com', 'usman', 'Admin12'),
('Rafay', 'rafay@gmail.com', 'rafay', 'Admin12'),
('Qasim', 'qasim@gmail.com', 'qasim', 'Admin12'),
('Shaheer', 'shaheer@gmail.com', 'shaheer', 'Admin12');

-- LOCATIONS
INSERT INTO locations (location_name) VALUES
('Library Entrance'),
('Cafeteria'),
('FES'),
('FCSE'),
('FME'),
('FMCE'),
('Acb'),
('Sports Complex'),
('Ground'),
('Raju'),
('Hot and Spicy');

-- ITEMS
INSERT INTO items (title, description, date_reported, status, image_path, location_id, reported_by) VALUES
('Lost Wallet', 'Brown leather wallet with cash and ID cards.', '2025-04-20', 'Lost', 'images/wallet1.jpg', 1, 1), -- Alice
('Found USB Drive', 'Black 16GB USB drive near lab area.', '2025-04-21', 'Found', 'images/usb1.jpg', 3, 2), -- Bob
('Lost Jacket', 'Blue denim jacket left in cafeteria.', '2025-04-19', 'Lost', 'images/jacket1.jpg', 2, 3), -- Charlie
('Found Laptop', 'Silver MacBook found in lecture hall.', '2025-04-22', 'Found', 'images/laptop1.jpg', 4, 4); -- Diana

-- CLAIMS
INSERT INTO claims (item_id, claimed_by, claim_date, status, loss_location, loss_date) VALUES
(1, 2, '2025-05-01', 'Pending', 'Library Area', '2025-04-20'), -- Bob claims Alice's wallet
(2, 3, '2025-05-02', 'Pending', 'Lab Area', '2025-04-21'), -- Charlie claims Bob's USB
(3, 4, '2025-05-03', 'Pending', 'Cafeteria', '2025-04-19'), -- Diana claims Charlie's jacket
(4, 1, '2025-05-04', 'Approved', 'Lecture Hall', '2025-04-22'); -- Alice claims Diana's laptop

-- Sample deleted data for testing
INSERT INTO deleted_users (user_id, name, email, phone, role, password, deleted_at) VALUES
(5, 'Eve Deleted', 'eve@gmail.com', '03900000000', 'Student', 'hashed_password_12345', CURRENT_TIMESTAMP);

INSERT INTO deleted_items (item_id, title, description, date_reported, status, image_path, location_id, reported_by, deleted_at) VALUES
(10, 'Deleted Phone', 'Lost iPhone', '2025-04-18', 'Lost', 'images/phone.jpg', 1, 1, CURRENT_TIMESTAMP); -- Alice

INSERT INTO deleted_claims (claim_id, item_id, claimed_by, claim_date, status, approved_by, loss_location, loss_date, deleted_at) VALUES
(5, 1, 3, '2025-05-05', 'Pending', NULL, 'Ground', '2025-04-18', CURRENT_TIMESTAMP); -- Charlie claimed Alice's wallet

-- Sample admin actions for testing
INSERT INTO admin_actions (admin_id, action_type, action_description) VALUES
(1, 'Create', 'Created new user: Alice Smith'),
(2, 'Update', 'Updated claim status for item ID 1'),
(3, 'Delete', 'Deleted item ID 10 from records');

-- Verify data
SELECT * FROM admins;
SELECT * FROM users;
SELECT * FROM claims;
SELECT * FROM items;
SELECT * FROM locations;
SELECT * FROM deleted_items;
SELECT * FROM deleted_claims;
SELECT * FROM deleted_users;
SELECT * FROM admin_actions;
