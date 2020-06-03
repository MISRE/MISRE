#include "Functions.h"
#include "Normalize.h"

#include <Eigen/Dense>
using Eigen::JacobiSVD;

#include <iostream>

void CarrierGen(const InputParam &input, V_SIZE_T &remainIndex, MatrixXd &carrier)
{
	double x, y, z;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];
		z = input.inputPtrArray[2][*i];

		carrier.block(input.zeta * rowIdx, 0, input.zeta, input.m) <<
			x, y, z, 1;

		rowIdx++;
	}
	return;
}

void JacobianGen(const InputParam &input, V_SIZE_T &remainIndex, MatrixXd &jacobian)
{
	double x, y, z;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];
		z = input.inputPtrArray[2][*i];

		jacobian.block(input.l * input.zeta * rowIdx, 0, input.l * input.zeta, input.m) <<
			1, 0, 0, 0,
			0, 1, 0, 0,
			0, 0, 1, 0;

		rowIdx++;
	}
	return;
}

bool DLTsolve(const InputParam &input, V_SIZE_T &subset, VectorXd &theta)
{
	// create homogeneous coords
	MatrixXd point(4, subset.size());
	MatrixXd H(4, 4);

	double x, y, z;
	size_t colIdx = 0;
	for (auto i = subset.begin(); i != subset.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];
		z = input.inputPtrArray[2][*i];

		point.col(colIdx) << x, y, z, 1;
		colIdx++;
	}

	// normalize data for DLT
	Normalize(point, H);

	// collect required carriers
	MatrixXd subsetCarrier(subset.size() * input.zeta, input.m);
	for (auto eleIdx = 0; eleIdx < subset.size(); eleIdx++) {
		x = point(0, eleIdx);
		y = point(1, eleIdx);
		z = point(2, eleIdx);
		subsetCarrier.block(input.zeta * eleIdx, 0, input.zeta, input.m) <<
			x, y, z, 1;
	}
	// compute structure by SVD		
	JacobiSVD<MatrixXd> subsetSvd(subsetCarrier, Eigen::ComputeFullV);

	// discard degenerate solutions
	if (subsetSvd.rank() < input.me * input.zeta)
		return false;

	// transform DLT solution back to original input space
	VectorXd DltTheta = subsetSvd.matrixV().col(input.m - 1);	

	DltTheta = H.transpose() * DltTheta;

	// normalize theta
	theta = DltTheta;
	if (input.alpha) {
		DltTheta(DltTheta.rows() - 1) = 0;
		double normVal = DltTheta.norm();
		theta /= normVal;
	}
	else {
		theta /= theta.norm();
	}
	return true;
}
