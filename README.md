# webargparse

这是一个将argparse的parser转换成web界面的工具, 可以只修改几行代码就将一个普通的命令行脚本变成一个可以分享出去的图形界面.

## 使用方法

1. 编写一个基于argparse的命令行脚本.参考example/demo.py. 脚本的具体编写方法参考demo.py中注释.需要注意的几个地方是:

* 脚本中必须包含一个名为STREAMLIT_PARSER变量, 类型是ArgumentParser, 用于本项目从中提取参数. parser中尽量完善help以使得web界面更容易理解.

  * 跟界面显示有关的参数
    * ArgumentParser:
      * prog: 用于在下拉列表中显示,
      * description: 在右侧展示, 可以写markdown
    * --add-argument:
      * help: 输入框的label, 方便用户知道该输入什么
  * 如果有subparsers, 那么所有的subparser会展开成一个独立的工具. 但不支持多级subparsers.
  * 支持的参数类型和对应的Web组件
    * 普通字符串参数: 对应一个文本输入框.  required=True时不填会报错
    * choices=[]: 配置了选项, 对应单选下拉框, 若指定nargs参数可以是一个多选下拉框.
    * action='store_true', 输出为布尔型, 对应checkbox单选框. store_false暂时未支持, 请用store_true来实现
    * type: type参数是一个函数, 接收字符串转换成期望的类型.
      * type=int, type=float. 对应数字输入框
      * type=open, type=argparse.FileType(mode='r'): 对应一个文件上传控件, args中会自动将文件对象传进去. 不支持输出文件, 输出文件不要用argparse.FileType(model='w')否则web端的行为不一样.
      * type=datetime.date.fromisoformat: 对应日期选择框, 返回的是datetime.date对象, 目前不支持datetime, 因为streamlit中没有同时选择日期和时间的组件
    * nargs: *或+的时候, 若有choices选项则是一个多选框. 否则是一个文本输入框,需要自行用4个空格分隔多个参数. nargs只支持了这两个字符, 其他字符无效.
    * default: 默认值会自动填入输入框
* 脚本中必须包含一个名为STREAMLIT_FUNCTION的函数, 他接收STREAMLIT_PARSER.parse_args()返回的参数, 并对参数进行处理.

  * 函数的stdout和stderr会被捕获输出
  * 函数的返回值会根据类型不同来进行展示:
    * None: 不展示
    * str:
      * 被&lt;markdown>&lt;/markdown>包围, 展示markdown
      * 长度小于1024,直接展示
      * 长度大于1024, 展示文件下载按钮作为文本文件下载
    * bytes: 作为二进制文件下载, 需要自行修改文件后缀
    * 文件对象(有read函数): 读取全文, 展示文件下载按钮作为文件下载.
    * pandas.DataFrame/list: 展示表格, 并提供csv文件下载按钮. 返回DataFrame时可以指定部分样式, 参考df.style.highlight_max(axis=0). 不建议下载很大的表格.
    * dict: 展示json
    * tuple: 返回一个dataframe和一个绘图类型, 将dataframe转换成图表展示. (DataFrame, type)
      * type: line_chart: 折线图, bar_chart: 柱状图, area_chart: 什么鬼, map: 地图打点
      * type=image的时候, 第一个参数是一个BytesIO或str, 当做图标展示
* 脚本中可以包含一个STREAMLIT_DETAIL_FUNCTION, 返回结果如果是表格, 表格中选定一行将执行此函数并将结果展示为详情. 返回结果会直接调用st.write()展示, 可以用markdown, 也可以是json或普通字符串

2. 启动web界面.

* 前置条件, pip install streamlit watchdog streamlit-aggrid
* 直接启动一个工具脚本

```
python3.8 -m webargparse -f example/demo.py
```

* 启动一个Python模块

```
python3.8 -m webargparse -m webargparse.example.demo
```

* 启动一个包含符合条件的子模块的模块.  会检索模块下所有子模块, 如果包含STREAMLIT_PARSER和STERAMLIT_FUNCTION变量则作为一个工具加入.

```
# 如果有多个模块, 可以用逗号分隔
python3.8 -m webargparse -m webargparse.example   # 两个demo都会加入
```

* 修改端口, 默认8503

```
python3.8 -m webargparse -m webargparse.example  --port 8080
```

3. 和后端微服务一起打包

* 可以在微服务的Python包中增加一个tools目录, 包含多个拥有包含STREAMLIT_PARSER和STERAMLIT_FUNCTION变量的脚本. 例如webargparse.tools
* requirements.txt中加入webargparse
* 在k8s deployment中增加一个pod执行 python3.8 -m webargparse -m webargparse.example 并将8503端口暴露出去访问

