import distutils
import distutils.sysconfig
import sys
import orngRegistry

orngRegistry.addWidgetCategory("Text Mining", distutils.sysconfig.get_python_lib() + r"\orngText\widgets", "remove" not in sys.argv[1])
