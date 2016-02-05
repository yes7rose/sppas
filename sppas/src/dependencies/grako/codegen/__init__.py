# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from dependencies.grako.exceptions import CodegenError
from dependencies.grako.codegen.cgbase import *  # noqa
from dependencies.grako.codegen import python


pythoncg = python.codegen


def codegen(model, target='python'):
    if target.lower() == 'python':
        return pythoncg(model)
    else:
        raise CodegenError('Unknown target language: %s' % target)