# Demo

### 输入项组件渲染

左侧的输入组件通过argparser的选项类型来控制.

```python
def getParser():
    # prog: 的内容是页面左侧"功能清单选择"下拉框中显示的内容
    # description: 功能说明, 可以写markdown, 会出现右侧顶部
    parser = ArgumentParser(prog='这是一个demo', description='''
    **这里可以写markdown**
    ''')

    # 选项的help是输入框的label
    parser.add_argument('-i', '--output', help='输入字符串')
    # int和float类型的输入框只能是数字
    parser.add_argument('--integer', dest='integer', help='这是一个数字', type=int)
    parser.add_argument('-s', dest='source', help='这是一个可以输入多值的字符串', nargs='*', default=['a', 'b'])
    # 这是一个单选的下拉列表
    parser.add_argument('--output-type', dest='output_type', help='选择返回结果类型, 测试工具输出结果样式', 
                        choices=['文件', '表格', '短字符串', 'bytes', '字典', '短字符串', '长字符串', 'markdown', '折线图'], default='表格')
    # 这是一个多选框
    parser.add_argument('--multi', dest='multi', help='多选框, 可以选择多个选项', nargs='+' , default=['表格', '文件'],
                        choices=['文件', '表格', '短字符串', 'bytes', '字典', '短字符串', '长字符串', 'markdown', '折线图'])
    # 这是一个必选的字符串, 如果不填会报错
    parser.add_argument('-r', dest='required_str', help='这是一个必选的字符串, 不填会报错', required=True)
    # 上传文件, 上传后的文件会打开并将文件对象传递给 args.file
    parser.add_argument('-f', dest='file', help='上传一个文件, 输出文件前10行', type=argparse.FileType(mode='r', encoding='utf-8'))
    parser.add_argument('--store', action='store_true', dest='store_true', help='单选框')
    parser.add_argument('--date', type=date.fromisoformat, help='选择日期')
    parser.add_argument('--time', type=types.time, help='选择时间, 目前只能分别得到时间后拼接在一起')
    return parser
```

![demo2.jpg](image/README/demo2.jpg)

![demo3.jpg](image/README/demo3.jpg)

### 输出效果

输出效果通过STREAMLIT_FUNCTION的返回值类型来控制

```
def process(args):
    if args.file:
        count = 0
        with args.file:
            for line in args.file:
                print(line)
                count += 1
                if count >= 10:
                    break
    time.sleep(3)
    print(args)
    #return [{'a':1, 'b':3, 'c': 4}, {'a':1, 'b':3, 'd': 4},]
    #return [1,2,3,4]
    if args.output_type == '文件':
        from io import StringIO
        return StringIO('这是一个测试文件')
    elif args.output_type == '表格':
        return [{'a':1, 'b':3, 'c': 4}] * 200
    elif args.output_type == '短字符串':
        return '短字符串'
    elif args.output_type == '折线图':
        return ([{'a':1, 'b':3, 'c': 4}] * 200, 'line_chart')
    elif args.output_type == '长字符串':
        return ''.join(['长字符串'] * 500)
    elif args.output_type == 'markdown':
        return '''<markdown># 一级标题
## 二级标题  
</markdown>'''
    elif args.output_type == 'bytes':
        return b'this is a bytes'
  
    return {'a':1, 'b':3, 'c': 4}
  
# ArgumentParser对象, 必须有此变量
STREAMLIT_PARSER = getParser()


```

![demo4.jpg](image/README/demo4.jpg "必选项")
![demo5.jpg](image/README/demo5.jpg "必选项")
![demo6.jpg](image/README/demo6.jpg "必选项")
![demo7.jpg](image/README/demo7.jpg "必选项")
![demo8.jpg](image/README/demo8.jpg "必选项")


# 已知限制

1. STREAMLIT_FUNCTION必须直接得到输出结果, 不支持再有交互式输入, 如果有可能会导致网页卡住.
2. subparsers最多只能有一组, 不能有多级subparser
3. argparse还有一些高级功能可能没有覆盖到, 比如nargs='?'等
4. 对于字符串类型,空格和None是无法区分的.
5. 只有字符串可以支持nargs='*', 数值只能输入1个, 如果确实需要只能自己转字符串.

# 这里是给不按套路出牌的人准备的

因为STREAMLIT_FUNCTION会被执行, 所以实际上你可以在这个函数中自己绘制网页, 如果你知道怎么使用streamlit的话.这样他就不用局限于根据返回值去渲染执行结果.  而是你可以自己设计最终的网页形态.

需要注意的是, 如果你这么做了, 那他在本地就无法执行了, 只能是一个WEB工具
