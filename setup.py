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

modules = [
        Extension(
                '_orngTextWrapper',
                sources=[
                                'source/orngTextWrapper/Wrapper_wrap.cxx',
                                'source/orngTextWrapper/Wrapper.cpp',
                                'source/tmt/common/Common.cpp',
                                'source/tmt/common/Files.cpp',
                                'source/tmt/lemmatization/FSADictionary.cpp',
                                'source/tmt/lemmatization/FSALemmatization.cpp',
                                'source/tmt/lemmatization/Lemmatization.cpp',
                                'source/tmt/lemmatization/PorterStemmer.cpp',
                                'source/tmt/strings/StringUtils.cpp',
                                'source/tmt/strings/UTF8Tokenizer.cpp',
                                'source/lemmagen/RdrLemmatizer.cpp'
                ],
                extra_compile_args=extra_compile_args,
                include_dirs=['.', 'source'],
                define_macros=[('TMTNOZLIB','1'), ('NDEBUG', '1')],
                language='c++'
        )
]
destDir="orange/add-ons/Text"

# list all language files that need to be included
#lngFiles = glob.glob('language_data/*.bin') + glob.glob('language_data/*.fsa') + glob.glob('language_data/*.txt')
#lngFiles = [f.replace('\\', '/').split('/')[1] for f in lngFiles]
def writeMakeFileDepends():
        f = open("Makefile.depends", "wt")

        includePaths = []
        for ext in modules:
                if ext.include_dirs <> []:
                        for p in ext.include_dirs:
                                includePaths.append( "-I%s" % (p))
        includePaths = " ".join(includePaths)

        if includePaths <> "":
                f.write("COMPILEOPTIONSMODULES = %s\n" % (includePaths))
        f.write("DESTDIR = $(PYTHONSITEPKGS)/%s\n" % (destDir))

        f.write("modules:")
        for ext in modules:
                f.write(" %s.so" % (ext.name))
        f.write("\n")

        for ext in modules:
                objs = []
                for s in ext.sources:
                        if s[-2:] == '.c' or s[-4:] == '.cpp':
                                objfname = os.path.splitext(os.path.join("..", s))[0] + ".o"
                                objs.append( objfname)
                objs = " ".join(objs)
                f.write("%s.so: %s\n" % (ext.name, objs))
                f.write("\t$(LINKER) $(LINKOPTIONS) %s -o %s.so\n" % (objs, os.path.join("..", ext.name)))
                f.write("ifeq ($(OS), Darwin)\n")
                f.write("\tinstall_name_tool -id $(DESTDIR)/%s.so %s.so\n" % (ext.name, os.path.join("..", ext.name)))
                f.write("endif\n")
        f.close()

if __name__ == "__main__":
        setup(name = "Orange Text Mining",
                version = "0.1.0",
                description = "Text Mining Add-On for Orange",
                packages = [ 'widgets', 'doc' ],

                package_data = {'doc': docFiles, 'widgets': ['icons/*.png']},

                py_modules = [ 'orngText', 'orngTextWrapper', 'textConfiguration'],
                extra_path = ("orange-text", destDir),
                ext_modules = modules,
                scripts=["post_install_script.py"]
        )

