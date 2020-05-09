/*	HomographyCtypes.h
This is a wrapper file to 
convert output in Ctypes for Python.

x1, y1, x2, y2 : 2D image pairs
inputNum : total amount of inputs
trial : number of trials.
*/

#ifndef HOMOGRAPHYCTYPES
#define HOMOGRAPHYCTYPES

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
		HomographyCtypes(const double *x1, const double *y1, 
						const double *x2, const double *y2,
						const size_t inputNum, const size_t trial);

	_declspec(dllexport)
		void FreeMemory(Structure *);
}

#endif
