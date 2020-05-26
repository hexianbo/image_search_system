

def classification(imgname):
    x = imgname[-2]
    if x == '任意表情包':
        return 1
    elif x == '小人':
        return 2
    elif x == '小黄脸':
        return 3
    elif x == '小黄鸡':
        return 4
    elif x == '熊猫头':
        return 5
    elif x == '猫和老鼠':
        return 6
    else:
        return 0

def str_map(n):
    if n == 0:
        return ''
    elif n == 1:
        return '任意表情包'
    elif n == 2:
        return '小人'
    elif n == 3:
        return '小黄脸'
    elif n == 4:
        return '小黄鸡'
    elif n == 5:
        return '熊猫头'
    elif n == 6:
        return '猫和老鼠'