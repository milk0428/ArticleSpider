import hashlib

#对输入的url生产md5
def get_md5(url):
    #判断如果是unicode类型的话就转换成utf-8（因为py3默认是采用unicode编码）
    if isinstance(url,str):
        url=url.encode("utf-8")
    m=hashlib.md5()
    m.update(url)
    return m.hexdigest()

#测试get_md5函数
if __name__=="__main__":
    print(get_md5("http://jobbole.com"))