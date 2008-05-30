#include "tmt/common/Common.h"
#include "tmt/common/Files.h"
#include "tmt/strings/StringUtils.h"

#include <string>
#include <cerrno>
#include <cstdio>
#include <cstdarg>
#include <stdexcept>
#include <algorithm>
#include <iostream>

using namespace std;
using namespace TMT::StringUtils;

namespace TMT
{

int StringUtils::initialized = 0;

const int StringUtils::utf8CharBytes[256] =
{
	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
	2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
	3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3, 4,4,4,4,4,4,4,4,5,5,5,5,6,6,6,6
};

int *StringUtils::utf8UppercaseTable;
int *StringUtils::utf8LowercaseTable;

const int StringUtils::uppercaseMap[][2] =
{
#include "tmt/strings/utfUpper"
};

const int StringUtils::lowercaseMap[][2] =
{
#include "tmt/strings/utfLower"
};

void InitStringUtils()
{
	if (initialized)
		return;

	utf8UppercaseTable = new int[65536];
	utf8LowercaseTable = new int[65536];

	int i;

	for (i = 0; i < 65536; ++i)
		utf8UppercaseTable[i] = i;
	for (i = 0; i < (sizeof(uppercaseMap) / sizeof(uppercaseMap[0])); ++i)
		utf8UppercaseTable[uppercaseMap[i][0]] = uppercaseMap[i][1];
	for (i = 0; i < 65536; ++i)
		utf8LowercaseTable[i] = i;
	for (i = 0; i < (sizeof(lowercaseMap) / sizeof(lowercaseMap[0])); ++i)
		utf8LowercaseTable[lowercaseMap[i][0]] = lowercaseMap[i][1];

	initialized = 1;
}

bool UTF8IsAlpha(const char *c)
{
	DCHECK(initialized);
	DCHECK(c);
	const unsigned char *uc = reinterpret_cast<const unsigned char *>(c);
	unsigned char uc0 = uc[0];
	if (uc0 <= 127)
		return utf8LowercaseTable[uc0] != utf8UppercaseTable[uc0];
	int u16 = (uc0 << 8) | uc[1];
	return utf8LowercaseTable[u16] != utf8UppercaseTable[u16];
}

bool UTF8IsUpper(const char *p)
{
	DCHECK(initialized);
	DCHECK(p);

	unsigned char c = *reinterpret_cast<const unsigned char *>(p);
	if (c <= 127)
		return utf8UppercaseTable[c] == c;

	int cn = p[1];
	int idx = (c << 8) | cn;
	return idx == utf8UppercaseTable[idx];
}

int UTF8CountChars(const char *s)
{
	DCHECK(initialized);
	DCHECK(s);
	unsigned int i;
	int rez = 0;
	for (i = 0; s[i]; ++rez)
		i += utf8CharBytes[static_cast<unsigned char>(s[i])];

	return rez;
}

int UTF8BytePosToCharPos(const char *str, int bytePos)
{
	DCHECK(initialized);
	DCHECK(str);
	int i, charPos, fwd;

	for (i = charPos = 0; i < bytePos; ++charPos)
	{
		fwd = utf8CharBytes[static_cast<unsigned char>(str[i])];
		i += fwd;
	}

	return charPos;
}

int UTF8CharPosToBytePos(const char *str, int charPos)
{
	DCHECK(initialized);
	DCHECK(str);
	int i, bytePos, fwd;

	for (i = bytePos = 0; i < charPos; ++i)
	{
		fwd = utf8CharBytes[static_cast<unsigned char>(str[bytePos])];
		bytePos += fwd;
	}

	return bytePos;
}

int UTF8GetUCS(const char *cp)
{
	DCHECK(initialized);
	DCHECK(cp);
	const unsigned char *ucp = reinterpret_cast<const unsigned char *>(cp);
	unsigned char uc = *ucp;

	switch (utf8CharBytes[uc])
	{
		#define s(a,b,c)((a & b) << c)
		case 1: return uc;
		case 2: return	s(uc, 0x1F, 6) |
						s(ucp[1], 0x3F, 0);
		case 3: return	s(uc, 0xF, 12) |
						s(ucp[1], 0x3F, 6) |
						s(ucp[2], 0x3F, 0);
		case 4: return	s(uc, 0x7, 18) |
						s(ucp[1], 0x3F, 12) |
						s(ucp[2], 0x3F, 6) |
						s(ucp[3], 0x3F, 0);
		#undef s
	}
	return -1;
}

void UTF8AppendUCS(string *utf8, int ucs)
{
	DCHECK(initialized);
	DCHECK(utf8);
	if (ucs <= 0x7F)
		*utf8 += static_cast<char>(ucs);
	else if (ucs <= 0x7FF)
	{
		*utf8 += static_cast<char>(0xC0 | (ucs >> 6));
		*utf8 += static_cast<char>(0x80 | (ucs & 0x3F));
	}
	else if (ucs <= 0xFFFF)
	{
		*utf8 += static_cast<char>(0xE0 | (ucs >> 12));
		*utf8 += static_cast<char>(0x80 | ((ucs >> 6) & 0x3F));
		*utf8 += static_cast<char>(0x80 | (ucs & 0x3F));
	}
	else
	{
		*utf8 += static_cast<char>(0xF0 | (ucs >> 18));
		*utf8 += static_cast<char>(0x80 | ((ucs >> 12) & 0x3F));
		*utf8 += static_cast<char>(0x80 | ((ucs >> 6) & 0x3F));
		*utf8 += static_cast<char>(0x80 | (ucs & 0x3F));
	}
}

void UCSToUTF8(int ucs, string *utf8)
{
	CHECK(utf8);
	utf8->clear();
	UTF8AppendUCS(utf8, ucs);
}

bool UTF8IsValidChar(const char *s)
{
	DCHECK(initialized);
	DCHECK(s);
	unsigned char c = static_cast<unsigned char>(s[0]);

	if (c <= 0x7F) // 7 bit ASCII
		return true;
	if (c <= 0xC1)
		return false;
	if (c <= 0xDF)
	{
		// 2-byte chars
		unsigned char d = static_cast<unsigned char>(s[1]);
		return d >= 0x80 && d <= 0xBF;
	}
	if (c <= 0xEF)
	{
		// 3-byte chars
		unsigned char d = static_cast<unsigned char>(s[1]);
		if (d < 0x80 || d > 0xBF)
			return false;
		if (c == 0xE0 && d < 0xA0)
			return false;
		d = static_cast<unsigned char>(s[2]);
		return d >= 0x80 && d <= 0xBF;
	}
	if (c < 0xF5)
	{
		// 4-byte chars
		unsigned char d = static_cast<unsigned char>(s[1]);
		if (d < 0x80 || d > 0xBF)
			return false;
		if (c == 0xF0 && d < 0x90)
			return false;
		d = static_cast<unsigned char>(s[2]);
		if (d < 0x80 || d > 0xBF)
			return false;
		d = static_cast<unsigned char>(s[3]);
		return d >= 0x80 && d <= 0xBF;
	}
	return false;
}

int StringToInt(const char *s)
{
	DCHECK(s);
	return atoi(s);
}

int StringToInt(const string &s)
{
	return StringToInt(s.c_str());
}

double StringToDouble(const char *s)
{
	DCHECK(s);
	return atof(s);
}

double StringToDouble(const string &s)
{
	return StringToDouble(s.c_str());
}

string IntToString(int x)
{
	string rez;
	bool negative = false;

	if (x < 0)
	{
		negative = true;
		x = -x;
	}

	do rez += static_cast<char>('0' + x % 10); while (x /= 10);
	if (negative)
		rez += '-';
	reverse(rez.begin(), rez.end());

	return rez;
}

static void UTF8UppercaseMutable(string &utf)
{
	DCHECK(initialized);
	unsigned char *utfPtr = reinterpret_cast<unsigned char *>(&utf[0]);

	for (;;)
	{
		int c = *utfPtr;
		if (!c)
			break;

		if (c <= 127)
			*utfPtr++ = utf8UppercaseTable[c];
		else
		{
			int cn, val;

			cn = utfPtr[1];
			val = utf8UppercaseTable[(c << 8) | cn];
			utfPtr[0] = val >> 8;
			utfPtr[1] = val & 0xFF;
			utfPtr += utf8CharBytes[c];
		}
	}
}

static void UTF8LowercaseMutable(string &utf)
{
	DCHECK(initialized);
	unsigned char *utfPtr = reinterpret_cast<unsigned char *>(&utf[0]);

	for (;;)
	{
		int c = *utfPtr;
		if (!c)
			break;

		if (c <= 127)
			*utfPtr++ = utf8LowercaseTable[c];
		else
		{
			int cn, val;

			cn = utfPtr[1];
			val = utf8LowercaseTable[(c << 8) | cn];
			utfPtr[0] = val >> 8;
			utfPtr[1] = val & 0xFF;
			utfPtr += utf8CharBytes[c];
		}
	}
}

void UTF8Lowercase(const string &src, string *trg)
{
	CHECK(&src != trg);
	CHECK(trg);
	*trg = src;
	UTF8LowercaseMutable(*trg);
}

void UTF8Uppercase(const string &src, string *trg)
{
	CHECK(&src != trg);
	CHECK(trg);
	*trg = src;
	UTF8UppercaseMutable(*trg);
}

void UTF8Lowercase(const char *src, string *trg)
{
	CHECK(src);
	CHECK(trg);
	*trg = src;
	UTF8LowercaseMutable(*trg);
}

void UTF8Uppercase(const char *src, string *trg)
{
	CHECK(src);
	CHECK(trg);
	*trg = src;
	UTF8UppercaseMutable(*trg);
}

int UTF8Collate(const char *a, const char *b)
{
	DCHECK(initialized);
	int caseDiff = 0;
	unsigned char ca, cb;
	int vala, valb;

	for (;;)
	{
		ca = *a, cb = *b;
		if (!ca || !cb)
		{
			if (!ca && !cb)
				return caseDiff;
			return static_cast<int>(ca) - static_cast<int>(cb);
		}

		vala = ca <= 127 ? ca : (ca << 8) | static_cast<unsigned char>(a[1]);
		valb = cb <= 127 ? cb : (cb << 8) | static_cast<unsigned char>(b[1]);
		if (!caseDiff)
			caseDiff = collateVals[vala * 2] + (collateVals[vala * 2 + 1] << 8) -
						collateVals[valb * 2] - (collateVals[valb * 2 + 1] << 8);

		if (utf8UppercaseTable[vala] != utf8UppercaseTable[valb])
		{
			int ia = utf8UppercaseTable[vala] * 2;
			int ib = utf8UppercaseTable[valb] * 2;
			return collateVals[ia] + (collateVals[ia + 1] << 8) -
						collateVals[ib] - (collateVals[ib + 1] << 8);
		}
		a += utf8CharBytes[ca];
		b += utf8CharBytes[cb];
	}
}

void Latin2LowercaseMutable(unsigned char *start, int len)
{
	DCHECK(initialized);
	CHECK(start);
	int i;

	for (i = 0; i < len; ++i, ++start)
		*start = lowerLatin2Table[*start];
}

void Latin2LowercaseMutable(unsigned char *start)
{
	DCHECK(initialized);
	CHECK(start);
	for (;(*start = lowerLatin2Table[*start]) != 0;)
		;
}

void Latin2Lowercase(const string &src, string *trg)
{
	DCHECK(initialized);
	CHECK(trg);
	CHECK(&src != trg);
	*trg = src;
	unsigned int i;

	for (i = 0; i < trg->size(); ++i)
		(*trg)[i] = lowerLatin2Table[static_cast<unsigned char>((*trg)[i])];
}

void Latin2UppercaseMutable(unsigned char *start, int len)
{
	DCHECK(initialized);
	CHECK(start);
	int i;

	for (i = 0; i < len; ++i, ++start)
		*start = upperLatin2Table[*start];
}

void Latin2UppercaseMutable(unsigned char *start)
{
	DCHECK(initialized);
	CHECK(start);
	for (;(*start = upperLatin2Table[*start]) != 0;)
		;
}

void Latin2Uppercase(const string &src, string *trg)
{
	DCHECK(initialized);
	CHECK(trg);
	CHECK(&src != trg);
	*trg = src;
	unsigned int i;

	for (i = 0; i < trg->size(); ++i)
		(*trg)[i] = upperLatin2Table[static_cast<unsigned char>((*trg)[i])];
}

int Latin2IgnoreCaseCompare(const char *a, const char *b)
{
	DCHECK(initialized);
	CHECK(a);
	CHECK(b);
	const unsigned char *ca = reinterpret_cast<const unsigned char *>(a);
	const unsigned char *cb = reinterpret_cast<const unsigned char *>(b);
	unsigned char uca, ucb;
	for (;; ++ca, ++cb)
	{
		uca = *ca;
		ucb = *cb;
		if (!uca || !ucb)
			break;
		unsigned char xa, xb;
		xa = latin2CharValue[upperLatin2Table[uca]];
		xb = latin2CharValue[upperLatin2Table[ucb]];
		if (xa != xb)
			return xa - xb;
	}
	return latin2CharValue[upperLatin2Table[uca]] - latin2CharValue[upperLatin2Table[ucb]];
}

int Latin2CaseCompare(const char *a, const char *b)
{
	DCHECK(initialized);
	CHECK(a);
	CHECK(b);
	int rez = Latin2IgnoreCaseCompare(a, b);

	if (rez) return rez;

	const unsigned char *ca = reinterpret_cast<const unsigned char *>(a);
	const unsigned char *cb = reinterpret_cast<const unsigned char *>(b);
	unsigned char uca, ucb;
	for (;; ++ca, ++cb)
	{
		uca = *ca;
		ucb = *cb;
		if (!uca || !ucb)
			break;
		unsigned char xa, xb;
		xa = latin2CharValue[uca];
		xb = latin2CharValue[ucb];
		if (xa != xb)
			return xa - xb;
	}
	return latin2CharValue[uca] - latin2CharValue[ucb];
}

string StringPrintf(const char *p, ...)
{
	DCHECK(p);
	static char buf[10000];
	va_list l;
	va_start(l, p);
#ifdef _MSC_VER
	_vsnprintf(buf, sizeof(buf), p, l);
#else
	vsnprintf(buf, sizeof(buf), p, l);
#endif
	va_end(l);
	return string(buf);
}

bool UTF8IsValid(const char *buffer, int length, int *firstErrorOffset)
{
	CHECK(buffer);
	DCHECK(initialized);
	for (int offset = 0; offset < length;)
	{
		if (!UTF8IsValidChar(buffer + offset))
		{
			if (firstErrorOffset)
				*firstErrorOffset = offset;
			return false;
		}
		offset += UTF8CharSize(buffer + offset);
	}

	return true;
}

void UTF8ReplaceInvalidChars(const char *buffer, int length, const string &replacement,
							 string *trg)
{
	DCHECK(initialized);
	CHECK(buffer);
	CHECK(trg);

	trg->clear();
	for (int offset = 0; offset < length;)
		if (!UTF8IsValidChar(buffer + offset))
		{
			trg->append(replacement);
			++offset;
		}
		else
		{
			int charSize = UTF8CharSize(buffer + offset);
			trg->append(buffer + offset, charSize);
			offset += charSize;
		}
}

// TODO: ubrzati
void NormalizeLineEndings(const string &src, string *trg)
{
	CHECK(trg);
	CHECK(&src != trg);

	trg->clear();
	trg->reserve(src.size());
	
	bool state_13 = false;
	for (size_t i = 0; i < src.size(); ++i)
	{
		if (!state_13)
		{
			if (src[i] == 10)
				*trg += '\n';
			else if (src[i] == 13)
				state_13 = true;
			else
				*trg += src[i];
		}
		else
		{
			if (src[i] == 10)
			{
				*trg += '\n';
				state_13 = false;
			}
			else if (src[i] == 13)
				*trg += '\n';
			else
			{
				*trg += '\n';
				*trg += src[i];
				state_13 = false;
			}
		}
	}
	if (state_13)
		*trg += '\n';
}

void ReadTextFromFile(const std::string &path, string *result, bool normalizeAndFix)
{
	FILE *fp = tmtfopen(path.c_str(), "rb");
	try
	{
		string tmp;
		ReadTextFromFile(fp, &tmp);
		if (normalizeAndFix)
		{
			NormalizeLineEndings(tmp, result);
			result->swap(tmp);
			UTF8ReplaceInvalidChars(tmp.c_str(), tmp.size(), "", result);
		}
		else
			result->swap(tmp);
	}
	catch(...)
	{
		fclose(fp);
		throw;
	}
	fclose(fp);
}

void ReadTextFromFile(FILE *fp, string *result)
{
	CHECK(fp);
	CHECK(result);
	result->clear();
	static const size_t bufferSize = 16384;
	char *buffer = new char[bufferSize];
	for (;;)
	{
		size_t nRead = fread(buffer, 1, bufferSize, fp);
		result->append(buffer, nRead);
		if (nRead < bufferSize)
			break;
	}
	delete[] buffer;
}

bool StringContains(const string &str, const string &what, int offset)
{
	if (offset < 0 || what.size() + offset > str.size())
		return false;
	for (size_t i = 0; i < what.size(); ++i)
		if (what[i] != str[offset + i])
			return false;
	return true;
}

void SplitStringUsing(const string &s, const char *separators, vector<string> *result)
{
	CHECK(result);
	CHECK(separators);
	result->clear();
	if (s.empty())
		return;
	size_t pos = s.find_first_not_of(separators);
	while (pos != string::npos)
	{
		size_t token_end = s.find_first_of(separators, pos);
		if (token_end == string::npos)
		{
			result->push_back(s.substr(pos));
			break;
		}
		result->push_back(s.substr(pos, token_end - pos));
		pos = s.find_first_not_of(separators, token_end);
	}
}

void JoinStrings(const vector<string> &strings, const char *separator, string *result)
{
	CHECK(result);
	CHECK(separator);
	result->clear();
	if (strings.empty())
		return;

	int separatorLen = 0;
	for (; separator[separatorLen]; ++separatorLen) ;

	int totalLen = 0;
	for (int i = 0; i < strings.size(); ++i)
		totalLen += strings[i].size();

	totalLen += separatorLen * (strings.size() - 1);
	result->resize(totalLen);

	char *ptr = &(*result)[0];
	for (int i = 0; i < strings.size(); ++i)
	{
		if (i)
		{
			copy(separator, separator + separatorLen, ptr);
			ptr += separatorLen;
		}
		const char *si = strings[i].c_str();
		int ss = strings[i].size();
		copy(si, si + ss, ptr);
		ptr += ss;
	}
}

string TrimString(const string &str, const char *drop)
{
	size_t start = str.find_first_not_of(drop);
	if (start == string::npos)
		return string();
	size_t end = str.find_last_not_of(drop);
	return str.substr(start, end + 1 - start);
}

void StripFileExtension(const string &path, bool stripAllExtensions, string *result)
{
	CHECK(result);

	int dotPos = path.size();
	for (int pos = path.size() - 1; pos > 0; --pos)
		if (path[pos] >= 'a' && path[pos] <= 'z' ||
			path[pos] >= 'A' && path[pos] <= 'Z' ||
			path[pos] >= '0' && path[pos] <= '9')
			continue;
		else if (path[pos] == '.')
		{
			dotPos = pos;
			if (!stripAllExtensions)
				break;
		}
		else break;
	*result = path.substr(0, dotPos);
}

void StringReplace(const string &src, const string &oldString,
				   const string &newString, bool repeat, string *trg)
{
	CHECK(trg);
	trg->clear();
	int lastPos = 0;
	for (; lastPos < src.size();)
	{
		int pos = src.find(oldString, lastPos);
		if (pos == string::npos)
			break;
		trg->append(src, lastPos, pos - lastPos);
		trg->append(newString);
		lastPos = pos + oldString.size();
		if (!repeat)
			break;
	}
	if (lastPos < src.size())
		trg->append(src, lastPos, src.size() - lastPos);
}

void StringCEscape(const std::string &x, std::string *escaped)
{
	CHECK(escaped);

	escaped->clear();

	for (int i = 0; i < x.size(); ++i)
	{
		unsigned char curChar = static_cast<unsigned char>(x[i]);
		if (curChar == '\n')
			*escaped += "\\n";
		else if (curChar == '\t')
			*escaped += '\t';
		else if (curChar < 32)
			*escaped += StringPrintf("\\%03o", curChar);
		else if (curChar == '"')
			*escaped += "\\\"";
		else if (curChar == '\\')
			*escaped += "\\\\";
		else
			*escaped +=curChar;
	}
}

const unsigned char StringUtils::lowerLatin2Table[256] =
{
#include "tmt/strings/latin2Lower"
};

const unsigned char StringUtils::upperLatin2Table[256] =
{
#include "tmt/strings/latin2Upper"
};

const unsigned char StringUtils::latin2CharValue[256] =
{
#include "tmt/strings/latin2Value"
};

const unsigned char StringUtils::collateVals[0x20000] =
{
#include "tmt/strings/utfCollate"
};

} // namespace TMT
