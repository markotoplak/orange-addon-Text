#ifndef TMT__LEMMATIZATION__FSA_DICTIONARY_H
#define TMT__LEMMATIZATION__FSA_DICTIONARY_H

#include "tmt/common/Common.h"

#include "tmt/serialization/PolymorphicSerialization.h"

#include <string>
#include <algorithm>
#include <iterator>
#include <vector>

namespace TMT {
/// A class represing finite state automata dictionaries.
/**
	Using this (low-level) class you can browse and search the dictionary.
	The dictionary structure is not modifiable - no words can be added, deleted or changed.

	\par Dictionary structure
	\n
	First 8 bytes contain identification "FSADict ".\n
	Next 4 bytes contain version information - <tt>00 01 00 00</tt> for this version.\n
	Next 4 bytes contain big-endian integer \b size.\n
	Next \b size bytes contain <b>size</b> / 4 transitions.\n
	<b>k</b>th transition is encoded as big-endian integer \b t.\n
	Bits of \b t: \n
	  - <tt>24-31 - character of transition \b k</tt>
	  - <tt>23 - on if \b k leads to final state </tt>
	  - <tt>22 - on if \b k is a last transition of the state that contains it</tt>
	  - <tt>0-21 - index of first transition of next state.
	  				If the index is 0, then the next state contains no transitions</tt>
	\par
	States are not explicitly encoded - each transition points to next state
	by pointing to that state's list of transitions. Transitions of one state
	are always listed in consecutive order. Last transition in a state is
	flagged. Final states are marked by transition that points to them.
	The first state contains transitions starting from transition with index 0.\n
	\par
	The dictionary can optionally be compressed using gzip.

	See also FSADictionary::Transition.
*/
class FSADictionary
{
	vector<unsigned char> data;
public:
	/// Initializes dictionary by loading file at \a path
	/** \param path a path to file representing fsa dictionary
	*/
	FSADictionary();
	explicit FSADictionary(const string &path);

	class Transition;

	/// Returns the first transition of initial state.
	Transition initialTransition() const;
	/// Returns the first transition of state pointed to by \a t.
	Transition followTransition(const Transition &t) const;
	/// Returns state of FSA after inputting string \a str to FSA that is in state \a start.
	/**
		It can be used to check whether dictionary contains a word.
		For example:
		\code
bool containsWord(const TMT::FSADictionary &d, const string &s)
{
	TMT::FSADictionary::Transition t = d.followPath(s);
	if (!t) return false;
	return t.toFinalState();
}
		\endcode
	*/
	Transition followPath(Transition start, const string &str) const;
	/// Returns state of FSA after inputting string \a str to FSA that is in state \a start.
	/**
		\overload
	*/
	Transition followPath(Transition start, const unsigned char *str) const;
	/// Returns state of FSA after inputting string \a str to FSA that is in state \a start.
	/**
		\overload
	*/
	Transition followPath(Transition start, const char *str) const;

	/// Traverses dictionary starting from state \a cur
	/**
		\param cur initial state
		\param functor user function that is called
		\param userData user data that is sent to user function

		Every transition reachable from transition \a start (including \a start) is visited.
		After the transition is visited, a (null-terminated) string of all transitions' labels
		starting from (and including) transition start is constructed.
		That string, along with current transition and user data sent to user function.
		If user function returns false, no transitions of current state are visited.
		User function should have the following signature:
\code
bool userFunc(const char *visitedLabels,
			   int nVisited,
			   const FSADictionary::Transition &currentTransition,
			   T &userData)
\endcode
		A better option would be supplying an object with operator() overloaded.
\code
struct UserFunc
{
	bool operator() (const char *visitedLabels,
					  int nVisited,
					  const FSADictionary::Transition &currentTransition,
					  T &userData) const;
};
\endcode
		T is data type supplied by template parameter.

		Example:
\code
struct GetWords
{
	bool operator() (const char *str,
					  int nVisited,
					  const TMT::FSADictionary::Transition &trans,
					  std::list<string> &list) const
	{
		if (trans.toFinalState())
			list.push_back(string(str));
		return true;
	}
					  
};

// return a list of words contained in the dictionary
std::list<string> dictionaryWords(const TMT::FSADictionary &dict)
{
	std::list<string> list;
	dict.itemize(dict.initialTransition(), GetWords(), list);
	return list;
}
\endcode
	*/
	int maxDepth;
	template<class F, class T>
	void itemize(Transition cur, F functor, T &userData) const;

