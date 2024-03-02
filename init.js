const optionsSchema = {
    bsonType: "object",
    required: ["type", "choices"],
    additionalProperties: false,
    properties: {
        type: {
            enum: ["radio", "checkbox"]
        },
        choices: {
            bsonType: "object",
            minProperties: 1,
            additionalProperties: {
                bsonType: "decimal"
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
            bsonType: "decimal"
        },
        choices: {
            bsonType: "array",
            items: {
                bsonType: "array",
                items: {
                    bsonType: "string"
                }
            }
        }
    }
};

db.createCollection("MenuItems", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "MenuItem Object Validation",
            required: ["_id", "menuName", "itemName", "kitchenName", "price", "options", "available"],
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
                    bsonType: "decimal"
                },
                options: {
                    bsonType: "array",
                    items: optionsSchema
                },
                available: {
                    bsonType: "bool"
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
                            bsonType: "decimal"
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
                    bsonType: "object",
                    minProperties: 1,
                    additionalProperties: {
                        enum: ["ordered", "ready", "fulfilled"]
                    }
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
        price: Decimal128("4.95"),
        options: [
            {
                type: "checkbox",
                choices: {
                    "Ketchup": Decimal128("0"),
                    "Mustard": Decimal128("0"),
                    "Relish": Decimal128("0")
                }
            }
        ],
        available: true
    },
    {
        menuName: "Food Items",
        itemName: "Bagel",
        kitchenName: "Example Kitchen",
        price: Decimal128("2.50"),
        options: [
            {
                type: "radio",
                choices: {
                    "No Cream cheese": Decimal128("0"),
                    "Cream cheese": Decimal128("0"),
                    "Extra Cream cheese": Decimal128("0")
                }
            }
        ],
        available: true
    },
    {
        menuName: "Food Items",
        itemName: "Bacon and Eggs",
        kitchenName: "Example Kitchen",
        price: Decimal128("4.55"),
        options: [
            {
                type: "radio",
                choices: {
                    "Fried": Decimal128("0"),
                    "Scrambled": Decimal128("0")
                }
            }
        ],
        available: false
    },
    {
        menuName: "Food Items",
        itemName: "Hamburger",
        kitchenName: "Example Kitchen",
        price: Decimal128("5.05"),
        options: [
            {
                type: "radio",
                choices: {
                    "Rare": Decimal128("0"),
                    "Medium-Rare": Decimal128("0"),
                    "Medium": Decimal128("0"),
                    "Well Done": Decimal128("0")
                }
            },
            {
                type: "checkbox",
                choices: {
                    "Lettuce": Decimal128("0"),
                    "Tomato": Decimal128("0"),
                    "Bacon": Decimal128("0.49"),
                    "Onion": Decimal128("0.19"),
                    "Ketchup": Decimal128("0"),
                    "Mustard": Decimal128("0")
                }
            }
        ],
        available: true
    },
    {
        menuName: "Food Items",
        itemName: "Muffin",
        kitchenName: "Example Kitchen",
        price: Decimal128("2.99"),
        options: [
            {
                type: "radio",
                choices: {
                    "Chocolate Chip": Decimal128("0"),
                    "Blueberry": Decimal128("0")
                }
            }
        ],
        available: true
    },
    {
        menuName: "Drink Items",
        itemName: "Coffee",
        kitchenName: "Example Kitchen",
        price: Decimal128("2.99"),
        options: [],
        available: true
    },
    {
        menuName: "Drink Items",
        itemName: "Bottled Water",
        kitchenName: "Example Kitchen",
        price: Decimal128("1.50"),
        options: [],
        available: true
    },
    {
        menuName: "Drink Items",
        itemName: "Soft Drink",
        kitchenName: "Example Kitchen",
        price: Decimal128("1.99"),
        options: [],
        available: true
    }
]);

print("Inserting user document");
var userInsertRes = db.Users.insertOne(
    {
        username: "user1",
        balance: Decimal128("123.45")
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
                price: Decimal128("1.99"),
                choices: []
            },
            {
                menuName: "Food Items",
                itemName: "Hamburger",
                kitchenName: "Example Kitchen",
                price: Decimal128("5.54"),
                choices: [["Medium"], ["Lettuce", "Bacon"]]
            }
        ],
        status: {"Example Kitchen": "ordered"}
    }
);


print(db.getMongo().getDBNames());
print(db.getName());
