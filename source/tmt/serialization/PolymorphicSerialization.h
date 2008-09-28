#ifndef TMT__SERIALIZATION__POLYMORPHIC_SERIALIZATION_H
#define TMT__SERIALIZATION__POLYMORPHIC_SERIALIZATION_H

#include "tmt/serialization/private/ClassTraits.h"

#if !TMT_SERIALIZATION_TEXT_STREAM_ARCHIVE && \
	!TMT_SERIALIZATION_BINARY_FILE_ARCHIVE && \
	!TMT_SERIALIZATION_BINARY_STREAM_ARCHIVE

#define TMT_SERIALIZATION_REGISTER(CLASS) 
#define TMT_SERIALIZATION_REGISTER_ABSTRACT(CLASS) 

#else
#include "tmt/serialization/private/Common.h"

namespace TMT
{
namespace Serialization
{
namespace Implementation
{
template<class Archive, class Derived>
struct ArchiveSaver : AbstractArchiveSaver<Archive>
{
	void save(Archive &ar, void *obj) const
	{
		Derived &derived = *static_cast<Derived *>(obj);
		ar << derived;
	}
};

template<class Archive, class Derived>
struct ArchiveSaverAdder
{
	explicit ArchiveSaverAdder(const char *name)
	{
		static ArchiveSaver<Archive, Derived> abstractSaveHelper;
		ArchiveSaversMap::getMap<Archive>()[typeid(Derived).name()] =
			std::make_pair(&abstractSaveHelper, name);
	}
};

template<class Archive, class Derived>
struct ArchiveLoader : AbstractArchiveLoader<Archive>
{
	void *load(Archive &ar) const
	{
		Derived *derived = new Derived;
		ar >> *derived;
		return derived;
	}
};

template<class Archive, class Derived>
struct ArchiveLoaderAdder
{
	explicit ArchiveLoaderAdder(const char *name)
	{
		static ArchiveLoader<Archive, Derived> abstractLoadHelper;
		ArchiveLoadersMap::getMap<Archive>()[name] = &abstractLoadHelper;
	}
};

template<>
struct SerializationObjectLoader<true>
{
	template<class ARCHIVEINPUTBASE, class ARCHIVEBASE, class BASE>
	static void loadObject(ARCHIVEINPUTBASE &archiveInputBase,
						   ARCHIVEBASE &archiveBase,
						   hash_map<int, void *> &pointers,
						   int curPtrVal,
						   hash_map<int, string> &classNamesMapping,
						   BASE *&baseObject)
	{
		int classTypeId;
		archiveInputBase & classTypeId;
		if (classTypeId == classNamesMapping.size())
		{
			string className;
			archiveBase.readRawString(archiveInputBase, className);
			classNamesMapping.insert(std::make_pair(classTypeId, className));
		}
		else if (classTypeId > static_cast<int>(classNamesMapping.size()))
			throw std::runtime_error("Broken archive: invalid class id.");

		typename hash_map<string,
						  AbstractArchiveLoader<ARCHIVEINPUTBASE> *
						  >::iterator hmit;
		hash_map<string, AbstractArchiveLoader<ARCHIVEINPUTBASE> *> &hm =
			ArchiveLoadersMap::getMap<ARCHIVEINPUTBASE>();

		{
			hash_map<int, string>::iterator it =
				classNamesMapping.find(classTypeId);
			if (it == classNamesMapping.end())
				throw std::runtime_error("Broken archive: invalid class id.");

			hmit = hm.find(it->second);
			if (hmit == hm.end())
				throw std::runtime_error("Class '" + it->second + "' not registered.");
		}

		pointers[curPtrVal] = baseObject = static_cast<BASE *>(hmit->second->load(archiveInputBase));
	}
};

namespace
{

template<class T>
struct ArchiveSaverRegistrator
{
	explicit ArchiveSaverRegistrator(const char *name)
	{
#if TMT_SERIALIZATION_TEXT_STREAM_ARCHIVE
		ArchiveSaverAdder<OTextStreamArchive::ArchiveBase, T> a1(name);
#endif
#if TMT_SERIALIZATION_BINARY_FILE_ARCHIVE
		ArchiveSaverAdder<OBinaryFILEArchive::ArchiveBase, T> a2(name);
#endif
#if TMT_SERIALIZATION_BINARY_STREAM_ARCHIVE
		ArchiveSaverAdder<OBinaryStreamArchive::ArchiveBase, T> a3(name);
#endif
	}
	static const ArchiveSaverRegistrator<T> init;
};

template<class T>
struct ArchiveLoaderRegistrator
{
	explicit ArchiveLoaderRegistrator(const char *name)
	{
#if TMT_SERIALIZATION_TEXT_STREAM_ARCHIVE
		ArchiveLoaderAdder<ITextStreamArchive::ArchiveBase, T> a1(name);
#endif
#if TMT_SERIALIZATION_BINARY_FILE_ARCHIVE
		ArchiveLoaderAdder<IBinaryFILEArchive::ArchiveBase, T> a2(name);
#endif
#if TMT_SERIALIZATION_BINARY_STREAM_ARCHIVE
		ArchiveLoaderAdder<IBinaryStreamArchive::ArchiveBase, T> a3(name);
#endif
	}
	static const ArchiveLoaderRegistrator<T> init;
};

}
}
}
}

#define TMT_SERIALIZATION_REGISTER(CLASS) \
TMT_SERIALIZATION_POLYMORPHIC(CLASS) \
namespace TMT \
{ \
namespace Serialization \
{ \
namespace Implementation\
{ \
namespace \
{ \
template<> \
const ArchiveSaverRegistrator<CLASS> ArchiveSaverRegistrator<CLASS>::init(#CLASS); \
template<> \
const ArchiveLoaderRegistrator<CLASS> ArchiveLoaderRegistrator<CLASS>::init(#CLASS); \
} \
} \
} \
}

#define TMT_SERIALIZATION_REGISTER_ABSTRACT(CLASS) \
TMT_SERIALIZATION_POLYMORPHIC(CLASS) \
namespace TMT \
{ \
namespace Serialization \
{ \
namespace Implementation \
{ \
namespace \
{ \
template<> \
const ArchiveSaverRegistrator<CLASS> ArchiveSaverRegistrator<CLASS>::init(#CLASS); \
} \
} \
} \
}

#endif
#define TMT_POLYMORPHIC_SERIALIZATION 1

#endif
