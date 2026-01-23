# class User: 默认继承 object
class User:
    # 构造函数
    # self 相当于 Java 的 this，但在 Python 中必须作为第一个参数显式写出来
    def __init__(self, name, age):
        self.name = name  # public 属性
        self._age = age  # 单下划线开头：约定俗成的 protected/private (其实外部也能访问)

    # 实例方法
    def say_hello(self):
        print(f"User {self.name} says hello!")

    # toString() 方法
    def __str__(self):
        return f"[User: name={self.name}, age={self._age}]"


# 继承
# class Admin extends User
class Admin(User):
    def __init__(self, name, age, level):
        # super(name, age)
        super().__init__(name, age)
        self.level = level

    # 重写方法 (@Override)
    def say_hello(self):
        print(f"Admin {self.name} (Level {self.level}) commands hello!")


def main():
    u = User("Alice", 20)
    a = Admin("Bob", 30, "Root")

    u.say_hello()
    a.say_hello()

    # 打印对象，自动调用 __str__
    print(u)


if __name__ == "__main__":
    main()