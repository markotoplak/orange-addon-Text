from distutils.core import setup
from distutils.core import Extension
import distutils.ccompiler

#if distutils.ccompiler.get_default_compiler() in ['unix', 'mingw32']:
extra_compile_args=[
        '-fno-strict-aliasing',
        '-Wall',
        '-Wno-sign-compare',
        '-Woverloaded-virtual'
        ]
#else:
#    extra_compile_args=[]

setup(name = "orngText",
      version = "0.1.0",
      description = "Text preprocessing utilities for Orange",
      packages = [ 'language_data', 'widgets' ],
      package_data = {'language_data':
                      ['*.bin',
                       '*.fsa',
                       '*.txt']},

      py_modules = [ 'orngText', 'orngTextWrapper' ],
      extra_path = "orngText",
      ext_modules = [
          Extension(
              '_orngTextWrapper',
              sources=[
                  'orngTextWrapper/Wrapper_wrap.cxx',
                  'orngTextWrapper/Wrapper.cpp',
                  'tmt/common/Common.cpp',
                  'tmt/common/Files.cpp',
                  'tmt/lemmatization/FSADictionary.cpp',
                  'tmt/lemmatization/FSALemmatization.cpp',
                  'tmt/lemmatization/Lemmatization.cpp',
                  'tmt/lemmatization/PorterStemmer.cpp',
                  'tmt/strings/StringUtils.cpp',
                  'tmt/strings/UTF8Tokenizer.cpp',
                  'lemmagen/RdrLemmatizer.cpp'
                  ],
              extra_compile_args=extra_compile_args,
              include_dirs=['.'],
              define_macros=[('TMTNOZLIB','1'), ('NDEBUG', '1')],
              language='c++')
          ]
      )
