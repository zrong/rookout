#!/usr/bin/env python3

import os
import shutil

def sub(afile, bfile):
	with open(afile, mode='r', encoding='utf-8') as f:
		txt = f.read()
	txt = txt.replace('_static/', 'static/')
	with open(bfile, mode='w', encoding='utf-8') as f:
		f.write(txt)
		print('Write %s to %s.'%(afile, bfile))

html = 'build/html/'
_static = html+'_static/'
static = 'static/'

if os.path.exists(static):
	shutil.rmtree(static)

shutil.copytree(_static, static)

for f in os.listdir(html):
	if f.endswith('.html'):
		sub(os.path.join(html, f), f)

for f in os.listdir(_static):
	if f.endswith('.js'):
		sub(os.path.join(_static, f), static+f)
