/*	PlaneCtypes.h
This is a wrapper file to 
convert output in Ctypes for Python.

x, y, z: 3D coordinates
inputNum : total amount of inputs
trial : number of trials.
*/

#ifndef PLANECTYPES
#define PLANECTYPES

#include <stddef.h>

// https://gcc.gnu.org/wiki/Visibility
#if defined _WIN32 || defined __CYGWIN__
  #ifdef BUILDING_DLL
    #ifdef __GNUC__
#define DLL_PUBLIC __attribute__ ((dllexport))
    #else
#define DLL_PUBLIC __declspec(dllexport) // Note: actually gcc seems to also supports this syntax.
    #endif
  #else
    #ifdef __GNUC__
#define DLL_PUBLIC __attribute__ ((dllimport))
    #else
#define DLL_PUBLIC __declspec(dllimport) // Note: actually gcc seems to also supports this syntax.
    #endif
  #endif
  #define DLL_LOCAL
#else
  #if __GNUC__ >= 4
#define DLL_PUBLIC __attribute__ ((visibility ("default")))
#define DLL_LOCAL  __attribute__ ((visibility ("hidden")))
  #else
    #define DLL_PUBLIC
    #define DLL_LOCAL
  #endif
#endif

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

        //_declspec(dllexport)
        DLL_PUBLIC
		Structure *
		PlaneCtypes(const double *x, const double *y, const double *z,
						const size_t inputNum, const size_t trial);

        //_declspec(dllexport)
        DLL_PUBLIC
		void FreeMemory(Structure *);
}

#endif
