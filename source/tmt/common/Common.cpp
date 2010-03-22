#include "tmt/common/Common.h"
#include "tmt/strings/StringUtils.h"

#include <cerrno>
#include <cstdarg>
#include <string>
#include <cstring>
#include <iostream>

#if HAS_BOOST
#include "boost/thread/mutex.hpp"

boost::mutex io_mutex;
#endif

using namespace std;
using namespace TMT;

int TMT::TMTVerbosity = 0;
int TMT::TMTNThreads = 1;

StdError::StdError() :
	std::runtime_error(strerror(errno)),
	error(errno)
{
}

StdError::StdError(int error_) :
	std::runtime_error(strerror(error_)),
	error(error_)
{
}

StdError::~StdError() throw()
{
}

void TMT::InitTMT() {
	InitStringUtils();
}

void TMT::TMTFatal1(const char *message)
{
	throw runtime_error(message);
}

void TMT::TMTFatal2(const char *string1, const char *string2)
{
	throw runtime_error(string1 + string(string2));
}

void TMT::TMTFatal2(const char *string1, const string &string2)
{
	throw runtime_error(string1 + string2);
}

void TMT::TMTLog(const char *string1, const char *format, ...)
{
	CHECK(format);
#if HAS_BOOST_
	boost::mutex::scoped_lock lock(io_mutex);
#endif
	cerr << flush;
	va_list l;
	va_start(l, format);
	vfprintf(stderr, format, l);
	fputc('\n', stderr);
	va_end(l);
	fflush(stderr);
}

#if __BORLANDC__ || __TURBOC__
#include <cfloat>

extern "C" {
int isnan(double a)
{
	return _isnan(a);
}
}
#endif
