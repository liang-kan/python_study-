import jpype
import jpype.imports
from jpype.types import *


def main():
    # 1. 启动 JVM
    # jpype.getDefaultJVMPath() 会自动找到你安装的 JDK
    if not jpype.isJVMStarted():
        print("Starting JVM...")
        jpype.startJVM(classpath=['.'])  # classpath 设置为当前目录

    # 2. 使用 Java 标准库
    # 直接 import java.util 包
    from java.util import ArrayList, HashMap

    # 3. 像写 Java 一样写 Python
    # New 一个 ArrayList
    java_list = ArrayList()
    java_list.add("Python")
    java_list.add("Java")
    java_list.add("Bridge")

    print(f"Java List Size: {java_list.size()}")
    print(f"Java List Get: {java_list.get(1)}")

    # New 一个 HashMap
    java_map = HashMap()
    java_map.put("key1", "value1")

    # 4. 甚至可以打印 System.out
    from java.lang import System
    System.out.println("Hello from Java System.out via Python!")

    # 5. 关闭 JVM
    jpype.shutdownJVM()


if __name__ == "__main__":
    main()