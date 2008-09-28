#ifndef TMT__COMMON__FILES_H
#define TMT__COMMON__FILES_H

#include <cstdio>

#include "tmt/common/Common.h"

namespace TMT
{
	std::FILE *tmtfopen(const char *path, const char *mode);
}
	
#endif
