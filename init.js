const optionsSchema = {
    bsonType: "object",
    required: ["type", "choices"],
    additionalProperties: false,
    properties: {
        type: {
            enum: ["radio", "checkbox"]
        },
        choices: {
            bsonType: "array",
            minItems: 1,
            items: {
                bsonType: "string"
            }
        }
    }
};

const orderItemSchema = {
    bsonType: "object",
    required: ["menuName", "itemName", "kitchenName", "price", "choices"],
    additionalProperties: false,
    properties: {
        menuName: {
            bsonType: "string"
        },
        itemName: {
            bsonType: "string"
        },
        kitchenName: {
            bsonType: "string"
        },
        price: {
            bsonType: "double"
        },
        choices: {
            bsonType: "array",
            items: {
                bsonType: "string"
            }
        }
    }
};

db.createCollection("MenuItems", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "MenuItem Object Validation",
            required: ["_id", "menuName", "itemName", "kitchenName", "price", "options"],
            additionalProperties: false,
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                menuName: {
                    bsonType: "string"
                },
                itemName: {
                    bsonType: "string"
                },
                kitchenName: {
                    bsonType: "string"
                },
                price: {
                    bsonType: "double"
                },
                options: {
                    bsonType: "array",
                    items: optionsSchema
                }
            }
        }
    }
});

db.MenuItems.createIndex(
    {
        "menuName": 1,
        "itemName": 1
    },
    {
        unique: true
    }
);

db.createCollection("Users", {
    validator: {
        $and: [
            {
                $jsonSchema: {
                    bsonType: "object",
                    title: "User Object Validation",
                    required: ["_id", "username", "balance"],
                    additionalProperties: false,
                    properties: {
                        _id: {
                            bsonType: "objectId"
                        },
                        username: {
                            bsonType: "string"
                        },
                        balance: {
                            bsonType: "double"
                        }
                    }
                }
            },
            {
                $expr: {
                    $gte: ["$balance", 0]
                }
            }
        ]
    }
});

db.Users.createIndex(
    {
        "username": 1
    },
    {
        unique: true
    }
);

db.createCollection("Orders", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Order Object Validation",
            required: ["_id", "userId", "dateOrdered", "orderItems", "status"],
            additionalProperties: false,
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                userId: {
                    bsonType: "objectId"
                },
                dateOrdered: {
                    bsonType: "date"
                },
                orderItems: {
                    bsonType: "array",
                    items: orderItemSchema
                },
                status: {
                    enum: ["ordered", "ready", "fulfilled"]
                }
            }
        }
    }
});

print("Inserting menuitem documents");
db.MenuItems.insertMany([
    {
        menuName: "Food Items",
        itemName: "Hotdog",
        kitchenName: "Example Kitchen",
        price: 4.95,
        options: [
            {
                type: "checkbox",
                choices: ["Ketchup", "Mustard", "Relish"]
            }
        ]
    },
    {
        menuName: "Food Items",
        itemName: "Bagel",
        kitchenName: "Example Kitchen",
        price: 2.50,
        options: [
            {
                type: "radio",
                choices: ["No Cream cheese", "Cream cheese", "Extra Cream cheese"]
            }
        ]
    },
    {
        menuName: "Food Items",
        itemName: "Bacon and Eggs",
        kitchenName: "Example Kitchen",
        price: 4.55,
        options: [
            {
                type: "radio",
                choices: ["Fried", "Scrambled"]
            }
        ]
    },
    {
        menuName: "Food Items",
        itemName: "Hamburger",
        kitchenName: "Example Kitchen",
        price: 5.05,
        options: [
            {
                type: "radio",
                choices: ["Rare", "Medium-Rare", "Medium", "Well Done"]
            },
            {
                type: "checkbox",
                choices: ["Lettuce", "Tomato", "Bacon", "Onion", "Ketchup", "Mustard"]
            }
        ]
    },
    {
        menuName: "Food Items",
        itemName: "Muffin",
        kitchenName: "Example Kitchen",
        price: 2.99,
        options: [
            {
                type: "radio",
                choices: ["Chocolate Chip", "Blueberry"]
            }
        ]
    },
    {
        menuName: "Drink Items",
        itemName: "Coffee",
        kitchenName: "Example Kitchen",
        price: 2.99,
        options: []
    },
    {
        menuName: "Drink Items",
        itemName: "Bottled Water",
        kitchenName: "Example Kitchen",
        price: 1.50,
        options: []
    },
    {
        menuName: "Drink Items",
        itemName: "Soft Drink",
        kitchenName: "Example Kitchen",
        price: 1.99,
        options: []
    }
]);

print("Inserting user document");
var userInsertRes = db.Users.insertOne(
    {
        username: "user1",
        balance: 123.45
    }
);

print("Inserting order document");
db.Orders.insertOne(
    {
        userId: userInsertRes.insertedId,
        dateOrdered: new Date(),
        orderItems: [
            {
                menuName: "Drink Items",
                itemName: "Soft Drink",
                kitchenName: "Example Kitchen",
                price: 1.99,
                choices: []
            },
            {
                menuName: "Food Items",
                itemName: "Hamburger",
                kitchenName: "Example Kitchen",
                price: 5.05,
                choices: ["Medium", "Lettuce", "Bacon"]
            }
        ],
        status: "ordered"
    }
);

print(db.getMongo().getDBNames());
print(db.getName());
