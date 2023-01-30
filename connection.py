from mongoengine import connect


connect(
    host="mongodb+srv://vasyliy:12345654321@cluster0.ay09rh2.mongodb.net/?retryWrites=true&w=majority",
    ssl=True,
)
