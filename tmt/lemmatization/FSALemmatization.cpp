#include "tmt/common/Common.h"
#include "tmt/lemmatization/FSALemmatization.h"
#include "tmt/lemmatization/FSADictionary.h"

using namespace TMT;
using namespace std;

/*
word-form>lemma
lemma<word-form
dernorm:lemma
infnorm;lemma
*/

static const char lemmaSeparator = '>';
static const char wordFormSeparator = '<';
static const char derNormSeparator = ':';
static const char infNormSeparator = ';';

class FSAInfo
{
	const FSADictionary *const dict;
	FSADictionary::Transition *const tr;
	const int nTransitions;
	const string &origWord;

	struct MSDAccess
	{
		string operator()
				(const FSADictionary *dict,
				FSADictionary::Transition *tr,
				int nTransitions,
				FSADictionary::EmptyStruct userData) const;
	};

public:
	FSAInfo(const FSADictionary *dict,
			  FSADictionary::Transition *tr,
			  int nTransitions,
			  const string &origWord);

	string info() const;

	typedef FSADictionary::DictionaryIterator<
				FSADictionary::WaitFinalTransition,
				string,
				MSDAccess,
				FSADictionary::EmptyStruct> iterator;

	iterator begin() const;
	iterator end() const;
};

class FSAInfos
{
	const FSADictionary *const dict;
	string origWord;
	FSADictionary::Transition trans;

	struct FSAInfoAccess
	{
		FSAInfo operator() (
					const FSADictionary *dict,
					FSADictionary::Transition *tr,
					int nTransitions,
					const string *origWord) const;
	};

public:
	FSAInfos(const string &origWord_);

	FSAInfos(const string &origWord_, 
			 const FSADictionary *const dict_,
			 FSADictionary::Transition trans_);

	typedef FSADictionary::DictionaryIterator<
					FSADictionary::WaitCharacter<' '>,
					FSAInfo,
					FSAInfoAccess,
					const string *> iterator;

	iterator begin() const;
	iterator end() const;
};

inline FSAInfo::FSAInfo(const FSADictionary *dict_,
					FSADictionary::Transition *tr_,
					int nTransitions_,
					const string &origWord_) :
	dict(dict_),
	tr(tr_),
	nTransitions(nTransitions_),
	origWord(origWord_)
{
}

inline FSAInfo::iterator FSAInfo::end() const
{
	return iterator();
}

inline FSAInfo FSAInfos::FSAInfoAccess::operator() (
					const FSADictionary *dict,
					FSADictionary::Transition *tr,
					int nTransitions,
					const string *origWord) const
{
	return FSAInfo(dict, tr, nTransitions, *origWord);
}

inline FSAInfos::FSAInfos(const string &origWord_) :
					dict(NULL), origWord(origWord_)
{
}

inline FSAInfos::FSAInfos(const string &origWord_,
					  const FSADictionary *const dict_,
					  FSADictionary::Transition trans_) :
	dict(dict_), origWord(origWord_), trans(trans_)
{
}

inline FSAInfos::iterator FSAInfos::end() const
{
	return iterator();
}

string FSAInfo::MSDAccess::operator()
				(const FSADictionary *dict,
				FSADictionary::Transition *tr,
				int nTransitions,
				FSADictionary::EmptyStruct userData) const
{
	string rez;
	rez.resize(nTransitions);
	for (int i = 0; i < nTransitions; ++i)
		rez[i] = tr[i].character();
	return rez;
}

string FSAInfo::info() const
{
	int i = tr[0].character() - 'A';
	int j = tr[1].character() - 'A';
	int k = tr[2].character() - 'A';
	int cn;
	string rez;
	rez.reserve(static_cast<int>(origWord.size()) - i - j + nTransitions - 4);
	for (cn = 0; cn < k; ++cn)
		rez += origWord[cn];
	for (cn = k + j; cn < static_cast<int>(origWord.size()) - i; ++cn)
		rez += origWord[cn];
	for (cn = 3; cn < nTransitions - 1; ++cn)
		rez += tr[cn].character();

	return rez;
}

FSAInfo::iterator FSAInfo::begin() const
{
	FSADictionary::Transition trans(dict->followTransition(tr[nTransitions - 1]));
	iterator it(iterator(dict, trans, FSADictionary::EmptyStruct()));
	if (!trans.toFinalState())
		++it;
	return it;
}

