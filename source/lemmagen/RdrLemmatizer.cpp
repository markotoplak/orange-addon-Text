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
#include "RdrLemmatizer.h"
#include <cstdio>
#include <stdexcept>
//-------------------------------------------------------------------------------------------
//helper macros for nicer code and faster execution
#if AddrLen == 3
	#define GETDWORD(type, wVar, wAddr) \
				type wVar = *((dword*) &abData[wAddr]) & 0x00FFFFF
#else
	#define GETDWORD(type, wVar, wAddr) \
				type wVar = *((dword *) &abData[wAddr]) 
#endif

#define GETBYTEMOVE(type, bByte, iSize) \
			type bByte = abData[iAddr]; \
			iAddr += iSize

#define GETDWORDMOVE(type, wVar, iSize) \
			GETDWORD(type, wVar, iAddr);  \
			iAddr += iSize

#define GETSTRINGMOVE(type, acString, iSize) \
			type acString = new char[iSize+1]; \
			strncpy(acString, (char*) &abData[iAddr], iSize); \
			acString[iSize] = NULL; \
			iAddr += iSize

//-------------------------------------------------------------------------------------------
//constructor
RdrLemmatizer::RdrLemmatizer() {
	this->abData = (byte*) abDataStatic;
	this->iDataLen = iDataLenStatic;
}

//-------------------------------------------------------------------------------------------
//destructor
RdrLemmatizer::~RdrLemmatizer() {
	if (this->abData != (byte*) abDataStatic)
		delete[] abData;
}

//-------------------------------------------------------------------------------------------
//lematizes word according to this data
char *RdrLemmatizer::Lemmatize(const char *acWord, char *acOutBuffer) const{
	byte bWordLen = strlen(acWord);

	dword iAddr = DataStart;
	dword iParentAddr = DataStart;
	dword iTmpAddr;
	char bLookChar = bWordLen;
	byte bType = abData[iAddr];

	while(true) {
		iTmpAddr = iAddr+FlagLen+AddrLen;
				
		//check if additional characters match
		if ((bType & BitAddChar) == BitAddChar) {
			byte bNewSufxLen = abData[iTmpAddr];
			iTmpAddr += LenSpecLen;

			bLookChar -= bNewSufxLen;

			//test additional chars if ok
			if (bLookChar>=0)
				do bNewSufxLen--;
				while (bNewSufxLen!=255 && abData[iTmpAddr+bNewSufxLen] == (byte) acWord[bLookChar+bNewSufxLen]);

			//wrong node, take parents rule
			if (bNewSufxLen!=255) {	iAddr = iParentAddr; break; } 

			//right node, but we are at the end (there will be no new loop) finish by returning this rule
			if ((bType & ~BitEntireWr) == TypeLeafAC) break;

			//right node and we need to go on with subnodes (it si probably type TypeIntrAC )
			//set iTmpAddr to start of hashtable
			iTmpAddr += abData[iTmpAddr-LenSpecLen];
		} 

		//move lookup char back
		bLookChar--;
		//check if we are still inside the word (bLookChar==0 when at the begining of word)
		if (bLookChar<0) {
			//this means that we are just one character in front of the word so we must look for entireword entries
			if((bType & BitInternal) == BitInternal) {
				//go to the hashtable position 0(NULL) and look idf address is not NULL
				iTmpAddr += ModLen;
				byte bChar = abData[iTmpAddr];
				GETDWORD(,iTmpAddr,iTmpAddr+CharLen);
				if (bChar == NULL && iTmpAddr!=NULL) {
					//we have a candidate for entireword, redirect addresses
					iParentAddr = iAddr;
					iAddr = iTmpAddr;
					bType = abData[iAddr];
					//increase lookchar (because we actualy eat one character)
					bLookChar++;
				}
			}
			break;
		}
		
		//find best node in hash table
		if((bType & BitInternal) == BitInternal) {
			byte bMod = abData[iTmpAddr];
			byte bChar = acWord[bLookChar];

			iTmpAddr += ModLen + (bChar%bMod)*(AddrLen+CharLen); 

			iTmpAddr = abData[iTmpAddr] == bChar ? iTmpAddr + CharLen : iAddr + FlagLen;

			iParentAddr = iAddr;
			GETDWORD(,iAddr, iTmpAddr);
			bType = abData[iAddr];

			if ((bType & ~BitEntireWr) == TypeRule) break;
		}
	}
	//if this is entire-word node, and we are not at the begining of word it's wrong node - take parents
	if((bType & BitEntireWr) == BitEntireWr && bLookChar!=0) {
		iAddr = iParentAddr;
		bType = abData[iAddr];
	}

	//search ended before we came to te node of type rule but current node is OK so find it's rule node
	if((bType & ~BitEntireWr) != TypeRule)  GETDWORD( ,iAddr, iAddr+FlagLen);
	
	//we have (100%) node of type rule for lemmatization - now it's straight forward to lemmatize
	//read out rule
	iTmpAddr = iAddr + FlagLen;
	byte iFromLen = abData[iTmpAddr];
	iTmpAddr += LenSpecLen;
	byte iToLen = abData[iTmpAddr];
	iTmpAddr += LenSpecLen;

	//prepare output buffer
	byte iStemLen = bWordLen - iFromLen;
	char *acReturn = acOutBuffer == NULL ? new char[iStemLen + iToLen + 1] : acOutBuffer;
	
	//do actual lematirazion using given rule
	memcpy(acReturn, acWord, iStemLen);
	memcpy(&acReturn[iStemLen], &abData[iTmpAddr], iToLen);
	acReturn[iStemLen + iToLen] = NULL;
	
	return acReturn;
}


