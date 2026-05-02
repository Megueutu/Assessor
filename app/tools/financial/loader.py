from json import loads

with open("app/tools/financial/aliases/category.json", "r") as json:
    CATEGORY_ALIASES = loads(json.read())

with open("app/tools/financial/aliases/type.json", "r") as json:
    PAYMENT_TYPES_ALIASES = loads(json.read())