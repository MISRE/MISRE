#include "Estimate.h"
#include "RandomSet.h"
#include "MahaDist.h"
#include "Expand.h"
#include "MeanShiftKDE.h"
#include "Functions.h"
#include <algorithm>

StructureList Estimate(InputParam &input)
{	
	StructureList result; // final result	
	V_SIZE_T remainIndex; // track remaining points
	for (size_t i = 0; i < input.n; i++)
		remainIndex.push_back(i);

	// iterative process
	while (remainIndex.size() > 5 * input.me) {
		size_t initialSize = (size_t)(remainIndex.size() * 0.05);
		if (initialSize < 5 * input.me)
			initialSize = 5 * input.me;

		// prepare Carriers and Jacobians for remaining inputs
		MatrixXd remainCarrier(remainIndex.size() * input.zeta, input.m);
		MatrixXd remainJacobian(remainIndex.size() * input.zeta * input.l, input.m);
		CarrierGen(input, remainIndex, remainCarrier);
		JacobianGen(input, remainIndex, remainJacobian);



		// *********** Step 1 : Scale estimate *************
		// randomly select points for elemental subset
		size_t goodSet = 0;
		double minSumDistance = -1;
		PAIR_DOUBLE_SIZE_T *seqM = new PAIR_DOUBLE_SIZE_T[remainIndex.size()];

		while (goodSet < input.trial) {			

			V_SIZE_T subset;
			RandomSet(remainIndex, input.me, subset);
			
			// compute structure
			VectorXd theta(input.m);
			if (!DLTsolve(input, subset, theta))
				continue;

			// compute distance
			VectorXd MahaDistance(remainIndex.size());
			MahaDist(input, remainCarrier, remainJacobian, theta, MahaDistance);

			// sort distances
			PAIR_DOUBLE_SIZE_T *sort_Distance = new PAIR_DOUBLE_SIZE_T[remainIndex.size()];
			for (auto eleIdx = 0; eleIdx < remainIndex.size(); eleIdx++) {
				sort_Distance[eleIdx].first = MahaDistance(eleIdx);
				sort_Distance[eleIdx].second = remainIndex[eleIdx];
			}			
			std::sort(sort_Distance, sort_Distance + remainIndex.size());			

			// find the minimal sum of distances
			double sumDistance = 0;
			for (auto eleIdx = 0; eleIdx < initialSize; eleIdx++)				
				sumDistance += sort_Distance[eleIdx].first;	
			if (sumDistance < minSumDistance || minSumDistance < 0) {
				minSumDistance = sumDistance;
				memcpy(seqM, sort_Distance, remainIndex.size() * sizeof(PAIR_DOUBLE_SIZE_T));
			}
			delete[] sort_Distance;
			goodSet++;
		}

		// expand
		double scale;
		V_SIZE_T expandedSet;
		Expand(seqM, remainIndex.size(), initialSize, scale, expandedSet);
		delete[] seqM;	


		// *********** Step 2 : Mean shift *************
		// randomly select points for elemental subset
		goodSet = 0;
		double maxMode = 0;
		VectorXd thetaHat(input.m);

		while (goodSet < input.trial / 10) {
			
			V_SIZE_T subset;
			RandomSet(expandedSet, input.me, subset);

			// compute structure
			VectorXd theta(input.m);
			if (!DLTsolve(input, subset, theta))
				continue;

			// mean shift to find mode
			double mode;
			MeanShiftKDE(input, remainCarrier, remainJacobian, scale, theta, mode);
			if (mode > maxMode) {
				maxMode = mode;
				thetaHat = theta;
			}
			goodSet++;
		}

		// Compute Mahalanobis distance corresponds to the maximal mode
		VectorXd MahaDistanceHat(remainIndex.size());
		MahaDist(input, remainCarrier, remainJacobian, thetaHat, MahaDistanceHat);

		// sort distances
		PAIR_DOUBLE_SIZE_T *sort_DistanceHat = new PAIR_DOUBLE_SIZE_T[remainIndex.size()];
		for (auto eleIdx = 0; eleIdx < remainIndex.size(); eleIdx++) {
			sort_DistanceHat[eleIdx].first = MahaDistanceHat(eleIdx);
			sort_DistanceHat[eleIdx].second = remainIndex[eleIdx];
		}
		std::sort(sort_DistanceHat, sort_DistanceHat + remainIndex.size());

		// collect all points that can be attracted as inliers
		PAIR_DOUBLE_SIZE_T dummy;
		dummy.first = scale;
		PAIR_DOUBLE_SIZE_T *inlierBound = std::upper_bound(sort_DistanceHat, sort_DistanceHat + remainIndex.size(), dummy);
		
		while (inlierBound != sort_DistanceHat + remainIndex.size()) {

			double center = inlierBound->first;
			for (auto i = 0; i < 10; i++) {
				size_t totalAmount = 0;
				double totalSumDist = 0;

				PAIR_DOUBLE_SIZE_T dummyLeft, dummyRight;
				dummyLeft.first = center - 0.5 * scale;
				dummyRight.first = center + 0.5 * scale;
				PAIR_DOUBLE_SIZE_T *left = std::lower_bound(sort_DistanceHat, sort_DistanceHat + remainIndex.size(), dummyLeft);
				PAIR_DOUBLE_SIZE_T *right = std::upper_bound(sort_DistanceHat, sort_DistanceHat + remainIndex.size(), dummyRight);
				
				for (auto item = left; item != right; ++item) {					
					totalAmount++;
					totalSumDist += item->first;
				}
				center = totalSumDist / totalAmount;
			}
			if (center > scale)
				break;
			inlierBound++;
		}


		// *********** Step 3 : TLS estimate *************
		V_SIZE_T inlierSet;
		for (auto i = sort_DistanceHat; i != inlierBound; ++i){
			inlierSet.push_back(i->second);
		}
		delete[] sort_DistanceHat;
		std::sort(inlierSet.begin(), inlierSet.end());

		// compute structure
		VectorXd thetaTLS(input.m);
		DLTsolve(input, inlierSet, thetaTLS);
		V_DOUBLE TLSestimate(input.m);
		for (auto i = 0; i < input.m; i++) {
			TLSestimate[i] = thetaTLS(i);
		}

		// prepare Carriers and Jacobians for inliers
		MatrixXd inlierCarrier(inlierSet.size() * input.zeta, input.m);
		MatrixXd inlierJacobian(inlierSet.size() * input.zeta * input.l, input.m);
		CarrierGen(input, inlierSet, inlierCarrier);
		JacobianGen(input, inlierSet, inlierJacobian);

		// compute distance
		VectorXd MahaDistanceTLS(inlierSet.size());
		MahaDist(input, inlierCarrier, inlierJacobian, thetaTLS, MahaDistanceTLS);
		scale = MahaDistanceTLS.col(0).maxCoeff();

		StructureTuple Inlier;
		std::get<0>(Inlier) = inlierSet.size() / scale;		// strength
		std::get<1>(Inlier) = inlierSet.size();				// size
		std::get<2>(Inlier) = scale;						// scale
		std::get<3>(Inlier) = inlierSet;					// index
		std::get<4>(Inlier) = TLSestimate;					// TLS estimate
		result.push_back(Inlier);
		
		// *********** Update remainIndex for next iteration ****************
		V_SIZE_T tempRemain;
		std::set_difference(remainIndex.begin(), remainIndex.end(), inlierSet.begin(), inlierSet.end(),
			std::inserter(tempRemain, tempRemain.begin()));
		remainIndex = tempRemain;
	}
	result.sort(std::greater<StructureTuple>());
	return result;
}