/*  OLD VERSION
char *RdrLemmatizer::Lemmatize(const char *acWord, char *acOutBuffer) const{
	byte bWordLen = strlen(acWord);

	dword iAddr = DataStart;
	dword iParentAddr = DataStart;
	dword iTmpAddr;
	char bLookChar = bWordLen;
	byte bType = abData[iAddr];

	while(true) {
		iTmpAddr = iAddr+FlagLen+AddrLen;
				
		//check if additional characters match
		if ((bType & BitAddChar) == BitAddChar) {
			byte bNewSufxLen = abData[iTmpAddr];
			iTmpAddr += LenSpecLen;

			bLookChar -= bNewSufxLen;

			//test additional chars if ok
			if (bLookChar>=0)
				do bNewSufxLen--;
				while (bNewSufxLen!=255 && abData[iTmpAddr+bNewSufxLen] == (byte) acWord[bLookChar+bNewSufxLen]);

			//wrong node, take parents rule
			if (bNewSufxLen!=255) {	iAddr = iParentAddr; break; } 

			//right node, but we are at the end (there will be no new loop) finish by returning this rule
			if (bType == TypeLeafAC) break;

			//right node and we need to go on with subnodes
			iTmpAddr += abData[iTmpAddr-LenSpecLen];
		} 

		//move lookup char back
		bLookChar--;
		if (bLookChar<0) break;
		
		//find best node in hash table
		if((bType & BitInternal) == BitInternal) {
			byte bMod = abData[iTmpAddr];
			byte bChar = acWord[bLookChar];

			iTmpAddr += ModLen + (bChar%bMod)*(AddrLen+CharLen); 

			iTmpAddr = abData[iTmpAddr] == bChar ? iTmpAddr + CharLen : iAddr + FlagLen;

			iParentAddr = iAddr;
			GETDWORD(,iAddr, iTmpAddr);
			bType = abData[iAddr];

			if (bType == TypeRule) break;
		}
	}
	//search ended because we came to the begining of word
	if(bType!=TypeRule)  GETDWORD( ,iAddr, iAddr+FlagLen);
	
	iTmpAddr = iAddr + FlagLen;
	byte iFromLen = abData[iTmpAddr];
	iTmpAddr += LenSpecLen;
	byte iToLen = abData[iTmpAddr];
	iTmpAddr += LenSpecLen;

	//lematizes a word using given rule
	byte iStemLen = bWordLen - iFromLen;
	char *acReturn = acOutBuffer == NULL ? new char[iStemLen + iToLen + 1] : acOutBuffer;
	
	memcpy(acReturn, acWord, iStemLen);
	memcpy(&acReturn[iStemLen], &abData[iTmpAddr], iToLen);
	acReturn[iStemLen + iToLen] = NULL;
	
	return acReturn;
} */


//-------------------------------------------------------------------------------------------
//loads all data needed from binary file
void RdrLemmatizer::LoadBinary(istream &is) {
	iDataLen =0;
	is.read((char*) &iDataLen, 4);
	abData = new byte[iDataLen];
	is.read((char*) abData, iDataLen);
}
//-------------------------------------------------------------------------------------------
//loads all data needed from binary file
void RdrLemmatizer::LoadBinary(const char *acFileName) {
	FILE *fp = fopen(acFileName, "rb");
	if (!fp)
		throw runtime_error("Can't open lemmatization dictionary.");
	fread(&iDataLen, sizeof(int), 1, fp);
	abData = new byte[iDataLen];
	fread(abData, 1, iDataLen, fp);
	fclose(fp);
/*	// commented out because file streams sometimes won't work from python extension.

	ifstream ifs(acFileName, ios_base::in | ios_base::binary);
	if (!ifs)
		throw runtime_error("Can't open file...");
	LoadBinary(ifs);
	ifs.close();
*/
}
