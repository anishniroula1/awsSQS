class MyClass:
    def __init__(self, value: str = None):
        self.value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


my_object = MyClass()


def modify_object(new_value):
    x = {"value": new_value}
    my_object = MyClass(x)
    print(my_object.get_value())


modify_object("Hello, World!")

# print(my_object.get_value())
