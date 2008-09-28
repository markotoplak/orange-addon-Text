#ifndef TMT__SERIALIZATION__PRIVATE__CLASS_TRAITS_H
#define TMT__SERIALIZATION__PRIVATE__CLASS_TRAITS_H

namespace TMT
{
namespace Serialization
{
/// \cond
namespace Implementation
{
template<class T>
struct SerializationClassIsPolymorphic
{
	static const bool value = false;
};
template<class T>
struct SerializationClassIsPOD
{
	static const bool value = false;
};
template<> struct SerializationClassIsPOD<char>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<unsigned char>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<short>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<unsigned short>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<int>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<unsigned int>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<long>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<unsigned long>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<float>
{
	static const bool value = true;
};
template<> struct SerializationClassIsPOD<double>
{
	static const bool value = true;
};
}
/// \endcond
}
}


#define TMT_SERIALIZATION_POLYMORPHIC(CLASS) \
namespace TMT\
{\
namespace Serialization\
{\
namespace Implementation\
{\
template<> \
struct SerializationClassIsPolymorphic<CLASS> \
{ \
	static const bool value = true; \
};\
}\
}\
}

#define TMT_SERIALIZATION_SET_POD(CLASS) \
namespace TMT\
{\
namespace Serialization\
{\
namespace Implementation\
{\
template<> \
struct SerializationClassIsPOD<CLASS> \
{ \
	static const bool value = true; \
};\
}\
}\
}

#endif
