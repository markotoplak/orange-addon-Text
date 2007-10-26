#ifndef TMT__LEMMATIZATION__STEMMER_H
#define TMT__LEMMATIZATION__STEMMER_H

#include "tmt/common/Common.h"

#include "tmt/serialization/PolymorphicSerialization.h"

namespace TMT
{

/// A stemming interface
/** Classes that implement stemming interface should
	provide only one method - stem.
*/
class Stemmer
{
public:
	/// Returns \p word stem
	virtual string stem(const string &word) const = 0;
	virtual ~Stemmer()
	{
	}

	template<class T>
	void serialize(T &x)
	{
	}
};

}

TMT_SERIALIZATION_REGISTER_ABSTRACT(TMT::Stemmer)

#endif