FSAInfos::iterator FSAInfos::begin() const
{
	if (!dict)
		return iterator();

	iterator it(dict, trans, &origWord);

	return ++it;
}

static FSAInfos getInfos(const FSADictionary &dict, const string &s, char c)
{
	FSADictionary::Transition trans(dict.initialTransition());

	// Find out does dict have an entry with prefix s.
	if (!(trans = dict.followPath(trans, s)) ||
	// It does. Now check whether s is a word or just a prefix.
		!(trans = trans.findTransitionLabeled(c)))
		// s is just a prefix.
		return FSAInfos(s);

	// otherwise, s is a word.
	return FSAInfos(s, &dict, dict.followTransition(trans));
}

FSALemmatization::FSALemmatization() : dict(0)
{
}

FSALemmatization::FSALemmatization(const string &path)
{
	dict = new FSADictionary(path);
	CHECK(dict);
}

FSALemmatization::~FSALemmatization()
{
	delete dict;
}

bool FSALemmatization::containsLW(const string &word, char c) const
{
	FSADictionary::Transition trans(dict->initialTransition());

	return (trans = dict->followPath(trans, word)) &&
			trans.findTransitionLabeled(c);
}

bool FSALemmatization::containsLemma(const string &lemma) const
{
	return containsLW(lemma, wordFormSeparator);
}

bool FSALemmatization::containsWordForm(const string &wordForm) const
{
	return containsLW(wordForm, lemmaSeparator);
}

string FSALemmatization::getValue(const string &key, const string &msd, char separator) const
{
	FSAInfos values(getInfos(*dict, key, separator));

	for (FSAInfos::iterator it = values.begin(); it != values.end(); ++it)
		for (FSAInfo::iterator msdIt = (*it).begin(); msdIt != (*it).end(); ++msdIt)
			if (*msdIt == msd)
				return (*it).info();

	return string();
}

string FSALemmatization::getWordForm(const string &lemma, const string &msd) const
{
	return getValue(lemma, msd, wordFormSeparator);
}

string FSALemmatization::getLemma(const string &wordForm, const string &msd) const
{
	return getValue(wordForm, msd, lemmaSeparator);
}

string FSALemmatization::getFirstLemma(const string &wordForm, bool forced) const
{
	FSAInfos values(getInfos(*dict, wordForm, lemmaSeparator));
	FSAInfos::iterator it = values.begin();
	if (it != values.end())
		return (*it).info();
	if (forced)
		return wordForm;
	return string();
}

vector<string> FSALemmatization::getValues(const string &key, char separator) const
{
	FSAInfos values(getInfos(*dict, key, separator));
	vector<string> rez;

	for (FSAInfos::iterator it = values.begin(); it != values.end(); ++it)
		rez.push_back((*it).info());

	return rez;
}

vector<string> FSALemmatization::getWordForms(const string &lemma) const
{
	return getValues(lemma, wordFormSeparator);
}

vector<string> FSALemmatization::getLemmas(const string &wordForm) const
{
	return getValues(wordForm, lemmaSeparator);
}

vector<string> FSALemmatization::getMSDs(const string &lemma, const string &wordForm) const
{
	vector<string> rez;
	FSAInfos lemmas(getInfos(*dict, wordForm, lemmaSeparator));

	for (FSAInfos::iterator it = lemmas.begin(); it != lemmas.end(); ++it)
		if ((*it).info() == lemma)
			for (FSAInfo::iterator msdIt = (*it).begin(); msdIt != (*it).end(); ++msdIt)
				rez.push_back(*msdIt);

	return rez;
}

string FSALemmatization::getConcatenatedMSDs(const string &lemma, const string &wordForm, char concatenator) const
{
	string rez;
	FSAInfos lemmas(getInfos(*dict, wordForm, lemmaSeparator));

	for (FSAInfos::iterator it = lemmas.begin(); it != lemmas.end(); ++it)
		if ((*it).info() == lemma)
			for (FSAInfo::iterator msdIt = (*it).begin(); msdIt != (*it).end(); ++msdIt)
			{
				if (!rez.empty())
					rez += concatenator;
				rez += *msdIt;
			}

	return rez;
}

vector<string> FSALemmatization::getDerNorms(const string &wordForm) const
{
	return getValues(wordForm, derNormSeparator);
}

vector<string> FSALemmatization::getInfNorms(const string &wordForm) const
{
	return getValues(wordForm, infNormSeparator);
}
