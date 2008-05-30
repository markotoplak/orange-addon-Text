#if TMTNOZLIB
#include "tmt/common/Files.h"
#else
#include <zlib.h>
#endif

#include "tmt/common/Common.h"
#include "tmt/lemmatization/FSADictionary.h"

#include <cerrno>
#include <stdexcept>
#include <string>

using namespace std;
using namespace TMT;

struct GetDepth
{
	bool operator() (const char *visitedLabels,
					  int nVisited,
					  const FSADictionary::Transition &currentTransition,
					  int &maxDepth)
	{
		if (nVisited > maxDepth)
			maxDepth = nVisited;
		return true;
	}
};

FSADictionary::FSADictionary() : maxDepth(0)
{
}

FSADictionary::FSADictionary(const string &path)
{
#if TMTNOZLIB
	FILE *fp = tmtfopen(path.c_str(), "rb");
	unsigned char c;
	int size;
	fread(&c, 1, 1, fp); size = c;
	fread(&c, 1, 1, fp); size = (size << 8) | c;
	fread(&c, 1, 1, fp); size = (size << 8) | c;
	fread(&c, 1, 1, fp); size = (size << 8) | c;

	if (size < 0 || size >= (1 << 22) * 4)
	{
		fclose(fp);
		throw runtime_error("Dictionary \"" + string(path) + "\" is corrupt.");
	}

	data = vector<unsigned char>(size);

	if (fread(&data[0], 1, size, fp) < size)
	{
		fclose(fp);
		throw runtime_error("Dictionary \"" + string(path) + "\" is corrupt.");
	}

	fclose(fp);
	maxDepth = 0;
	itemize(initialTransition(), GetDepth(), maxDepth);
#else
	gzFile fp = gzopen(path.c_str(), "rb");

	if (!fp)
	{
		int err;
		const char *msg;

		msg = gzerror(fp, &err);
		if (err == Z_ERRNO)
			throw StdError();
		throw runtime_error(msg);
	}

	unsigned char c;
	int size;
	gzread(fp, &c, 1); size = c;
	gzread(fp, &c, 1); size = (size << 8) | c;
	gzread(fp, &c, 1); size = (size << 8) | c;
	gzread(fp, &c, 1); size = (size << 8) | c;

	if (size < 0 || size >= (1 << 22) * 4)
		throw runtime_error("Dictionary \"" + string(path) + "\" is corrupt.");

	data = vector<unsigned char>(size);

	if (gzread(fp, &data[0], size) < size)
		throw runtime_error("Dictionary \"" + string(path) + "\" is corrupt.");

	gzclose(fp);
	maxDepth = 0;
	itemize(initialTransition(), GetDepth(), maxDepth);
#endif
}

string FSADictionary::StringAndIterator::getString() const
{
	string rez;
	rez.resize(nTransitions);
	for (int i = 0; i < nTransitions; ++i)
		rez[i] = tr[i].character();

	return rez;
}
