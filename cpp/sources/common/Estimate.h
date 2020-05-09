/*	Estimate.h
This file implements the basic algorithm for the estimation. 
For general use, modification on this file is not required.

Function Estimate takes a general form of input parameters, InputParam;
and outputs the result in a cpp list object, StructureList.
*/

#ifndef ESTIMATE
#define ESTIMATE

struct InputParam					// general form of inputs
{
	const double **inputPtrArray;	// array of pointers of input variables
	size_t l;						// number of measurements, l
	size_t m;						// number of carriers in each carrier vector, m
	size_t n;						// total number of input, n
	size_t me;						// size of elemental subset, m_e
	size_t zeta;					// number of carrier vectors, zeta
	size_t alpha;					// whether intercept term alpha exists
	size_t trial;					// number of trials for random sampling, M
};

#include <vector>
typedef std::vector<size_t> V_SIZE_T;
typedef std::vector<double> V_DOUBLE;

#include <tuple>
// strength, size, scale, indices and TLS estimate of a structure
typedef std::tuple<double, size_t, double, V_SIZE_T, V_DOUBLE> StructureTuple;

#include <list> // return type, a list sorted by strengths
typedef std::list<StructureTuple> StructureList;

StructureList Estimate(InputParam &);

#endif
