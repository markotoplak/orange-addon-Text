#ifndef TMT__LEMMATIZATION__FSA_LEMMATIZATION_H
#define TMT__LEMMATIZATION__FSA_LEMMATIZATION_H

#include "tmt/lemmatization/Lemmatization.h"
#include "tmt/lemmatization/FSADictionary.h"

namespace TMT
{

/// Dictionary lemmatization.
/** Class \c FSALemmatization describes dictionary lemmatization.
	It loads dictionary containing triplets (lemma, word form, msd) and (word form, lemma, msd).
	It is not posibble to add, delete or modify any triplet during runtime.

See also \c Lemmatization and \c NOPLemmatization.

\attention
Lemmatization interface assumes all words are in lowercase.
It is your responsibility to convert all words to lowercase prior to calling lemmatization functions.
You can use utilites provided in \c StringUtils.
*/
class FSALemmatization : public Lemmatization
{
	FSADictionary *dict;
	bool containsLW(const string &word, char c) const;
	string getValue(const string &key, const string &msd, char separator) const;
	vector<string> getValues(const string &key, char separator) const;
public:
	/// Inits class with dictionary from file \c path
	/** Dictionary described in file located at \c path is based on class \c FSADictionary.
	*/
	FSALemmatization();
	explicit FSALemmatization(const string &path);
	~FSALemmatization();

	bool containsLemma(const string &lemma) const;
	bool containsWordForm(const string &wordForm) const;

	string getWordForm(const string &lemma, const string &msd) const;
	string getLemma(const string &wordForm, const string &msd) const;
	string getFirstLemma(const string &wordForm, bool forced) const;

	vector<string> getWordForms(const string &lemma) const;
	vector<string> getLemmas(const string &wordForm) const;

	vector<string> getMSDs(const string &lemma, const string &wordForm) const;
	string getConcatenatedMSDs(const string &lemma, const string &wordForm,
							   char concatenator) const;

	vector<string> getDerNorms(const string &wordForm) const;
	vector<string> getInfNorms(const string &wordForm) const;

public:
	template<class T>
	void serialize(T &x)
	{
		Lemmatization::serialize(x);
		x & dict;
	}
};

}

TMT_SERIALIZATION_REGISTER(TMT::FSALemmatization)

#endif
