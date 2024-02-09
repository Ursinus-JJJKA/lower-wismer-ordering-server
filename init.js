const options_schema = {
    bsonType: "object",
    required: ["type", "choices"],
    additionalProperties: false,
    properties: {
        type: {
            bsonType: "string",
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

const menuitem_schema = {
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
            items: options_schema
        }
    }
};

const orderitem_schema = {
    bsonType: "object",
    required: ["name", "price", "choices"],
    additionalProperties: false,
    properties: {
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
            required: ["_id", "name", "menuitems"],
            additionalProperties: false,
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                name: {
                    bsonType: "string",
                    description: "'name' must be a string and is required"
                },
                menuitems: {
                    bsonType: "array",
                    description: "'menuitems' must be an array and is required",
                    items: menuitem_schema
                }
            }
        }
    }
})

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
                            bsonType: "string",
                            description: "'username' must be a string and is required"
                        },
                        balance: {
                            bsonType: "double",
                            description: "'balance' must be a double and is required"
                        }
                    }
                }
            },
            {
                $expr: {
                    $gte: ["balance", 0]
                }
            }
        ]
    }
})

db.Users.createIndex(
    {
        "username": 1
    },
    {
        unique: true
    }
)

db.createCollection("Orders", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Order Object Validation",
            required: ["_id", "userid", "date", "orderitems"],
            additionalProperties: false,
            properties: {
                _id: {
                    bsonType: "objectId"
                },
                userid: {
                    bsonType: "objectId"
                },
                date: {
                    bsonType: "date",
                    description: "'date' must be a date and is required"
                },
                orderitems: {
                    bsonType: "array",
                    description: "'orderitems' must be an array and is required",
                    items: orderitem_schema
                }
            }
        }
    }
})

db.Menus.insertOne(
    {
        name: "Example Section",
        menuitems: [
            {
                name: "Example Food",
                price: 9.99,
                options: []
            }
        ]
    }
)

var userInsertRes = db.Users.insertOne(
    {
        username: "Example Username",
        balance: 123.45
    }
)

db.Orders.insertOne(
    {
        userid: userInsertRes.insertedId,
        date: new Date(),
        orderitems: [
            {
                name: "Example Food",
                price: 9.99,
                options: []
            }
        ]
    }
)
