/******************************************************************************
This file is part of the lemmagen library. It gives support for lemmatization.
Copyright (C) 2006-2007 Matjaz Jursic <matjaz@gmail.com>

The lemmagen library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
******************************************************************************/
#pragma once

#define AllInOneFile

//-------------------------------------------------------------------------------------------
//includes
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>

#ifndef AllInOneFile
	#include "RdrLemmData.h"
#endif

//-------------------------------------------------------------------------------------------
//if data is not loaded from separate file define empty structure
#ifndef RrdLemmData
	#define RrdLemmData
	#define DATA_LEN 8
	#define DATA_TBL {0x0000000000000000}
#endif

//-------------------------------------------------------------------------------------------
//typedefs
typedef unsigned char byte;
typedef unsigned short word;
typedef unsigned int dword;
typedef unsigned long long qword;

//-------------------------------------------------------------------------------------------
//const variables that algorithm depends on
#define AddrLen 4
#define FlagLen 1
#define ModLen 1
#define LenSpecLen 1
#define CharLen 1
#define DataStart 0

#define RoundDataLen 8

#define BitDefault	0x00
#define BitAddChar	0x01
#define BitInternal	0x02

#define TypeRule	(BitDefault)
#define TypeLeafAC	(BitDefault | BitAddChar)
#define TypeIntr	(BitDefault | BitInternal)
#define TypeIntrAC	(BitDefault | BitAddChar | BitInternal)

//-------------------------------------------------------------------------------------------
//main data structure and it's length 
static dword iDataLenStatic = DATA_LEN;
static qword abDataStatic[] = DATA_TBL;

//-------------------------------------------------------------------------------------------
using namespace std;

class RdrLemmatizer{
private:
	byte *abData;
	int iDataLen;

public:
	RdrLemmatizer();
	~RdrLemmatizer();

	char *Lemmatize(const char *acWord, char *acOutBuffer = NULL) const;

	void LoadBinary(const char *acFileName);
	void LoadBinary(istream &is);

};

