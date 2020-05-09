#ifndef EXPAND
#define EXPAND

#include "Estimate.h"

typedef std::pair<double, size_t> PAIR_DOUBLE_SIZE_T;

void Expand(PAIR_DOUBLE_SIZE_T *seqM, size_t seqMSize, size_t initialSize, double &scale, V_SIZE_T &expandedSet);

#endif
