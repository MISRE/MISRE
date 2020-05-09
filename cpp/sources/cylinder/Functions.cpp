#include "Functions.h"
#include "Normalize.h"

#include <Eigen/Dense>
using Eigen::JacobiSVD;

#include <iostream>

void CarrierGen(InputParam &input, V_SIZE_T &remainIndex, MatrixXd &carrier)
{
	double x, y, z;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];
		z = input.inputPtrArray[2][*i];

		carrier.block(input.zeta * rowIdx, 0, input.zeta, input.m) <<
			x * x, x * y, x * z, x,
			y * y, y * z, y,
			z * z, z,
			1;

		rowIdx++;
	}
	return;
}

void JacobianGen(InputParam &input, V_SIZE_T &remainIndex, MatrixXd &jacobian)
{
	double x, y, z;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];
		z = input.inputPtrArray[2][*i];

		jacobian.block(input.l * input.zeta * rowIdx, 0, input.l * input.zeta, input.m) <<
			2 * x, y, z, 1, 0, 0, 0, 0, 0, 0,
			0, x, 0, 0, 2 * y, z, 1, 0, 0, 0,
			0, 0, x, 0, 0, y, 0, 2 * z, 1, 0;

		rowIdx++;
	}
	return;
}

bool DLTsolve(InputParam &input, V_SIZE_T &subset, VectorXd &theta)
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
			x * x, x * y, x * z, x,
			y * y, y * z, y,
			z * z, z,
			1;
	}
	// compute structure by SVD		
	JacobiSVD<MatrixXd> subsetSvd(subsetCarrier, Eigen::ComputeFullV);

	// discard degenerate solutions
	if (subsetSvd.rank() < input.me * input.zeta)
		return false;

	// transform DLT solution back to original input space
	VectorXd DltTheta = subsetSvd.matrixV().col(input.m - 1);

	// check if solution is a cylinder		
	MatrixXd DMat(3, 3);
	DMat << DltTheta(0), DltTheta(1) / 2, DltTheta(2) / 2,
		DltTheta(1) / 2, DltTheta(4), DltTheta(5) / 2,
		DltTheta(2) / 2, DltTheta(5) / 2, DltTheta(7);

	//JacobiSVD<MatrixXd> DMatSvd(DMat, Eigen::ComputeFullU | Eigen::ComputeFullV);
	JacobiSVD<MatrixXd> DMatSvd(DMat, Eigen::ComputeFullV);

	VectorXd sValues = DMatSvd.singularValues();
	if (sValues(2) < 0 || sValues(0) > 1.21 * sValues(1) || sValues(2) > 0.1 * sValues(0))
		return false;	

	MatrixXd DltThetaMat(4, 4);
	DltThetaMat << DltTheta(0), DltTheta(1) / 2, DltTheta(2) / 2, DltTheta(3) / 2,
		DltTheta(1) / 2, DltTheta(4), DltTheta(5) / 2, DltTheta(6) / 2,
		DltTheta(2) / 2, DltTheta(5) / 2, DltTheta(7), DltTheta(8) / 2,
		DltTheta(3) / 2, DltTheta(6) / 2, DltTheta(8) / 2, DltTheta(9);

	/*
	MatrixXd sinMat(3, 3);
	sinMat.setZero();
	sinMat(0, 0) = 0.5 * (sValues(0) + sValues(1));
	sinMat(1, 1) = 0.5 * (sValues(0) + sValues(1));
	sinMat(2, 2) = 0;
	DltThetaMat.block<3, 3>(0, 0) = DMatSvd.matrixU() * sinMat * (DMatSvd.matrixV().transpose());
	*/

	DltThetaMat = (H.transpose()) * DltThetaMat * H;

	DltTheta(0) = DltThetaMat(0, 0);
	DltTheta(1) = 2 * DltThetaMat(0, 1);
	DltTheta(2) = 2 * DltThetaMat(0, 2);
	DltTheta(3) = 2 * DltThetaMat(0, 3);
	DltTheta(4) = DltThetaMat(1, 1);
	DltTheta(5) = 2 * DltThetaMat(1, 2);
	DltTheta(6) = 2 * DltThetaMat(1, 3);
	DltTheta(7) = DltThetaMat(2, 2);
	DltTheta(8) = 2 * DltThetaMat(2, 3);
	DltTheta(9) = DltThetaMat(3, 3);

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