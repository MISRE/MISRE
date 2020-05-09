#include "MeanShiftKDE.h"

void MeanShiftKDE(InputParam &input, const MatrixXd &remainCarrier, const MatrixXd &remainJacobian,
	const double &scale, VectorXd &theta, double &mode)
{
	VectorXd thetaNoAlpha = theta;
	double Alpha = 0;
	if (input.alpha) {
		thetaNoAlpha(theta.rows() - 1) = 0;
		Alpha = theta(theta.rows() - 1);
	}

	// Compute numerators and denominators
	VectorXd CarTheta = remainCarrier * thetaNoAlpha;
	VectorXd tempJacTheta = remainJacobian * thetaNoAlpha;
	MatrixXd JacThetaZeta = Eigen::Map<MatrixXd>(tempJacTheta.data(), input.l, remainCarrier.rows());

	// Compute norms of denominators
	VectorXd JacTheta(remainCarrier.rows());
	for (auto i = 0; i < remainCarrier.rows(); i++) {
		JacTheta(i) = fabs(JacThetaZeta.col(i).norm()) * scale;
	}

	// mean shift
	double maxMode = -1;
	double tempAlpha = Alpha;
	VectorXd AlphaVector(remainCarrier.rows());

	for (auto i = 0; i < 10; i++) {
		double mode_i = 0;
		AlphaVector.setConstant(tempAlpha);
		VectorXd KDEDistance = (CarTheta + AlphaVector).cwiseQuotient(JacTheta);
		VectorXd UVal = KDEDistance.cwiseProduct(KDEDistance);

		size_t GSum = 0;
		double ZSum = 0;
		for (auto j = 0; j < UVal.rows(); j++) {
			if (UVal(j) > 1)
				continue;
			mode_i += 1 - UVal(j);
			GSum++;
			ZSum += CarTheta(j);
		}
		if (mode_i > maxMode) {
			maxMode = mode_i;
			Alpha = tempAlpha;
			tempAlpha = -ZSum / GSum;
		}
		else {
			break;
		}
		if (input.alpha == 0)
			break;
	}

	mode = maxMode;
	if (input.alpha)
		theta(theta.rows() - 1) = Alpha;
	return;
}