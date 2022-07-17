def decorate(tag_name):

    def p_decorate(func):

        def func_wrapper(*args, **kwargs):
            return "<{1}>{0}</{1}>".format(func(*args, **kwargs), tag_name)

        return func_wrapper

    return p_decorate

@decorate("tag")
@decorate("p")
@decorate("b")
def get_text(text):
    return text

if __name__=='__main__':
    print(get_text('some_test'))