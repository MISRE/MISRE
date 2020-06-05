#include "Functions.h"
#include "Normalize.h"

#include <Eigen/Dense>
using Eigen::JacobiSVD;

void CarrierGen(const InputParam &input, const V_SIZE_T &remainIndex, MatrixXd &carrier)
{
	double x1, y1, x2, y2;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x1 = input.inputPtrArray[0][*i];
		y1 = input.inputPtrArray[1][*i];
		x2 = input.inputPtrArray[2][*i];
		y2 = input.inputPtrArray[3][*i];

		carrier.block(input.zeta * rowIdx, 0, input.zeta, input.m) <<
			0, 0, 0, -x1, -y1, -1, y2 * x1, y2 * y1, y2,
			x1, y1, 1, 0, 0, 0, -x2 * x1, -x2 * y1, -x2;

		rowIdx++;
	}
	return;
}

void JacobianGen(const InputParam &input, const V_SIZE_T &remainIndex, MatrixXd &jacobian)
{
	double x1, y1, x2, y2;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x1 = input.inputPtrArray[0][*i];
		y1 = input.inputPtrArray[1][*i];
		x2 = input.inputPtrArray[2][*i];
		y2 = input.inputPtrArray[3][*i];

		jacobian.block(input.l * input.zeta * rowIdx, 0, input.l * input.zeta, input.m) <<
			0, 0, 0, -1, 0, 0, y2, 0, 0,
			0, 0, 0, 0, -1, 0, 0, y2, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, x1, y1, 1,
			1, 0, 0, 0, 0, 0, -x2, 0, 0,
			0, 1, 0, 0, 0, 0, 0, -x2, 0,
			0, 0, 0, 0, 0, 0, -x1, -y1, -1,
			0, 0, 0, 0, 0, 0, 0, 0, 0;

		rowIdx++;
	}
	return;
}

bool DLTsolve(const InputParam &input, const V_SIZE_T &subset, VectorXd &theta)
{
	// create homogeneous coords
	MatrixXd point1(3, subset.size()), point2(3, subset.size());
	MatrixXd H1(3, 3), H2(3, 3);

	double x1, y1, x2, y2;
	size_t colIdx = 0;
	for (auto i = subset.begin(); i != subset.end(); ++i) {
		x1 = input.inputPtrArray[0][*i];
		y1 = input.inputPtrArray[1][*i];
		x2 = input.inputPtrArray[2][*i];
		y2 = input.inputPtrArray[3][*i];

		point1.col(colIdx) << x1, y1, 1;
		point2.col(colIdx) << x2, y2, 1;
		colIdx++;
	}

	// normalize data for DLT
	Normalize(point1, H1);
	Normalize(point2, H2);

	// collect required carriers
	MatrixXd subsetCarrier(subset.size() * input.zeta, input.m);
	for (auto eleIdx = 0; eleIdx < subset.size(); eleIdx++) {
		x1 = point1(0, eleIdx);
		y1 = point1(1, eleIdx);
		x2 = point2(0, eleIdx);
		y2 = point2(1, eleIdx);
		subsetCarrier.block(input.zeta * eleIdx, 0, input.zeta, input.m) <<
			0, 0, 0, -x1, -y1, -1, y2 * x1, y2 * y1, y2,
			x1, y1, 1, 0, 0, 0, -x2 * x1, -x2 * y1, -x2;
	}
	// compute structure by SVD		
	JacobiSVD<MatrixXd> subsetSvd(subsetCarrier, Eigen::ComputeFullV);

	// discard degenerate solutions
	if (subsetSvd.rank() < input.me * input.zeta)
		return false;

	// transform DLT solution back to original input space
	VectorXd DltTheta = subsetSvd.matrixV().col(input.m - 1);
	MatrixXd DltThetaMat = Eigen::Map<MatrixXd>(DltTheta.data(), 3, 3);

	DltThetaMat.transposeInPlace();
	DltThetaMat = H2.inverse() * DltThetaMat * H1;
	DltThetaMat.transposeInPlace();

	DltTheta = Eigen::Map<VectorXd>(DltThetaMat.data(), input.m);

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
