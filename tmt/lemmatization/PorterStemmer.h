#ifndef TMT__LEMMATIZATION__PORTER_STEMMER_H
#define TMT__LEMMATIZATION__PORTER_STEMMER_H

#include "tmt/common/Common.h"
#include "tmt/lemmatization/Stemmer.h"

namespace TMT
{

/// Wrapper around the Porter's stemming algoritm implementation.
class PorterStemmer : public Stemmer
{
public:
	string stem(const string &word) const;

	template<class T> void serialize(T &x)
	{
		Stemmer::serialize(x);
	}
};

}

TMT_SERIALIZATION_REGISTER(TMT::PorterStemmer)

#endif
