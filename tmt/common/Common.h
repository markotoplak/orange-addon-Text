#ifndef TMT__COMMON__COMMON_H
#define TMT__COMMON__COMMON_H

#include <string>
#include <vector>
#include <stdexcept>

/// TMT initialization and error handling.
/*! \file Common.h
	Remember to call TMT::InitTMT before using any class or function in TMT namespace.
	You can make various checks at runtime by using TMT::CHECK and TMT::DCHECK.
*/

/// Namespace containing all TMT functions.
/** \namespace TMT
*/
namespace TMT
{

using std::string;
using std::vector;

/// All languages used in TMT
/** \enum Language
*/
enum Language
{
	LanguageUnknown = -1,
	LanguageCroatian = 0,
	LanguageEnglish = 1
};

/// A class representing standard library error exception
/**
	Use this class to catch standard library errors.

	Example:
	\code
FILE *fp = fopen(file, "rb");
if (!fp)
	throw StdError();
	\endcode
*/
class StdError : public std::runtime_error
{
	int error;

public:
	/// Create new standard library error exception using errno as error number.
	StdError();

	/// Create new standard library error exception
	/** \param error is error index as specified in errno.h
	*/
	explicit StdError(int error);
	~StdError() throw();
};

#if __APPLE__ || __GNUC__ >= 4
#define TMTDEADFN __dead2
#elif defined(__GNUC__)
#define TMTDEADFN __attribute__ ((__noreturn__))
#else
#define TMTDEADFN 
#endif

/// TMT initialization function
/** Use this function before calling or initializing any other function or class
	defined in TMT. This function will perform all the necessary initializations.
*/
void InitTMT();
/// @cond
void TMTFatal1(const char *message) TMTDEADFN;
void TMTFatal2(const char *string1, const char *string2) TMTDEADFN;
void TMTFatal2(const char *string1, const string &string2) TMTDEADFN;
void TMTLog(const char *string1, const char *format, ...);
/// @endcond

/// @cond
#define __TMT_STRINGIFY2__(condition) #condition
#define __TMT_STRINGIFY__(condition) __TMT_STRINGIFY2__(condition)
/// @endcond
#define CHECK(condition)	if (condition) (void) 0; \
					else ::TMT::TMTFatal1(__FILE__ ":" \
								   __TMT_STRINGIFY__(__LINE__) \
								   ": CHECK(" #condition ") failed.")
#ifdef NDEBUG
#define DCHECK(condition) if (condition) (void) 0; else ((void) 0)
#else
#define DCHECK(condition)	if (condition) (void) 0; \
					else ::TMT::TMTFatal1(__FILE__ ":" \
								   __TMT_STRINGIFY__(__LINE__) \
								   ": DCHECK(" #condition ") failed.")
#endif

/// Throw an exception if the condition is false.
/** \def CHECK(condition)
	\param condition an expression that evaluates to test context.

	Expression given to \link CHECK \endlink will always be evaluated. If the condition is not
	satisfied, the exception is thrown. Condition will be checked even when the
	program is not run in debug mode.

	\attention
	Do not use this macro in performance critical parts. Rather use \link DCHECK \endlink.
*/

/// Checks for the condition only in debug mode. If false, throws the exception.
/** \def DCHECK(condition)
	\param condition an expression that evaluates to test context.

	Expression given to \link DCHECK \endlink will be evaluated only when the program is compiled
	using debug mode. If the program is run in debug mode and the condition is not
	satisfied, the exception is thrown.

	\attention
	When the program is not run in debug mode, the condition will not be evaluated.
*/
#define FATAL(errorString) \
/** \cond */\
::TMT::TMTFatal2(__FILE__ ":" __TMT_STRINGIFY__(__LINE__) ": " , (errorString));
/// \endcond

/// Throws an exception with description given in errorString.
/** \def FATAL
	\param errorString can be null terminated string or stl string.

	The exception thrown will contain current file, current line number and errorString.
*/
#define FATAL(errorString) \
/** \cond */\
::TMT::TMTFatal2(__FILE__ ":" __TMT_STRINGIFY__(__LINE__) ": " , (errorString));
/// \endcond

	extern int TMTVerbosity;
	extern int TMTNThreads;

/// Logs an error if verbosity level is at least \p level.
/** \def LOG
	\param level minimum verbosity level.

	You can change verbosity level by modifying variable TMTVerbosity or by
	using command line option --verbosity.
*/
#define LOG(level, ...) \
/** \cond */\
	if (::TMT::TMTVerbosity >= (level)) \
		TMTLog(__FILE__ ":" __TMT_STRINGIFY__(__LINE__) ": ", __VA_ARGS__); \
	else ((void) 0)
/// \endcond
#ifdef NDEBUG
#define DLOG(level, ...) \
/** \cond */\
	if (level) (void) 0; else ((void) 0)
/// \endcond
#else
#define DLOG(level, ...) \
/** \cond */\
	LOG(level, __VA_ARGS__)
/// \endcond
#endif

/// Same as LOG, but works only in debug mode.
/** \def DLOG
*/

}

#endif
