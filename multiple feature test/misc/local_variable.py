if False:
    print('test')
else:
    if True:
        if False:
            print('test')
        else:
            try:
                prompt_name = 'very_secret_name'
            except Exception:
                prompt_name = 'very_secret_name'
    else:
        prompt_name = 'other'
    if True:
        if False:
            print('test')
        else:
            def test():
                print(prompt_name)

            test()
