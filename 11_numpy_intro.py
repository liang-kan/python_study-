import numpy as np
import time

def main():
    # --- 1. 创建数组 ---
    # Python List: [0, 1, 2, ..., 999999]
    size = 1_000_000
    size = 1_000_000
    py_list = list(range(size))

    # NumPy Array: 内存连续的数组，类似 Java 的 int[] 但功能更强
    np_arr = np.arange(size)

    print(f"Data size: {size}")

    # --- 2. 性能测试：所有元素 * 2 ---

    # Python List 方式 (循环)
    start = time.time()
    py_result = [x * 2 for x in py_list]
    print(f"Python List time: {time.time() - start:.4f} seconds")

    # NumPy 方式 (向量化运算 - Vectorization)
    # 这一行代码会在 C 语言层面并行执行，极快
    start = time.time()
    np_result = np_arr * 2
    print(f"NumPy Array time: {time.time() - start:.4f} seconds")

    # --- 3. 矩阵操作 (机器学习的基础) ---
    # 创建一个 3行 4列 的矩阵 (二维数组)
    matrix = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ])

    print("\nOriginal Matrix (3x4):")
    print(matrix)

    # 矩阵转置 (Transpose) -> 4x3
    print("\nTransposed (4x3):")
    print(matrix.T)

    # 统计计算
    print(f"\nMean value: {matrix.mean()}")  # 平均值
    print(f"Sum of each column: {matrix.sum(axis=0)}")  # 按列求和


if __name__ == "__main__":
    main()