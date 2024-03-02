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
                bsonType: "object",
                required: ["name", "price"],
                additionalProperties: false,
                properties: {
                    name: {
                        bsonType: "string"
                    },
                    price: {
                        bsonType: "double"
                    }
                }
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
                    bsonType: "object"
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
                choices: [
                    {name: "Ketchup", price: 0},
                    {name: "Mustard", price: 0},
                    {name: "Relish", price: 0}
                ]
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
                choices: [
                    {name: "No Cream cheese", price: 0},
                    {name: "Cream cheese", price: 0},
                    {name: "Extra Cream cheese", price: 0}
                ]
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
                choices: [
                    {name: "Fried", price: 0},
                    {name: "Scrambled", price: 0}
                ]
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
                choices: [
                    {name: "Rare", price: 0},
                    {name: "Medium-Rare", price: 0},
                    {name: "Medium", price: 0},
                    {name: "Well Done", price: 0}
                ]
            },
            {
                type: "checkbox",
                choices: [
                    {name: "Lettuce", price: 0},
                    {name: "Tomato", price: 0},
                    {name: "Bacon", price: 0.49},
                    {name: "Onion", price: 0.19},
                    {name: "Ketchup", price: 0},
                    {name: "Mustard", price: 0}
                ]
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
                choices: [
                    {name: "Chocolate Chip", price: 0},
                    {name: "Blueberry", price: 0}
                ]
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
                price: 5.54,
                choices: ["Medium", "Lettuce", "Bacon"]
            }
        ],
        status: {"Example Kitchen": "ordered"}
    }
);

print(db.getMongo().getDBNames());
print(db.getName());
