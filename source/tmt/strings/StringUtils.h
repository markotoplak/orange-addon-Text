#ifndef TMT__STRINGS__STRING_UTILS_H
#define TMT__STRINGS__STRING_UTILS_H

#include "tmt/common/Common.h"

#include <cstdio>
#include <string>
#include <vector>

/// Various string utils.
/*! \file StringUtils.h
	Before working with strings one should learn more about various encodings,
	especially UTF-8 encoding. Functions described here can be used to process
	UTF-8 and ISO-8859-2 encoded strings.
*/

namespace TMT
{

namespace StringUtils
{
	extern int initialized;
	extern const int utf8CharBytes[256];
	extern const int uppercaseMap[][2];
	extern const int lowercaseMap[][2];
	extern const unsigned char lowerLatin2Table[256];
	extern const unsigned char upperLatin2Table[256];
	extern const unsigned char latin2CharValue[256];
	extern const unsigned char collateVals[0x20000];
	extern int *utf8UppercaseTable;
	extern int *utf8LowercaseTable;
}

void InitStringUtils();

/// Collates two UTF-8 strings.
/** This function collattes two UTF-8 strings. String order resembles
	word order in Croatian dictionaries.

	\param a first UTF-8 string
	\param b second UTF-8 string
	\return 0 if strings are same.
	\return Number less than 0 if \c a should come before \c b in Croatian
	dictionary.
	\return Number greater than 0 otherwise.
*/
int UTF8Collate(const char *a, const char *b);

/// Stores uppercased \c str to \c trg.
void UTF8Uppercase(const std::string &src, std::string *trg);
/// Stores uppercased \c str to \c trg.
/** \overload
*/
void UTF8Uppercase(const char *src, std::string *trg);
/// Stores lowercased \c str to \c trg.
void UTF8Lowercase(const std::string &src, std::string *trg);
/// Stores lowercased \c str to \c trg.
/** \overload
*/
void UTF8Lowercase(const char *src, std::string *trg);
/// Tests whether \c s points to a valid UTF-8 character.
bool UTF8IsValidChar(const char *s);
/// Tests whether \c s points to alphabetic UTF-8 character.
bool UTF8IsAlpha(const char *c);
/// Tests whether \c s points to upper case UTF-8 character.
bool UTF8IsUpper(const char *c);

int UTF8CountChars(const char *s);
int UTF8GetUCS(const char *cp);
void UCSToUTF8(int ucs, std::string *utf8);
void UTF8AppendUCS(std::string *utf8, int ucs);
int UTF8CharPosToBytePos(const char *str, int charPos);
int UTF8BytePosToCharPos(const char *str, int bytePos);

int Latin2IgnoreCaseCompare(const char *a, const char *b);
int Latin2CaseCompare(const char *a, const char *b);
void Latin2Lowercase(const std::string &src, std::string *trg);
void Latin2Uppercase(const std::string &src, std::string *trg);

int StringToInt(const std::string &s);
int StringToInt(const char *s);
double StringToDouble(const std::string &s);
double StringToDouble(const char *s);
std::string IntToString(int x);

void StringCEscape(const std::string &x, std::string *escaped);

std::string StringPrintf(const char *p, ...);
bool UTF8IsValid(const char *buffer, int length, int *firstErrorOffset);

void SplitStringUsing(const std::string &s, const char *separators, std::vector<std::string> *result);
void JoinStrings(const std::vector<std::string> &strings, const char *separator, std::string *result);

void ReadTextFromFile(const std::string &path, string *result, bool normalizeAndFix = true);
void ReadTextFromFile(std::FILE *fp, std::string *result);
void NormalizeLineEndings(const std::string &src, std::string *trg);
void UTF8ReplaceInvalidChars(const char *buffer, int length, const std::string &replacement,
							 std::string *trg);

void StripFileExtension(const std::string &path, bool stripAllExtensions, std::string *result);


bool StringContains(const std::string &str, const std::string &what, int offset);
inline bool StringStartsWith(const std::string &str, const std::string &prefix)
{
	return StringContains(str, prefix, 0);
}

inline bool StringEndsWith(const std::string &str, const std::string &suffix)
{
	return StringContains(str, suffix, str.size() - suffix.size());
}

void StringReplace(const std::string &src, const std::string &oldString,
				   const std::string &newString, bool repeat, std::string *trg);

std::string TrimString(const std::string &str, const char *drop = " \t\n\r\v\0");

inline int UTF8CharSize(const char *c)
{
	DCHECK(StringUtils::initialized);
	return StringUtils::utf8CharBytes[static_cast<unsigned char>(*c)];
}

inline const char *UTF8NextChar(const char *c)
{
	DCHECK(StringUtils::initialized);
	return c + StringUtils::utf8CharBytes[static_cast<unsigned char>(*c)];
}

inline char *UTF8NextChar(char *c)
{
	DCHECK(StringUtils::initialized);
	return c + StringUtils::utf8CharBytes[static_cast<unsigned char>(*c)];
}

inline bool UTF8IsASCII(const char *c)
{
	return !(*c & 0x80);
}

inline bool UTF8IsMultibyte(const char *c)
{
	return !!(*c & 0x80);
}

inline bool UTF8IsAlphanum(const char *c)
{
	DCHECK(StringUtils::initialized);
	return c[0] >= '0' && c[0] <= '9' || UTF8IsAlpha(c);
}

inline bool Latin2IsAlpha(unsigned char c)
{
	DCHECK(StringUtils::initialized);
	return StringUtils::lowerLatin2Table[c] != StringUtils::upperLatin2Table[c];
}

inline bool Latin2IsAlphanum(unsigned char c)
{
	DCHECK(StringUtils::initialized);
	return c >= '0' && c <= '9' || StringUtils::lowerLatin2Table[c] != StringUtils::upperLatin2Table[c];
}

}

#endif
