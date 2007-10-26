from distutils.core import setup
from distutils.core import Extension
import distutils.ccompiler

if distutils.ccompiler.get_default_compiler() in ['unix', 'mingw32']:
    extra_compile_args=[
        '-fno-strict-aliasing',
        '-Wall',
        '-Wno-sign-compare',
        '-Woverloaded-virtual'
        ]
else:
    extra_compile_args=[]

setup(name = "Orange Text Setup",
      version = "0.1.0",
      description = "Text preprocessing utilities for Orange",
      packages = ['orngText'],
      options={'build_ext':{'swig_opts':'-c++'}},
      ext_modules = [
          Extension(
              '_tmt',
              sources=[
                  'orange/TMTOrange.i',
                  'orange/TMTOrange.cpp',
                  'tmt/common/Common.cpp',
                  'tmt/common/Files.cpp',
                  'tmt/lemmatization/FSADictionary.cpp',
                  'tmt/lemmatization/FSALemmatization.cpp',
                  'tmt/lemmatization/Lemmatization.cpp',
                  'tmt/lemmatization/PorterStemmer.cpp',
                  'tmt/strings/StringUtils.cpp',
                  'tmt/strings/UTF8Tokenizer.cpp'
                  ],
              extra_compile_args=extra_compile_args,
              include_dirs=['.'],
              define_macros=[('TMTNOZLIB','1'), ('NDEBUG', '1')],
              swig_opts=['-c++'],
              language='c++')
          ]
      )
