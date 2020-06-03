#include "HomographyCtypes.h"
#include "Estimate.h"

//_declspec(dllexport)
DLL_PUBLIC
Structure *
HomographyCtypes(const double *x1, const double *y1,
				const double *x2, const double *y2,
				const size_t inputNum, const size_t trial)
{
	// create a general input format
	InputParam input;
	const double *inputPtr[4] = { x1, y1, x2, y2 };
	input.inputPtrArray = inputPtr;
	input.l = 4;
	input.m = 9;
	input.n = inputNum;
	input.me = 4;
	input.zeta = 2;
	input.alpha = 0;
	input.trial = trial;

	// compute in Estimate code
	StructureList estStructure = Estimate(input);

	// allocate Ctypes Structure
	Structure *ctypesStructure = new Structure[estStructure.size() + 1]();
	size_t res_i = 0;
	for (auto i = estStructure.begin(); i != estStructure.end(); ++i) {

		ctypesStructure[res_i].StructureStrength = std::get<0>(*i);
		ctypesStructure[res_i].StructureSize = std::get<1>(*i);
		ctypesStructure[res_i].StructureScale = std::get<2>(*i);

		ctypesStructure[res_i].StructureIndex = new size_t[std::get<3>(*i).size()];
		size_t res_j = 0;
		for (auto j = std::get<3>(*i).begin(); j != std::get<3>(*i).end(); ++j) {
			ctypesStructure[res_i].StructureIndex[res_j] = *j;
			res_j++;
		}

		ctypesStructure[res_i].StructureTLS = new double[std::get<4>(*i).size()];
		res_j = 0;
		for (auto j = std::get<4>(*i).begin(); j != std::get<4>(*i).end(); ++j) {
			ctypesStructure[res_i].StructureTLS[res_j] = *j;
			res_j++;
		}
		res_i++;
	}
	
	return ctypesStructure;
}

//_declspec(dllexport)
DLL_PUBLIC
void FreeMemory(Structure *ctypesStructure)
{	
	int i = 0;
	while (1) {
		delete[] ctypesStructure[i].StructureIndex;
		delete[] ctypesStructure[i].StructureTLS;
		if (ctypesStructure[i].StructureSize == 0)
			break;		
		i++;
	}
	delete[] ctypesStructure;	
}
