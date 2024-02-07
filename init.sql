CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    username TEXT UNIQUE NOT NULL,
    mealswipes INTEGER,
    diningdollars REAL,
    bearbucks REAL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Concepts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE FoodOrders (
    id SERIAL PRIMARY KEY,
    userid INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(userid) REFERENCES Users(id)
);

CREATE TABLE Items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    conceptid INTEGER,
    hidden BOOLEAN DEFAULT FALSE NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conceptid) REFERENCES Concepts(id)
);


CREATE TABLE FoodOrderItems (
    id SERIAL PRIMARY KEY,
    orderid INTEGER,
    itemid INTEGER,
    FOREIGN KEY(orderid) REFERENCES FoodOrders(id),
    FOREIGN KEY(itemid) REFERENCES Items(id)
);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_modified AFTER UPDATE ON Users FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_foodorders_modified AFTER UPDATE ON FoodOrders FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_items_modified AFTER UPDATE ON Items FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
