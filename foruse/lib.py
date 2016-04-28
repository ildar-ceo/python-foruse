# -*- coding: utf-8 -*- 

import string, random

def var_dump_output(var, level, space, crl, outSpaceFirst=True, outLastCrl=True):
	res = ''
	if outSpaceFirst: res = res + space * level
	
	typ = type(var)
	
	if typ in [list]:
		res = res + "[" + crl
		for i in var:
			res = res + var_dump_output(i, level + 1, space, crl, True, False) + ',' + crl
		res = res + space * level + "]" 
		
	elif typ in [dict]:
		res = res + "{" + crl 
		for i in var:
			res = res + space * (level+1) + i + ": " + var_dump_output(var[i], level + 1, space, crl, False, False)  + ',' + crl
		res = res + space * level  + "}"
	
	elif typ in [str]:
		res = res + "'"+str(var)+"'"
	
	elif typ in [NoneType]:
		res = res + "None"
	
	elif typ in (int, float, bool):
		res = res + typ.__name__ + "("+str(var)+")"
		
	elif isinstance(typ, object):
		res = res + typ.__name__ + "("+str(var)+")"
		
	if outLastCrl == True:
		res = res + crl
		
	return res
	
def var_dump(*obs):
	"""
	  shows structured information of a object, list, tuple etc
	"""
	i = 0
	for x in obs:
		
		str = var_dump_output(x, 0, '  ', '\n', True)
		print (str.strip())
		
		#dump(x, 0, i, '', object)
		i += 1

def gen_random_string(size=6, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


# from http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
	"""Ask a yes/no question via input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".
	"""
	valid = {"yes": True, "y": True, "ye": True,
			 "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' "
							 "(or 'y' or 'n').\n")