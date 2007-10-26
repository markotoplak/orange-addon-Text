%module(docstring="Interface to orange text functions.") orngTextWrapper
%include "std_string.i"
%include "std_vector.i"
%{
#include "orngTextWrapper/Wrapper.h"
%}
%include "exception.i"

%template(VectorStr) std::vector<std::string>;

%exception {
  try {
    $action
  } catch (const std::exception &e) {
    SWIG_exception(SWIG_RuntimeError, e.what());
  }
}

namespace TMT
{
	class Lemmatization;
};
class RdrLemmatizer;

class baseLemmatizer
{
public:
	virtual ~baseLemmatizer();

	virtual std::string getLemma(const char *s) const = 0;
	std::string lemmatizeText(const char *s) const;
protected:
};

class lemmatizer : public baseLemmatizer
{
public:
	explicit lemmatizer(const char *path);
	~lemmatizer();

	std::string getLemma(const char *s) const;
private:
	TMT::Lemmatization *lem;
};

class lemmagen : public baseLemmatizer
{
public:
	explicit lemmagen(const char *path);
	~lemmagen();

	std::string getLemma(const char *s) const;
private:
	RdrLemmatizer *lem;
};

class porter : public baseLemmatizer
{
public:
	std::string getLemma(const char *s) const;
};

std::vector<std::string> tokenizeNonWords(const char *text);
std::string removeWords(const char *text, const std::vector<std::string> &words);
