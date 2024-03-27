"""  add a way to select the number of bits """

""" add restore / clear functions that only effect the selected bits. """

""" add sort options for all options. """

def sort_list(unsorted:list[str], idx:int, reverse:float=False):
	key = lambda a:a[idx]
	unsorted.sort(key=key, reverse=reverse)

""" add password hide button???? """

""" use random.getrandbits(8)???? """


