# -*- coding: utf-8 -*- 


def colorf(str, *args, **kwargs):
	color = None
	is_bold = False
	for x in args:
		if x in ['black', 'red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'white']:
			color = x
		if x == 'bold':
			is_bold = True
	
	if color is None:
		for x in args:
			if x in COLORS:
				color = x
	else:
		if is_bold:
			color = "b_" + color
	
	c = COLORS.get(color)
	if c is not None:
		return c + str + COLORS['nc']
	return str

	
# Цвета
COLORS={
	"black": '\033[0;30m',
	"red": '\033[0;31m',
	"green": '\033[0;32m',
	"yellow": '\033[0;33m',
	"blue": '\033[0;34m',
	"purple": '\033[0;35m',
	"cyan": '\033[0;36m',
	"white": '\033[0;37m',
	
	"b_black": '\033[1;30m',
	"b_red": '\033[1;31m',
	"b_green": '\033[1;32m',
	"b_yellow": '\033[1;33m',
	"b_blue": '\033[1;34m',
	"b_purple": '\033[1;35m',
	"b_cyan": '\033[1;36m',
	"b_white": '\033[1;37m',
	
	#"nc": '\e[0m',
	"nc": '\033[0m',
}