	/// A class abstracting FSA dictionary transition
	/**
		This class represents both FSA states and transitions.
		A state is only a collection of transitions, and it doesn't
		contain information whether it is final state - only
		transitions that lead to some state contain information
		whether that state is final or not.
		
		Every state is represented by a single transition <tt>k</tt>.
		It contains transition <tt>k</tt> and all transitions
		following <tt>k</tt> up to (and including) transition that is
		flagged as the last sibling.

		See also FSADictionary.
	*/
	class Transition
	{
		const unsigned char *ptr;
		explicit Transition(const unsigned char *ptr);
		int offset() const;
		friend class FSADictionary;
	public:
		/// Default constructor
		Transition() {}
		/// Returns true if the transition is valid
		operator bool() const;
		/// Returns true if the transition leads to state that is final
		bool toFinalState() const;
		/// Returns true if the transition is last transition of its parent state
		bool lastSibling() const;
		/// Returns true if this is the last transition
		bool lastTransition() const;
		/// Returns sibling transition
		Transition nextSibling() const;
		/// Finds sibling transition after (and including) current transition that is labeled with \a c
		Transition findTransitionLabeled(unsigned char c) const;
		/// Returns this transition's label
		unsigned char character() const;
	};

	/// \cond
	struct EmptyStruct
	{
	};
	/// \endcond
private:
	struct StringAndIteratorAccess;
	class StringAndIterator
	{
		Transition *tr;
		int nTransitions;
		StringAndIterator(Transition *tr, int nTransitions);
	public:
		string getString() const;
		Transition getTransition() const;
		friend struct StringAndIteratorAccess;
	};

	struct StringAndIteratorAccess
	{
		StringAndIterator operator() (const FSADictionary *dict, Transition *tr, int nTransitions, EmptyStruct data) const;
	};

public:
	/// \cond
	struct NeverContinue
	{
		bool operator() (const FSADictionary *dict, Transition *tr, int nTransitions) const;
	};

	struct WaitFinalTransition
	{
		bool operator() (const FSADictionary *dict, Transition *tr, int nTransitions) const;
	};

	template<char c>
	struct WaitCharacter
	{
		bool operator() (const FSADictionary *dict, Transition *tr, int nTransitions) const;
	};

	template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
	class DictionaryIterator : public std::iterator<std::forward_iterator_tag, ReturnType>
	{
		const FSADictionary *dict;
		int nStack;
		FSADictionary::Transition *st;
	public:
		UserData userData;
		DictionaryIterator();
		DictionaryIterator(const DictionaryIterator &b);
		DictionaryIterator(const FSADictionary *dict, FSADictionary::Transition trans, UserData userData);
		~DictionaryIterator();
		const DictionaryIterator &operator = (const DictionaryIterator &b);
		const DictionaryIterator &operator ++ ();
		DictionaryIterator operator ++ (int);
		bool operator == (const DictionaryIterator &b) const;
		bool operator != (const DictionaryIterator &b) const;
		ReturnType operator * () const;
	};

	typedef DictionaryIterator<NeverContinue, StringAndIterator, StringAndIteratorAccess, EmptyStruct> transition_iterator;
	typedef DictionaryIterator<WaitFinalTransition, StringAndIterator, StringAndIteratorAccess, EmptyStruct> word_iterator;
	/// \endcond

