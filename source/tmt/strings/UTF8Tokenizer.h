#ifndef TMT__STRINGS__UTF8TOKENIZER_H
#define TMT__STRINGS__UTF8TOKENIZER_H

#include "tmt/common/Common.h"

#include <string>
#include <iterator>

namespace TMT
{

/// A class for UTF-8 tokenization
/** This class enables very fast UTF-8 tokenization. When dealing with
	international text you should use this class instead of simple ASCII
	processing.

	The following code snippet prints all words in a string, ignoring
	whitespace and punctuation:

	\code
string sentence;
getline(cin, sentence);
// In a production code you should not assume the console encoding is UTF-8.
UTF8Tokenizer tokens(sentence);

for (UTF8Tokenizer::iterator it = tokens.begin(); it != tokens.end(); ++it)
	if (it->isWord() && !it->isNumber())
		cout << *it << endl;
	\endcode

	Constructing, destructing, incrementing and comparing iterators is O(1)
	operation. Only increment operators need to access memory. Iterators point
	to objects of type UTF8Tokenizer::Token.

	\see UTF8Tokenizer::Token, EncodingConverter
*/
class UTF8Tokenizer
{
	class TokenIterator;
public:
	/// A class representing a single token.
	/** Token objects describe one consecutive run of characters.
		You can use various methods to find out what kind of token
		it is.

		Method getString allocates a new string, so it should be
		used with care in performance-critical parts of program.
		You might want to directly read start and end.

		Methods UTF8Tokenizer::isNumber and UTF8Tokenizer::hasDigits
		currently require processing time proportional to the token
		size.

		All other methods are O(1).
		\see UTF8Tokenizer
	*/
	class Token
	{
		int mask;
	public:
		friend class TokenIterator;
		/// A pointer to the token beginning.
		const char *start;
		/// A pointer to the one character after token's end.
		const char *end;
		bool hasDigits() const;
		bool isUnicodeBOM() const;
		bool isEOT() const;
		bool isIllegalUTF8() const;
		bool isNumber() const;
		bool isPunctuation() const;
		bool isURI() const;
		bool isWhitespace() const;
		bool isWord() const;
		string getString() const;
	};
private:
	class TokenIterator : public std::iterator<std::forward_iterator_tag, Token>
	{
		Token token;
		unsigned const char *scan(unsigned const char *p);
		explicit TokenIterator(const char *ptr);
	public:
		TokenIterator();
		const TokenIterator &operator ++ ();
		TokenIterator operator ++ (int);
		bool operator == (const TokenIterator &b) const;
		bool operator != (const TokenIterator &b) const;
		Token operator * () const;
		const Token *operator -> () const;
		friend class UTF8Tokenizer;
	};
	const char *ptr;
	const bool retainCopy;
	const int len;
	void init(const char *s);
public:
	typedef TokenIterator iterator;

	/// Constructs UTF-8 tokenizer with a given c string
	/** Class UTF8Tokenizer during its construction copies the provided string.
		In some cases that may not be the desired behaviour, so you can set option
		\em copy to false. In that case, you <B>must not</B> deallocate the string before
		you continue to use the tokenizer object.
	*/
	UTF8Tokenizer(const char *s, bool copy = true);
	/// Constructs UTF-8 tokenizer with a given string.
	/** \overload
	*/
	UTF8Tokenizer(const string &s, bool copy = true);

	/// Returns an iterator pointing to the first element.
	iterator begin() const;
	/// Returns an iterator pointing to one element after the last element.
	iterator end() const;

	~UTF8Tokenizer();
};

inline UTF8Tokenizer::TokenIterator::TokenIterator()
{
}

inline const UTF8Tokenizer::TokenIterator &UTF8Tokenizer::TokenIterator::operator ++ ()
{
	token.start = token.end;
	token.end = reinterpret_cast<const char *>(
					scan(reinterpret_cast<unsigned const char *>(token.end)));

	return *this;
}

inline UTF8Tokenizer::TokenIterator UTF8Tokenizer::TokenIterator::operator ++ (int)
{
	TokenIterator tmp(*this);
	++*this;
	return tmp;
}

inline bool UTF8Tokenizer::TokenIterator::operator == (const TokenIterator &b) const
{
	return token.start == b.token.start;
}

inline bool UTF8Tokenizer::TokenIterator::operator != (const TokenIterator &b) const
{
	return token.start != b.token.start;
}

inline UTF8Tokenizer::Token UTF8Tokenizer::TokenIterator::operator * () const
{
	return token;
}

inline const UTF8Tokenizer::Token *UTF8Tokenizer::TokenIterator::operator -> () const
{
	return &token;
}

inline UTF8Tokenizer::TokenIterator::TokenIterator(const char *ptr)
{
	token.start = token.end = ptr;
	token.mask = 1;   //TokenEOT;
}

inline UTF8Tokenizer::iterator UTF8Tokenizer::end() const
{
	return iterator(ptr + len);
}

}

#endif
