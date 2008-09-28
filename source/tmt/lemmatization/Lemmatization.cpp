#include "tmt/lemmatization/Lemmatization.h"

#include <set>
#include <string>
#include <vector>

#include <cstdio>

#include "tmt/common/Common.h"
#include "tmt/common/Files.h"
#include "tmt/strings/StringUtils.h"
#include "tmt/lemmatization/FSADictionary.h"

#include<iostream>

using namespace std;
using namespace TMT;

Lemmatization::Lemmatization() : stopwordMSD("X"), notfoundMSD("F")
{
}

void Lemmatization::loadWordSet(const string &path, set<string> *words)
{
	CHECK(words);
	words->clear();

	vector<string> lines;
	{
		FILE *fp = tmtfopen(path.c_str(), "rb");
		string fileContents;
		ReadTextFromFile(fp, &fileContents);
		fclose(fp);
		SplitStringUsing(fileContents, "\r\n", &lines);
	}

	for (int i = 0; i < lines.size(); ++i)
		if (!lines[i].empty())
		{
			string cur;

			UTF8Lowercase(lines[i], &cur);

			size_t pos = cur.find_first_not_of(" \t");
			if (pos != string::npos)
				cur = cur.substr(pos);

			pos = cur.find(';');
			if (pos != string::npos)
				cur = cur.substr(0, pos);

			pos = cur.find_first_of(" \t\r\n");
			if (pos != string::npos)
				cur = cur.substr(0, pos);

			if (!cur.empty())
				words->insert(cur);
		}
}

void Lemmatization::saveWordSet(set<string> &wordSet, const string &path)
{
	string contents;
	for(set<string>::iterator it = wordSet.begin(); it != wordSet.end(); ++it)
	{
		contents += *it;
		contents += + '\n';
	}
	FILE *fp = tmtfopen(path.c_str(), "wb");
	fwrite(contents.c_str(), 1, contents.size(), fp);
	fclose(fp);
}

Lemmatization::~Lemmatization()
{
}

Lemmatization::WordData Lemmatization::fillWordData(string wordForm) const
{
	WordData rez;

	if (isStopword(wordForm))
	{
		rez.type = WTStopword;
		rez.derNorms.push_back(wordForm);
		rez.infNorms.push_back(wordForm);
		rez.lemmas.resize(1);
		rez.lemmas[0].lemma = wordForm;
		rez.lemmas[0].msd.push_back(stopwordMSD);

		return rez;
	}
	if (isIgnoreword(wordForm))
		rez.type = WTIgnoreword;
	else
		rez.type = WTNormal;

	rez.infNorms = getInfNorms(wordForm);
	rez.derNorms = getDerNorms(wordForm);

	vector<string> lemmas(getLemmas(wordForm));
	rez.lemmas.resize(lemmas.size());
	for(int i = 0; i < lemmas.size(); ++i)
	{
		rez.lemmas[i].lemma = lemmas[i];
		rez.lemmas[i].msd = getMSDs(lemmas[i], wordForm);
	}

	if (rez.lemmas.empty())
	{
		rez.lemmas.resize(1);
		rez.lemmas[0].lemma = wordForm;
		rez.lemmas[0].msd.push_back(notfoundMSD);
	}

	return rez;
}

string Lemmatization::getFirstLemma(const string &wordForm, bool forced) const
{
	vector<string> lemmas(getLemmas(wordForm));
	if (!lemmas.empty())
		return lemmas[0];
	if (forced)
		return wordForm;
	return string();
}

string Lemmatization::getConcatenatedMSDs(const string &lemma,
										  const string &wordForm,
										  char concatenator) const
{
	vector<string> tmp(getMSDs(lemma, wordForm));
	string rez;
	char tmpconcat[2] = { concatenator, 0 };
	JoinStrings(tmp, tmpconcat, &rez);
	return rez;
}
