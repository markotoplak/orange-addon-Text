#ifndef TMT__LEMMATIZATION__LEMMATIZATION_H
#define TMT__LEMMATIZATION__LEMMATIZATION_H

#include "tmt/common/Common.h"
#include "tmt/serialization/PolymorphicSerialization.h"

#include <set>
#include <string>
#include <vector>

namespace TMT
{

/// %Lemmatization interface.
/** Class \c Lemmatization describes lemmatization interface.

See also \c FSALemmatization and \c NOPLemmatization.

\attention
Lemmatization interface assumes all words are in lowercase.
It is your responsibility to convert all words to lowercase prior to calling lemmatization functions.
You can use utilites provided in \c StringUtils.
*/

class Lemmatization
{
	const string stopwordMSD;
	const string notfoundMSD;
protected:
	Lemmatization();
public:
	enum WordType
	{
		WTStopword,
		WTIgnoreword,
		WTNormal
	};

	struct LemmaData
	{
		string lemma;
		vector<string> msd;
	};

	struct WordData
	{
		vector<string> infNorms;
		vector<string> derNorms;
		vector<LemmaData> lemmas;

		WordType type;
	};

	/// A set of stopwords.
	/** You can use Lemmatization::loadWordSet to load it from file.
	*/
	std::set<string> stopwords;

	/// A set of ignorewords.
	/** You can use Lemmatization::loadWordSet to load it from file.
	*/
	std::set<string> ignorewords;

	/// Loads a set of words from \c path.
	/**
		
		Each line should contain at most one word.
		Words must be in lowercase. Everything after ';' is ignored.
		Whitespace is ignored.
	*/
	void loadWordSet(const string &path, std::set<string> *words);
	static void saveWordSet(std::set<string> &wordSet, const string &path);

	virtual ~Lemmatization();

	/// Checks whether \c word is stopword
	bool isStopword(const string &word) const;

	/// Checks whether \c word is ignoreword
	bool isIgnoreword(const string &word) const;

	/// Returns true if lemmatization dictionary contains lemma \c word
	virtual bool containsLemma(const string &word) const = 0;

	/// Returns true if lemmatization dictionary contains word form \c word
	virtual bool containsWordForm(const string &word) const = 0;

	/// Returns word form given \c lemma and \c msd
	/** \param lemma a lemma whose word form we are looking for
		\param msd morphosyntactic descriptor

		If there is no such word form, function returns empty string.
	*/
	virtual string getWordForm(const string &lemma, const string &msd) const = 0;

	/// Returns lemma form given \c wordForm and \c msd
	/** \param wordForm a word form whose lemma we are looking for
		\param msd morphosyntactic descriptor

		If there is no such lemma, function returns empty string.
	*/
	virtual string getLemma(const string &wordForm, const string &msd) const = 0;

	/// Returns all word forms of a given lemma
	virtual vector<string> getWordForms(const string &lemma) const = 0;

	/// Returns first lemma. If there is no lemma returns empty string or wordForm if \c forced is true.
	virtual string getFirstLemma(const string &wordForm, bool forced) const;

	/// Returns all lemmas of a given word form
	virtual vector<string> getLemmas(const string &wordForm) const = 0;

	/// Returns all morphosyntactic descriptors given lemma and word form
	virtual vector<string> getMSDs(const string &lemma, const string &wordForm) const = 0;

	/// Returns all morphosyntactic descriptors given lemma and word form
	/** Morphosyntatic descriptors are concatenated using character \c concatenator.
	*/
	virtual string getConcatenatedMSDs(const string &lemma, const string &wordForm,
									   char concatenator) const;

	/// Returns all derivational norms of \p wordForm
	virtual vector<string> getDerNorms(const string &wordForm) const = 0;

	/// Returns all derivational norms of \p wordForm
	virtual vector<string> getInfNorms(const string &wordForm) const = 0;

	/// Convenience method that returns WordData structure for the given word form
	WordData fillWordData(string wordForm) const;

	template<class T> void serialize(T &x)
	{
		x & stopwords;
		x & ignorewords;
	}
};

inline bool Lemmatization::isStopword(const string &word) const
{
	return stopwords.find(word) != stopwords.end();
}

inline bool Lemmatization::isIgnoreword(const string &word) const
{
	return ignorewords.find(word) != ignorewords.end();
}

}

TMT_SERIALIZATION_REGISTER_ABSTRACT(TMT::Lemmatization)

#endif
