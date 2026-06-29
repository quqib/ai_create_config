def a(b=10):
    # 1. 增加终止条件：当 b 小于等于 1 时，停止递归
    if b <= 1:
        return

    for i in range(1, b):
        print("lll")
        if i == 1:
            print("gggg")
        else:
            # 2. 将 b 减 1 后的结果作为参数传递给下一次递归
            a(b - 1)




# ctrl+shift+e的演示
c = 10
print(c)
b = 20
print(b)


