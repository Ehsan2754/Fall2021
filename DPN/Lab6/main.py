import sys
def eval_args(args):
    flag=(len(args)==3)
    for item in args:
        flag=flag and item.isnumeric()
    flag = flag and ((int(args[2])-int(args[1])+1)==int(args[0]))
    if(flag):
        return args
    else: raise ValueError
if __name__=="__main__":
    print(eval_args(sys.argv[1:]))
