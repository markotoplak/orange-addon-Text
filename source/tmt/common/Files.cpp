#include "tmt/common/Files.h"
#include "tmt/strings/StringUtils.h"

#include <cerrno>
#include <cstring>

#if HAS_BOOST
#include <boost/filesystem/path.hpp>
#include <boost/filesystem/operations.hpp>
#endif

using namespace std;

FILE *TMT::tmtfopen(const char *path, const char *mode)
{
	errno = 0;
	FILE *fp = fopen(path, mode);
	if (!fp)
#if HAS_BOOST
		throw runtime_error(StringPrintf(
			"Error while opening '%s': %s.",
			boost::filesystem::system_complete(path).string().c_str(), strerror(errno)).c_str());
#else
		throw runtime_error(StringPrintf(
			"Error while opening '%s': %s.",
			path, strerror(errno)).c_str());
#endif

	return fp;
}
