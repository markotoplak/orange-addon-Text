#include "orngTextWrapper/Wrapper.h"
#include "tmt/common/Common.h"
#include "tmt/lemmatization/FSALemmatization.h"
#include "tmt/lemmatization/PorterStemmer.h"
#include "tmt/strings/StringUtils.h"
#include "tmt/strings/UTF8Tokenizer.h"

#include <algorithm>

static void InitTMTOrange()
{
	TMT::InitTMT();
}

baseLemmatizer::~baseLemmatizer()
{
}

std::string baseLemmatizer::lemmatizeText(const char *s) const
{
	InitTMTOrange();
	TMT::UTF8Tokenizer tokenizer(s, false);
	std::string result;
	for (TMT::UTF8Tokenizer::iterator i = tokenizer.begin(); i != tokenizer.end(); ++i)
		if (i->isWord())
			result += getLemma(i->getString().c_str());
		else
			result.append(i->start, i->end);
	return result;
}

lemmatizer::lemmatizer(const char *path) : lem(0)
{
	InitTMTOrange();
	lem = new TMT::FSALemmatization(path);
}

lemmatizer::~lemmatizer()
{
	delete lem;
}

enum WordCase
{
	Lowercase,
	Uppercase,
	Titlecase,
	Mixedcase
};

static void MatchCase(WordCase wc, std::string *trg)
{
	if (wc == Lowercase || trg->empty())
		return;
	if (wc == Titlecase)
	{
		int split = TMT::UTF8CharSize(trg->c_str());
		std::string tmp;
		TMT::UTF8Uppercase(trg->substr(0, split), &tmp);
		*trg = tmp + trg->substr(split);
	}
	else
	{
		std::string tmp;
		TMT::UTF8Uppercase(*trg, &tmp);
		*trg = tmp;
	}
}

std::string lemmatizer::getLemma(const char *s) const
{
	InitTMTOrange();
	std::string lowercased;
	TMT::UTF8Lowercase(s, &lowercased);
	std::vector<std::string> result = lem->getLemmas(lowercased);
	if (result.empty())
		return s;

	WordCase targetCase = Lowercase;

	if (s != lowercased)
	{
		int nUCased = 0;
		const char *ps = s;
		const char *pl = lowercased.c_str();
		for (int i = 0, j = 0; j < lowercased.size();)
		{
			if (TMT::UTF8GetUCS(ps + i) != TMT::UTF8GetUCS(pl + j))
				++nUCased;

			i += TMT::UTF8CharSize(ps + i);
			j += TMT::UTF8CharSize(pl + j);
		}

		if (nUCased > 0)
			targetCase = Uppercase;
		if (nUCased == 1 && TMT::UTF8GetUCS(ps) != TMT::UTF8GetUCS(pl))
			targetCase = Titlecase;
	}

	MatchCase(targetCase, &result[0]);

	return result[0];
}

std::string porter::getLemma(const char *s) const
{
	InitTMTOrange();
	return TMT::PorterStemmer().stem(s);
}

std::vector<std::string> tokenizeNonWords(const char *text)
{
	InitTMTOrange();
	std::vector<std::string> result;
	TMT::UTF8Tokenizer tokenizer(text);
	for (TMT::UTF8Tokenizer::iterator i = tokenizer.begin(); i != tokenizer.end(); ++i)
		if (i->isWord() && !i->hasDigits())
			result.push_back(i->getString());
	return result;
}

std::string removeWords(const char *text, const std::vector<std::string> &words)
{
	InitTMTOrange();
	std::vector<std::string> sortedWords(words.size());
	for (int i = 0; i < words.size(); ++i)
		sortedWords[i] = words[i];
	sort(sortedWords.begin(), sortedWords.end());

	InitTMTOrange();
	TMT::UTF8Tokenizer tokenizer(text);
	bool lastWasWhiteSpace;
	std::string result, lastToken, curToken;
	for (TMT::UTF8Tokenizer::iterator i = tokenizer.begin(); i != tokenizer.end(); ++i)
	{
		if (lastToken.empty())
			lastWasWhiteSpace = false;

		curToken = i->getString();

		if (i->isWord())
		{
			if (binary_search(sortedWords.begin(), sortedWords.end(), curToken))
				curToken.clear();
			else
				result += lastToken;
		}
		else
			result += lastToken;

		curToken.swap(lastToken);
		lastWasWhiteSpace = i->isWhitespace();
	}
	result += lastToken;

	return result;
}

#include "lemmagen/RdrLemmatizer.h"

lemmagen::lemmagen(const char *path) : lem(0)
{
	lem = new RdrLemmatizer();
	lem->LoadBinary(path);
}

lemmagen::~lemmagen()
{
	delete lem;
}

std::string lemmagen::getLemma(const char *s) const
{
	char *str = lem->Lemmatize(s, 0);
	std::string rez = str;
	delete[] str;
	return rez;
}
