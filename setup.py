from distutils.core import setup
from distutils.core import Extension
import distutils.ccompiler
import os, glob

#if distutils.ccompiler.get_default_compiler() in ['unix', 'mingw32']:
extra_compile_args=[
        '-fno-strict-aliasing',
        '-Wall',
        '-Wno-sign-compare',
        '-Woverloaded-virtual'
        ]
#else:
#    extra_compile_args=[]

# list all documentation files that need to be included
docFiles = []
for (dirp, dirns, n) in os.walk('doc'):
	nr = [n1.replace('\\', '/') for n1 in n]
	dirn = dirp.replace('\\', '/')[4:]
	if len(dirn):
		dirn = dirn + '/'
	docFiles.extend( [dirn + n1r for n1r in nr if '.svn' not in dirp + '/' + n1r] )

# list all language files that need to be included
#lngFiles = glob.glob('language_data/*.bin') + glob.glob('language_data/*.fsa') + glob.glob('language_data/*.txt')
#lngFiles = [f.replace('\\', '/').split('/')[1] for f in lngFiles]

setup(name = "orngText",
      version = "0.1.0",
      description = "Text preprocessing utilities for Orange",
      packages = [ 'widgets', 'language_data', 'doc' ],

      package_data = {'language_data': ['*.bin', '*.fsa', '*.txt'], 'doc': docFiles, 'widgets': ['icons/*.png']},

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
          ],
      scripts=["post_install_script.py"]
      )
