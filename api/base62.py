import string
import time
import random


# https://gist.github.com/toddlerya/e134007fada31377659a9281e21767fc
class Base62(object):
    """
    基于abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789共计62个ascii字符
    构建62进制编码, 实现正整型十进制数据字符编码和解码
    """

    def __init__(self):
        self.BASE_STR = string.ascii_letters + string.digits
        self.BASE = len(self.BASE_STR)

    def __10to62(self, digit, value=None):
        # 小心value参数的默认传参数陷阱
        # 不应写为value=[], 这将导致只有一次初始化, 每次调用列表的值都会累加
        # 应该声明为None, 只有为None才进行初始化, 这样能保持每次调用都会初始化此参数
        # https://pythonguidecn.readthedocs.io/zh/latest/writing/gotchas.html
        if value is None:
            value = list()
        rem = int(digit % self.BASE)
        value.append(self.BASE_STR[rem])
        div = int(digit / self.BASE)
        if div > 0:
            value = self.__10to62(div, value)
        return value

    def __62to10(self, str_value):
        value_list = list(str_value)
        value_list.reverse()
        temp_list = [
            self.BASE_STR.index(ele) * (self.BASE**n)
            for n, ele in enumerate(value_list)
        ]
        return sum(temp_list)

    def encode_10to62(self, digit: int) -> str:
        """
        10进制转为62进制
        """
        if not isinstance(digit, int) or digit < 0:
            raise TypeError("请输入正整数")
        value = self.__10to62(digit)
        value.reverse()
        value = "".join(value)
        return value

    def decode_62to10(self, str62: str) -> int:
        """
        62进制转为10进制
        """
        check = sum([1 for ele in str62 if ele not in self.BASE_STR])
        if check > 0 or len(str62) == 0 or not isinstance(str62, str):
            raise TypeError("请输入正确的62进制数")
        return self.__62to10(str62)


def genCode():
    return Base62().encode_10to62(int(time.time()) + random.randint(0, 100000000))


# if __name__ == "__main__":
#     print(genCode())
