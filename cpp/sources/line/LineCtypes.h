/*	LineCtypes.h
This is a wrapper file to 
convert output in Ctypes for Python.

x, y: 2D coordinates
inputNum : total amount of inputs
trial : number of trials.
*/

#ifndef LINECTYPES
#define LINECTYPES

extern "C"
{
	struct Structure // return type of structure
	{
		double StructureStrength;		// strength
		size_t StructureSize;			// size		
		double StructureScale;			// scale
		size_t *StructureIndex;			// Indices
		double *StructureTLS;			// TLS estimate
	};

	_declspec(dllexport)
		Structure *
		LineCtypes(const double *x, const double *y,
						const size_t inputNum, const size_t trial);

	_declspec(dllexport)
		void FreeMemory(Structure *);
}

#endif