	transition_iterator transitions_begin() const;
	transition_iterator transitions_end() const;
	word_iterator words_begin() const;
	word_iterator words_end() const;

public:
	template<class T> void serialize(T &x)
	{
		x & data;
		x & maxDepth;
	}
};


inline FSADictionary::Transition::Transition(const unsigned char *p) : ptr(p)
{
}

inline FSADictionary::Transition::operator bool() const
{
	return !!ptr;
}

inline unsigned char FSADictionary::Transition::character() const
{
	DCHECK(ptr);
	return ptr[0];
}

inline bool FSADictionary::Transition::toFinalState() const
{
	DCHECK(ptr);
	return !!(ptr[1] >> 7);
}

inline bool FSADictionary::Transition::lastSibling() const
{
	DCHECK(ptr);
	return (ptr[1] >> 6) & 1;
}

inline FSADictionary::Transition FSADictionary::Transition::nextSibling() const
{
	DCHECK(ptr);
	return Transition(ptr + 4);
}

inline FSADictionary::Transition FSADictionary::initialTransition() const
{
	return Transition(&data[0]);
}

inline int FSADictionary::Transition::offset() const
{
	DCHECK(ptr);
	return ((ptr[1] & 0x3F) << 16) | (ptr[2] << 8) | ptr[3];
}

inline bool FSADictionary::Transition::lastTransition() const
{
	return !offset();
}

inline FSADictionary::Transition FSADictionary::followTransition(const Transition &t) const
{
	int off = t.offset();
	DCHECK(off >= 0 && off < data.size());
	if (!off)
		return Transition(NULL);
	return Transition(&data[0] + off);
}

inline FSADictionary::Transition FSADictionary::Transition::findTransitionLabeled(unsigned char c) const
{
	DCHECK(*this);
	for (Transition cur = *this;; cur = cur.nextSibling())
	{
		if (cur.character() == c)
			return cur;
		if (cur.lastSibling())
			return Transition(NULL);
	}
}

inline FSADictionary::Transition FSADictionary::followPath(Transition cur, const unsigned char *str) const
{
	DCHECK(cur && str);
	unsigned char c;

	for (; (c = *str++) != 0;)
		if (!(cur = cur.findTransitionLabeled(c)) ||
			!(cur = followTransition(cur)))
			break;

	return cur;
}

inline FSADictionary::Transition FSADictionary::followPath(Transition start, const char *str) const
{
	return followPath(start, reinterpret_cast<const unsigned char *>(str));
}

inline FSADictionary::Transition FSADictionary::followPath(Transition start, const string &str) const
{
	return followPath(start, reinterpret_cast<const unsigned char *>(str.c_str()));
}

inline FSADictionary::StringAndIterator::StringAndIterator(Transition *tr_, int nTransitions_) :
	tr(tr_), nTransitions(nTransitions_)
{
}

inline FSADictionary::Transition FSADictionary::StringAndIterator::getTransition() const
{
	return tr[nTransitions - 1];
}

template<char c>
inline bool FSADictionary::WaitCharacter<c>::operator() (const FSADictionary *dict, Transition *tr, int nTransitions) const
{
	return nTransitions && tr[nTransitions - 1].character() != c;
}

inline FSADictionary::StringAndIterator FSADictionary::StringAndIteratorAccess::operator () (const FSADictionary *dict, Transition *tr, int nTransitions, EmptyStruct data) const
{
	return StringAndIterator(tr, nTransitions);
}

inline bool FSADictionary::WaitFinalTransition::operator() (const FSADictionary *dict, Transition *tr, int nTransitions) const
{
	return nTransitions && !tr[nTransitions - 1].toFinalState();
}

inline bool FSADictionary::NeverContinue::operator() (const FSADictionary *dict, Transition *tr, int nTransitions) const
{
	// don't continue
	return false;
}

inline FSADictionary::transition_iterator FSADictionary::transitions_begin() const
{
	return transition_iterator(this, initialTransition(), EmptyStruct());
}

inline FSADictionary::transition_iterator FSADictionary::transitions_end() const
{
	return transition_iterator();
}

inline FSADictionary::word_iterator FSADictionary::words_begin() const
{
	return word_iterator(this, initialTransition(), EmptyStruct());
}

inline FSADictionary::word_iterator FSADictionary::words_end() const
{
	return word_iterator();
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	DictionaryIterator()
{
	nStack = 0;
	st = NULL;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	DictionaryIterator(const FSADictionary *dict_, FSADictionary::Transition trans, UserData userData_) : dict(dict_), userData(userData_)
{
	st = new FSADictionary::Transition[dict->maxDepth];
	nStack = 0;
	st[nStack++] = trans;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	DictionaryIterator(const DictionaryIterator &b) : dict(b.dict), nStack(b.nStack), userData(b.userData)
{
	if (b.st)
	{
		st = new FSADictionary::Transition[dict->maxDepth];
		std::copy(b.st, b.st + nStack, st);
	}
	else
		st = NULL;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	~DictionaryIterator()
{
	if (st)
		delete[] st;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline const FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData> &
	FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	operator = (const DictionaryIterator &b)
{
	if (this != &b)
	{
		if (st)
			delete[] st;
		nStack = b.nStack;
		dict = b.dict;
		userData = b.userData;
		if (nStack)
		{
			st = new FSADictionary::Transition[dict->maxDepth];
			std::copy(b.st, b.st + nStack, st);
		}
	}

	return *this;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline const FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData> &
	FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	operator ++ ()
{
	do
	{
		FSADictionary::Transition trans = st[nStack - 1];
		FSADictionary::Transition tmp;

		if ((tmp = dict->followTransition(trans)))
			st[nStack++] = tmp;
		else if (!trans.lastSibling())
			st[nStack - 1] = trans.nextSibling();
		else
			for (;;)
			{
				if (!--nStack)
					break;

				trans = st[nStack - 1];
				if (!trans.lastSibling())
				{
					st[nStack - 1] = trans.nextSibling();
					break;
				}
			}
	}
	while (ShouldContinue() (dict, st, nStack));
	return *this;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>
	FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	operator ++ (int)
{
	DictionaryIterator tmp(*this);
	++*this;
	return tmp;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline bool FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	operator == (const FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData> &b) const
{
	if (nStack != b.nStack)
		return false;
	for (int i = nStack - 1; i >= 0; --i)
		if (st[i] != b.st[i])
			return false;
	return true;
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline bool FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	operator != (const DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData> &b) const
{
	return !(*this == b);
}

template<class ShouldContinue, class ReturnType, class AccessOperator, class UserData>
inline ReturnType FSADictionary::DictionaryIterator<ShouldContinue, ReturnType, AccessOperator, UserData>::
	operator * () const
{
	return AccessOperator() (dict, st, nStack, userData);
}

template<class F, class T>
void FSADictionary::itemize(Transition cur, F functor, T &userData) const
{
	if (!cur) return;

	static int itemizeDepth = 0;
	++itemizeDepth;
	static vector<Transition *> vxstack;
	static vector<char *> vstate;
	static vector<char *> vtmpString;
	if (itemizeDepth > static_cast<int>(vxstack.size()))
	{
		static const int maxDictWordLength = 500;
		vxstack.push_back(new Transition[maxDictWordLength]);
		vstate.push_back(new char[maxDictWordLength]);
		vtmpString.push_back(new char[maxDictWordLength]);
	}

	Transition *xstack = vxstack.back();
	char *state = vstate.back();
	char *tmpString = vtmpString.back();
	int d = 0;

	for (;;)
	{
		stateFalse:
		for (;; cur = cur.nextSibling())
		{
			tmpString[d] = cur.character();
			tmpString[d + 1] = 0;

			if (functor(tmpString, d + 1, cur, userData))
			{
				Transition child(followTransition(cur)); 
				if (child)
				{
					xstack[d] = cur;
					state[d] = true;

					++d;
					cur = child;
					goto stateFalse;
				}
			}
			stateTrue:
			if (cur.lastSibling())
				break;
		}
		if (--d < 0)
			break;
		cur = xstack[d];
		if (state[d])
			goto stateTrue;
	}
	--itemizeDepth;
}

}

TMT_SERIALIZATION_REGISTER(TMT::FSADictionary)

#endif
