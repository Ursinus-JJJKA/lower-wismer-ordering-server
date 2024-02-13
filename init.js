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

const menuItemSchema = {
    bsonType: "object",
    required: ["name", "price", "options"],
    additionalProperties: false,
    properties: {
        name: {
            bsonType: "string",
        },
        price: {
            bsonType: "double"
        },
        options: {
            bsonType: "array",
            items: optionsSchema
        }
    }
};

const orderItemSchema = {
    bsonType: "object",
    required: ["kitchenName", "name", "price", "choices"],
    additionalProperties: false,
    properties: {
        kitchenName: {
            bsonType: "string"
        },
        name: {
            bsonType: "string",
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

db.createCollection("Menus", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Menu Object Validation",
            required: ["_id", "menuName", "kitchenName", "menuItems"],
            additionalProperties: false,
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                menuName: {
                    bsonType: "string"
                },
                kitchenName: {
                    bsonType: "string"
                },
                menuItems: {
                    bsonType: "array",
                    items: menuItemSchema
                }
            }
        }
    }
});

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
                    bsonType: ["string", "date"]
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

console.log("Inserting menu document");
db.Menus.insertOne(
    {
        menuName: "Example Section",
        kitchenName: "Example Kitchen",
        menuItems: [
            {
                name: "Example Food",
                price: 9.99,
                options: []
            }
        ]
    }
);

console.log("Inserting user document");
var userInsertRes = db.Users.insertOne(
    {
        username: "Example Username",
        balance: 123.45
    }
);

console.log("Inserting order document");
db.Orders.insertOne(
    {
        userId: userInsertRes.insertedId,
        dateOrdered: new Date(),
        orderItems: [
            {
                kitchenName: "Example Kitchen",
                name: "Example Food",
                price: 9.99,
                choices: []
            }
        ],
        status: "ordered"
    }
);
