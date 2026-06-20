from json import loads

with open("app/tools/financial/aliases/category.json", "r", encoding="utf-8") as json:
    CATEGORY_ALIASES = loads(json.read())

with open("app/tools/financial/aliases/payment_method.json", "r", encoding="utf-8") as json:
    PAYMENT_METHOD_ALIASES = loads(json.read())