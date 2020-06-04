#include "Functions.h"
#include "Normalize.h"

#include <Eigen/Dense>
using Eigen::JacobiSVD;

void CarrierGen(const InputParam &input, const V_SIZE_T &remainIndex, MatrixXd &carrier)
{
	double x, y;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];

		carrier.block(input.zeta * rowIdx, 0, input.zeta, input.m) <<
			x * x, x * y, x, y * y, y, 1;

		rowIdx++;
	}
	return;
}

void JacobianGen(const InputParam &input, const V_SIZE_T &remainIndex, MatrixXd &jacobian)
{
	double x, y;
	size_t rowIdx = 0;
	for (auto i = remainIndex.begin(); i != remainIndex.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];

		jacobian.block(input.l * input.zeta * rowIdx, 0, input.l * input.zeta, input.m) <<
			2 * x, y, 1, 0, 0, 0,
			0, x, 0, 2 * y, 1, 0;

		rowIdx++;
	}
	return;
}

bool DLTsolve(const InputParam &input, const V_SIZE_T &subset, VectorXd &theta)
{
	// create homogeneous coords
	MatrixXd point(3, subset.size());
	MatrixXd H(3, 3);

	double x, y;
	size_t colIdx = 0;
	for (auto i = subset.begin(); i != subset.end(); ++i) {
		x = input.inputPtrArray[0][*i];
		y = input.inputPtrArray[1][*i];

		point.col(colIdx) << x, y, 1;
		colIdx++;
	}

	// normalize data for DLT
	Normalize(point, H);

	// collect required carriers
	MatrixXd subsetCarrier(subset.size() * input.zeta, input.m);
	for (auto eleIdx = 0; eleIdx < subset.size(); eleIdx++) {
		x = point(0, eleIdx);
		y = point(1, eleIdx);
		subsetCarrier.block(input.zeta * eleIdx, 0, input.zeta, input.m) <<
			x * x, x * y, x, y * y, y, 1;
	}
	// compute structure by SVD		
	JacobiSVD<MatrixXd> subsetSvd(subsetCarrier, Eigen::ComputeFullV);

	// discard degenerate solutions
	if (subsetSvd.rank() < input.me * input.zeta)
		return false;

	// transform DLT solution back to original input space
	VectorXd DltTheta = subsetSvd.matrixV().col(input.m - 1);

	// check if solution is an ellipse or other conic		
	if (DltTheta(1) * DltTheta(1) - 4 * DltTheta(0) * DltTheta(3) >= 0)
		return false;
	MatrixXd DltThetaMat(3, 3);
	DltThetaMat << DltTheta(0), DltTheta(1) / 2, DltTheta(2) / 2,
		DltTheta(1) / 2, DltTheta(3), DltTheta(4) / 2,
		DltTheta(2) / 2, DltTheta(4) / 2, DltTheta(5);
	DltThetaMat = (H.transpose()) * DltThetaMat * H;

	// special condition for ellipse: 
	// major axis cannot be too long compared with the minor axis
	// this avoids recognizing straight lines as ellipses
	Eigen::Matrix2d EigEllipse = DltThetaMat.block<2, 2>(0, 0);
	Eigen::SelfAdjointEigenSolver<Eigen::Matrix2d> eigensolver(EigEllipse);
	double eig1 = fabs(eigensolver.eigenvalues()(0));
	double eig2 = fabs(eigensolver.eigenvalues()(1));
	if (eig1 < eig2) {
		double tempEig = eig1;
		eig1 = eig2;
		eig2 = tempEig;
	}
	if (eig1 / eig2 > 100)
		return false;

	DltTheta(0) = DltThetaMat(0, 0);
	DltTheta(1) = 2 * DltThetaMat(0, 1);
	DltTheta(2) = 2 * DltThetaMat(0, 2);
	DltTheta(3) = DltThetaMat(1, 1);
	DltTheta(4) = 2 * DltThetaMat(1, 2);
	DltTheta(5) = DltThetaMat(2, 2);
	
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
