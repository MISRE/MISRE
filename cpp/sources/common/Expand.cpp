#include "Expand.h"

void Expand(PAIR_DOUBLE_SIZE_T *seqM, size_t seqMSize, size_t initialSize, double &scale, V_SIZE_T &expandedSet)
{
	size_t bestCountInlier = initialSize;
	bool expandStart = false;

	size_t startRatio = (size_t)((double)initialSize / seqMSize * 100);
	for (auto multSample = startRatio; multSample < 99; multSample++) {

		size_t startSize = (size_t)((0.01 * multSample) * seqMSize);
		size_t countInlier = startSize > initialSize ? startSize : initialSize;

		int expCriteria = 2;
		double begin = seqM[countInlier].first;
		while (countInlier < seqMSize - 1) {
			double search = expCriteria * begin;
			double exp_count = (1 + 0.5 / (expCriteria - 1)) * countInlier;

			size_t tempCountInlier = countInlier;

			while (countInlier < seqMSize - 1) {
				if (seqM[countInlier].first > search)
					break;
				countInlier++;
			}
			if (countInlier < exp_count) {
				countInlier = tempCountInlier;
				break;
			}
			expCriteria++;
		}

		if (expCriteria > 2)
			expandStart = true;
		if (expCriteria == 2 && expandStart)
			break;
		if (countInlier > bestCountInlier && expandStart)
			bestCountInlier = countInlier;
	}

	// scale
	scale = seqM[bestCountInlier].first;

	// collect indices of expanded set 	
	for (auto eleIdx = 0; eleIdx < bestCountInlier; eleIdx++) {
		expandedSet.push_back(seqM[eleIdx].second);
	}
	return;
}
